#! /usr/bin/env python

import pathlib
import subprocess
from typing import Iterator, Type, Optional


def node_list(slurm_conf: pathlib.Path) -> Iterator[str]:
    """
    Given a config file, gives all the nodes listed within
    """
    with slurm_conf.open() as conf:
        for line in conf:
            if line.startswith("NodeName="):
                nodelist = line.split()[0][9:]
                if "[" in nodelist:
                    # TODO use pyslurm.hostlist().create()/get_list()
                    pass
                yield from nodelist.split(",")


NODE_STATE_FLAGS = {
    "*": "not_responding",
    "~": "power_save",
    "#": "powering_up",
    "%": "powering_down",
    "$": "main_reservation",
    "@": "pending_reboot",
}


class SlurmNode:
    def __init__(self, name, state, features, state_flag):
        self.name = name
        self.state = state
        self.state_flag = state_flag
        self.features = features

    SINFO_FIELDS = [
        "nodelist",
        "statelong",
        "reason",
        "cpus",
        "socketcorethread",
        "memory",
        "features",
        "gres",
        "nodeaddr",
        "timestamp",
    ]

    name: str
    state: str
    state_flag: Optional[str]
    features: dict

    @classmethod
    def from_name(cls: Type["SlurmNode"], nodename: str) -> "SlurmNode":
        field_width = 40
        sinfo_format = ",".join(f"{f}:{field_width}" for f in cls.SINFO_FIELDS)
        out = subprocess.run(
            ["sinfo", "--nodes", nodename, "--Format", sinfo_format, "--noheader"],
            timeout=5,
        ).stdout.decode()
        fields = [
            out[start : start + field_width].strip()
            for start in range(0, len(out), field_width)
        ]
        data = {k: v for k, v in zip(cls.SINFO_FIELDS, fields)}

        if data["statelong"][-1] in NODE_STATE_FLAGS:
            state = data["statelong"][:-1]
            state_flag: Optional[str] = data["statelong"][-1]
        else:
            state = data["statelong"]
            state_flag = None

        features = parse_features(data["features"])

        return cls(name=nodename, state=state, state_flag=state_flag, features=features)


def parse_features(feature_string: str) -> dict:
    feature_dict = {}
    for pair in feature_string.split(","):
        k, v = pair.split("=")
        feature_dict[k] = v
    return feature_dict


def all_nodes(slurm_conf):
    return [SlurmNode.from_name(hostname) for hostname in node_list(slurm_conf)]

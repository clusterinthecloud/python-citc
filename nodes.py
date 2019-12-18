#! /usr/bin/env python

import pathlib
import subprocess
from typing import Iterator, Type


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


class Node:
    def __init__(self):
        pass

    sinfo_fields = [
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

    statelong: str

    @classmethod
    def from_name(cls: Type["Node"], nodename: str) -> "Node":
        field_width = 40
        sinfo_format = ",".join(f"{f}:{field_width}" for f in cls.sinfo_fields)
        out = subprocess.run(
            ["sinfo", "--nodes", nodename, "--Format", sinfo_format, "-h"]
        ).stdout.decode()
        fields = [
            out[start : start + field_width].strip()
            for start in range(0, len(out), field_width)
        ]
        data = {k: v for k, v in zip(cls.sinfo_fields, fields)}
        n = cls()
        n.statelong = data["statelong"]
        return n

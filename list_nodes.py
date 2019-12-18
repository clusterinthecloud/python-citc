#! /usr/bin/env python

import pathlib
from typing import Iterator


def slurm_node_list(slurm_conf: pathlib.Path) -> Iterator[str]:
    """
    Given a config file, gives all the nodes listed within
    """
    with slurm_conf.open() as conf:
        for line in conf:
            if line.startswith("NodeName="):
                nodelist = line.split()[0][9:]
                if '[' in nodelist:
                    # TODO use pyslurm.hostlist.create/get_list
                    pass
                yield from nodelist.split(",")

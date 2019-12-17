#! /usr/bin/env python


def slurm_node_list(slurm_conf):
    with open(slurm_conf) as conf:
        for line in conf:
            if line.startswith("NodeName="):
                yield line.split()[0][9:]

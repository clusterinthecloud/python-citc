#! /usr/bin/env python


def slurm_node_list(slurm_conf):
    with open(slurm_conf) as conf:
    """
    Given a config file, gives all the nodes listed within
    """
        for line in conf:
            if line.startswith("NodeName="):
                nodelist = line.split()[0][9:]
                if '[' in nodelist:
                    # TODO use pyslurm.hostlist.create/get_list
                    pass
                yield from nodelist.split(",")

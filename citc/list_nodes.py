from pathlib import Path
from typing import List, Optional

from tabulate import tabulate

from . import slurm, cloud, utils


def create_table(
    slurm_nodes: List[slurm.SlurmNode], cloud_nodes: List[cloud.CloudNode]
):
    table = []
    for slurm_node in slurm_nodes:
        matches = [node for node in cloud_nodes if node.name == slurm_node.name]
        if len(matches) == 1:
            cloud_state = matches[0].state  # type: Optional[cloud.NodeState]
        else:
            cloud_state = None
        table.append(
            [
                slurm_node.name,
                slurm_node.state,
                slurm.NODE_STATE_FLAGS.get(slurm_node.state_flag or "", ""),
                cloud_state,
            ]
        )

    headers = ["Name", "Slurm state", "Flag", "Cloud state"]

    return table, headers


def main():
    slurm_conf = Path("/mnt/shared/etc/slurm/slurm.conf")

    cloud_nodes = utils.get_cloud_nodes()
    slurm_nodes = slurm.all_nodes(slurm_conf)

    table_data, headers = create_table(slurm_nodes, cloud_nodes)
    table = tabulate(table_data, headers=headers)
    print(table)


if __name__ == "__main__":
    main()

import copy
import signal
import time
from typing import Dict, List, Callable, Iterator
from pathlib import Path

import yaml

from . import aws, slurm, cloud


def load_yaml(filename: str) -> dict:
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def get_nodespace(file="/etc/citc/startnode.yaml") -> Dict[str, str]:
    """
    Get the information about the space into which we were creating nodes
    This will be static for all nodes in this cluster
    """
    return load_yaml(file)


class SignalHandler:
    alive = True

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print(f"Received signal {signum}, shutting down...")
        self.alive = False


Changes = Iterator[Callable[[], None]]


def crosscheck(
    slurm_nodes: List[slurm.SlurmNode], cloud_nodes: List[cloud.CloudNode]
) -> Changes:
    """
    Compare the Slurm and cloud nodes and provide fixes

    Args:
        slurm_nodes: a list of nodes from Slurm
        cloud_nodes: a list of nodes from the cloud

    Returns:
        functions which, when called, fix each problem in turn
    """
    cloud_nodes = copy.copy(cloud_nodes)
    for slurm_node in slurm_nodes:
        matches = [node for node in cloud_nodes if node.name == slurm_node.name]
        if len(matches) == 0:
            if slurm_node.state_flag == "~":
                # Slurm thinks the node is turned off and there's no cloud node, all good.
                continue
            if slurm_node.state == "down":
                # The node is marked down but does not exist. Reset the state so that a new one can be created.
                # TODO Check REASON?
                print(f"Node {slurm_node.name} is DOWN with no cloud node, resuming")
                yield slurm_node.resume
            # Can't find the node in the cloud
            print(f"Node {slurm_node.name} has no matching cloud node")
            # TODO match up appropriate states
            # TODO yield things to fix
            pass
        elif len(matches) > 1:
            # Too many cloud node matches
            print(f"Node {slurm_node.name} matched multiple cloud nodes")
            # TODO yield things to fix
            pass
        else:
            # There is one slurm node and one cloud node
            # TODO check for unmatched state
            # TODO yield things to fix
            cloud_nodes.remove(matches[0])

    if cloud_nodes:
        # There are unmatched cloud nodes
        print(f"Cloud nodes {cloud_nodes} have no match in Slurm")
        # TODO yield things to fix
        pass


def main():
    print("Starting CitC watchdog")

    handler = SignalHandler()

    SLURM_CONF = Path("/mnt/shared/etc/slurm/slurm.conf")

    while handler.alive:
        nodespace = get_nodespace()

        csp = nodespace["csp"]
        if csp == "aws":
            ec2 = aws.ec2_client(nodespace)
            cloud_nodes = aws.all_nodes(ec2, nodespace)
        elif csp == "google":
            cloud_nodes = []
        elif csp == "oracle":
            cloud_nodes = []
        else:
            raise Exception(f"Cloud provider {csp} not found")

        slurm_nodes = slurm.all_nodes(SLURM_CONF)

        for task in crosscheck(slurm_nodes, cloud_nodes):
            task()

        time.sleep(60)

    print("Exiting CitC watchdog")


if __name__ == "__main__":
    main()

from typing import Dict, List

import yaml

from . import aws, oracle, cloud, google


def load_yaml(filename: str) -> dict:
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def get_nodespace(file="/etc/citc/startnode.yaml") -> Dict[str, str]:
    """
    Get the information about the space into which we were creating nodes
    This will be static for all nodes in this cluster
    """
    return load_yaml(file)


def get_cloud_nodes() -> List[cloud.CloudNode]:
    nodespace = get_nodespace()

    csp = nodespace["csp"]
    if csp == "aws":
        ec2 = aws.ec2_client(nodespace)
        cloud_nodes = aws.AwsNode.all(ec2, nodespace)
    elif csp == "google":
        client_config = google.client(nodespace)
        cloud_nodes = google.GoogleNode.all(client_config, nodespace)
    elif csp == "oracle":
        client = oracle.client_config(nodespace)
        cloud_nodes = oracle.OracleNode.all(client, nodespace)
    elif csp == "azure":
        cloud_nodes = []
    else:
        raise Exception(f"Cloud provider {csp} not found")

    return cloud_nodes

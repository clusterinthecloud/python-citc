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
        client = google.client(nodespace)
        cloud_nodes = google.GoogleNode.all(client, nodespace)
    elif csp == "oracle":
        client = oracle.client(nodespace)
        cloud_nodes = oracle.OracleNode.all(client, nodespace)
    elif csp == "azure":
        cloud_nodes = []
    else:
        raise Exception(f"Cloud provider {csp} not found")

    return cloud_nodes


def get_types_info():
    """
    Returns:
        list: a list of node info dictionaries
    """
    nodespace = get_nodespace()

    csp = nodespace["csp"]
    if csp == "aws":
        ec2 = aws.ec2_client(nodespace)
        return aws.get_types_info(ec2)
    elif csp == "google":
        return []
    elif csp == "oracle":
        return []
    elif csp == "azure":
        return []

    raise Exception(f"Cloud provider {csp} not found")

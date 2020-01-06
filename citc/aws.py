from typing import Type

import boto3  # type: ignore

from .cloud import CloudNode, NodeState


class NodeNotFound(Exception):
    pass


def ec2_client(nodespace: dict):
    return boto3.client("ec2", region_name=nodespace["region"])


class AwsNode(CloudNode):
    @classmethod
    def from_name(
        cls: Type["AwsNode"], nodename: str, client, nodespace: dict
    ) -> "AwsNode":
        instances = client.describe_instances(
            Filters=[
                {"Name": "tag:Name", "Values": [nodename]},
                {"Name": "tag:cluster", "Values": [nodespace["cluster_id"]]},
                {"Name": "tag:type", "Values": ["compute"]},
            ]
        )
        # TODO check for multiple returned matches
        if instances["Reservations"]:
            instance = instances["Reservations"][0]["Instances"][0]
        else:
            raise NodeNotFound(f"{nodename}")

        return cls.from_response(instance)

    @classmethod
    def from_response(cls: Type["AwsNode"], response) -> "AwsNode":
        state = response["State"]["Name"]
        name = next(pair["Value"] for pair in response["Tags"] if pair["Key"] == "Name")

        n = cls()

        n.name = name
        if state == "running":
            n.state = NodeState.RUNNING
        else:
            n.state = NodeState.OTHER

        return n


def all_nodes(client, nodespace: dict):
    result = client.describe_instances(
        Filters=[
            {"Name": "tag:cluster", "Values": [nodespace["cluster_id"]]},
            {"Name": "tag:type", "Values": ["compute"]},
        ]
    )
    if result["Reservations"]:
        instances = result["Reservations"][0]["Instances"]
    else:
        instances = []

    return [AwsNode.from_response(instance) for instance in instances]

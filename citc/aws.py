import configparser
from typing import Type

import boto3  # type: ignore

from .cloud import CloudNode, NodeState


class NodeNotFound(Exception):
    pass


def ec2_client(nodespace: dict):
    config = configparser.ConfigParser()
    config.read("/home/slurm/aws-credentials.csv")
    return boto3.client(
        "ec2",
        region_name=nodespace["region"],
        aws_access_key_id=config["default"]["aws_access_key_id"],
        aws_secret_access_key=config["default"]["aws_secret_access_key"],
    )


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
                # TODO filter on not-terminated state
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

        node_state_map = {
            "pending": NodeState.PENDING,
            "running": NodeState.RUNNING,
            "stopping": NodeState.STOPPING,
            "stopped": NodeState.STOPPED,
            "shutting-down": NodeState.TERMINATING,
            "terminated": NodeState.TERMINATED,
        }
        node_state = node_state_map.get(state, NodeState.OTHER)

        return cls(name=name, state=node_state)

    @classmethod
    def all(cls, client, nodespace: dict):
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

        return [cls.from_response(instance) for instance in instances]

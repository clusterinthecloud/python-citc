import configparser
import math
from typing import Type, Dict

import boto3
from mypy_boto3_ec2 import EC2Client

from .cloud import CloudNode, NodeState, NodeTypeInfo


class NodeNotFound(Exception):
    pass


def ec2_client(nodespace: dict) -> EC2Client:
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
                {
                    "Name": "instance-state-name",
                    "Values": [
                        "pending",
                        "running",
                        "shutting-down",
                        "stopping",
                    ],  # not "stopped" or terminated
                },
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

        ip = response["PrivateIpAddress"]

        return cls(name=name, state=node_state, ip=ip, id=response["InstanceId"])

    @classmethod
    def all(cls, client: EC2Client, nodespace: dict):
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


def get_types_info(client: EC2Client) -> Dict[str, NodeTypeInfo]:
    instances = {
        i["InstanceType"]: i
        for page in client.get_paginator("describe_instance_types").paginate()
        for i in page["InstanceTypes"]
    }

    def is_cluster_group(d):
        if "PlacementGroupInfo" not in d:
            return False
        return "cluster" in d["PlacementGroupInfo"]["SupportedStrategies"]

    return {
        s: {
            "memory": d["MemoryInfo"]["SizeInMiB"]
            - int(math.pow(d["MemoryInfo"]["SizeInMiB"], 0.7) * 0.9 + 500),
            "cores_per_socket": d["VCpuInfo"].get(
                "DefaultCores", d["VCpuInfo"]["DefaultVCpus"]
            ),
            "threads_per_core": d["VCpuInfo"].get("DefaultThreadsPerCore", 1),
            "arch": d["ProcessorInfo"]["SupportedArchitectures"][0],
            "cluster_group": is_cluster_group(d),
        }
        for s, d in instances.items()
    }

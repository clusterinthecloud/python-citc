import boto3  # type: ignore
import pytest  # type: ignore
from moto import mock_ec2  # type: ignore

from citc.aws import AwsNode
from citc.cloud import NodeState


@pytest.fixture
def nodespace():
    return {
        "cluster_id": "cluster1",
    }


@pytest.fixture(scope="function")
def ec2():
    with mock_ec2():
        yield boto3.client("ec2", region_name="eu-west-1")


def launch_node(nodename: str, client, nodespace):
    tag_specifications = [
        {
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": nodename},
                {"Key": "cluster", "Value": nodespace["cluster_id"]},
                {"Key": "type", "Value": "compute"},
            ],
        },
    ]

    client.run_instances(
        ImageId="ami-760aaa0f",
        TagSpecifications=tag_specifications,
        MinCount=1,
        MaxCount=1,
    )


def test_awsnode(ec2, nodespace):
    launch_node("foo", ec2, nodespace)
    node = AwsNode.from_name("foo", ec2, nodespace)
    assert node.name == "foo"
    assert node.state == NodeState.RUNNING


def test_all_nodes_empty(ec2, nodespace):
    assert AwsNode.all(ec2, nodespace) == []


def test_all_nodes(ec2, nodespace):
    launch_node("foo", ec2, nodespace)
    nodes = AwsNode.all(ec2, nodespace)
    assert len(nodes) == 1

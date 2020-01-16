import oci  # type: ignore
import pytest  # type: ignore
from mebula import mock_oracle

from citc.oracle import OracleNode
from citc.cloud import NodeState


@pytest.fixture(scope="function")
def client():
    with mock_oracle():
        return oci.core.ComputeClient(config={})


@pytest.fixture
def nodespace():
    return {
        "ad_root": "HERE-AD-",
        "compartment_id": "ocid1.compartment.oc1..aaaaa",
        "vcn_id": "ocid1.vcn.oc1..aaaaa",
        "region": "uk-london-1",
    }


def launch_node(nodename: str, client, nodespace):
    instance_details = oci.core.models.LaunchInstanceDetails(
        compartment_id=nodespace["compartment_id"],
        display_name=nodename,
        freeform_tags={"type": "compute"},
    )
    client.launch_instance(instance_details)


def test_oraclenode(client, nodespace):
    launch_node("foo", client, nodespace)
    node = OracleNode.from_name("foo", client, nodespace)
    assert node.name == "foo"
    assert node.state == NodeState.RUNNING


def test_all_nodes_empty(client, nodespace):
    assert OracleNode.all(client, nodespace) == []


def test_all_nodes(client, nodespace):
    launch_node("foo", client, nodespace)
    nodes = OracleNode.all(client, nodespace)
    assert len(nodes) == 1

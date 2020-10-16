import oci  # type: ignore
import pytest  # type: ignore
from mebula import mock_oracle

from citc.oracle import OracleNode
from citc.cloud import NodeState


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
    client = oci.core.ComputeClient({})
    client.launch_instance(instance_details)


def test_oraclenode(nodespace):
    with mock_oracle():
        launch_node("foo", {}, nodespace)
        node = OracleNode.from_name("foo", {}, nodespace)
        assert node.name == "foo"
        assert node.state == NodeState.RUNNING


def test_all_nodes_empty(nodespace):
    with mock_oracle():
        assert OracleNode.all({}, nodespace) == []


def test_all_nodes(nodespace):
    with mock_oracle():
        launch_node("foo", {}, nodespace)
        nodes = OracleNode.all({}, nodespace)
        assert len(nodes) == 1

from tabulate import tabulate

from citc.aws import AwsNode
from citc.list_nodes import create_table
from citc.cloud import NodeState
from citc.slurm import SlurmNode


def test_create_table():
    slurm_nodes = [
        SlurmNode(name="foo-1", state="idle", state_flag=None, features={}, reason=""),
        SlurmNode(name="foo-2", state="idle", state_flag="~", features={}, reason=""),
    ]
    cloud_nodes = [
        AwsNode(name="foo-1", state=NodeState.RUNNING, ip="10.0.0.25", id="i-foobar")
    ]
    table, headers = create_table(slurm_nodes, cloud_nodes)
    assert table == [
        ["foo-1", "idle", "", NodeState.RUNNING],
        ["foo-2", "idle", "power save", None],
    ]
    assert headers == ["Name", "Slurm state", "Flag", "Cloud state"]


def test_print_table():
    slurm_nodes = [
        SlurmNode(name="foo-1", state="idle", state_flag=None, features={}, reason="")
    ]
    cloud_nodes = [
        AwsNode(name="foo-1", state=NodeState.RUNNING, ip="10.0.0.25", id="i-foobar")
    ]
    table_data = create_table(slurm_nodes, cloud_nodes)
    print(tabulate(table_data))

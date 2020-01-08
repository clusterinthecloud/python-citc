from tabulate import tabulate

from citc.aws import AwsNode
from citc.list_nodes import create_table
from citc.cloud import NodeState
from citc.slurm import SlurmNode


def test_create_table():
    slurm_nodes = [
        SlurmNode(name="foo-1", state="idle", state_flag=None, features={}),
        SlurmNode(name="foo-2", state="idle", state_flag="~", features={}),
    ]
    cloud_nodes = [AwsNode(name="foo-1", state=NodeState.RUNNING)]
    table = create_table(slurm_nodes, cloud_nodes)
    assert table == [
        ["foo-1", "idle", "", NodeState.RUNNING],
        ["foo-2", "idle", "power save", None],
    ]


def test_print_table():
    slurm_nodes = [SlurmNode(name="foo-1", state="idle", state_flag=None, features={})]
    cloud_nodes = [AwsNode(name="foo-1", state=NodeState.RUNNING)]
    table_data = create_table(slurm_nodes, cloud_nodes)
    print(tabulate(table_data))

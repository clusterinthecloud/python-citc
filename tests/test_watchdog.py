from citc.aws import AwsNode
from citc.cloud import NodeState
from citc.slurm import SlurmNode
from citc.watchdog import crosscheck


def test_crosscheck():
    slurm_nodes = [SlurmNode(name="foo-1", state="idle", state_flag=None, features={})]
    cloud_nodes = [AwsNode(name="foo-1", state=NodeState.RUNNING)]

    crosscheck(slurm_nodes, cloud_nodes)


def test_missing_node_down():
    slurm_nodes = [SlurmNode(name="foo-1", state="down", state_flag=None, features={})]
    cloud_nodes = []

    res = crosscheck(slurm_nodes, cloud_nodes)
    assert slurm_nodes[0].resume in res


def test_idle_node_off():
    slurm_nodes = [SlurmNode(name="foo-1", state="idle", state_flag="~", features={})]
    cloud_nodes = []

    res = crosscheck(slurm_nodes, cloud_nodes)
    res = list(res)
    assert not res

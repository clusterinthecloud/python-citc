from citc.aws import AwsNode
from citc.cloud import NodeState
from citc.slurm import SlurmNode
from citc.watchdog import crosscheck


def test_crosscheck():
    slurm_nodes = [SlurmNode(name="foo-1", state="idle", state_flag=None, features={})]
    cloud_nodes = [AwsNode(name="foo-1", state=NodeState.RUNNING)]

    crosscheck(slurm_nodes, cloud_nodes)
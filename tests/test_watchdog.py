from citc.aws import AwsNode
from citc.cloud import NodeState
from citc.slurm import SlurmNode
from citc.watchdog import crosscheck


def test_crosscheck():
    slurm_nodes = [SlurmNode(name="foo-1", state="idle", state_flag=None, features={})]
    cloud_nodes = [AwsNode(name="foo-1", state=NodeState.RUNNING)]

    crosscheck(slurm_nodes, cloud_nodes)


def test_missing_node_down(mocker):
    slurm_nodes = [SlurmNode(name="foo-1", state="down", state_flag=None, features={})]
    cloud_nodes = []

    run = mocker.patch("subprocess.run")
    crosscheck(slurm_nodes, cloud_nodes)
    run.assert_called_once()


def test_idle_node_off(mocker):
    slurm_nodes = [SlurmNode(name="foo-1", state="idle", state_flag="~", features={})]
    cloud_nodes = []

    crosscheck(slurm_nodes, cloud_nodes)

    # TODO assert that nothing hapenns

import subprocess
import textwrap

import pytest  # type: ignore

from citc.slurm import node_list, SlurmNode, parse_features


@pytest.fixture(scope="function")
def slurm_conf(tmp_path):
    p = tmp_path / "slurm.conf"
    p.write_text(
        textwrap.dedent(
            """
            # STARTNODES
            NodeName=t3-micro-0001 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            NodeName=t3-micro-0002 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            NodeName=t3-micro-0003 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            NodeName=t3-micro-0004 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            NodeName=t3-micro-0005 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            NodeName=t3-micro-0006 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            NodeName=t3-micro-0007 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            NodeName=t3-micro-0008 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            NodeName=t3-micro-0009 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            NodeName=t3-micro-0010 State=CLOUD SocketsPerBoard=1 CoresPerSocket=1 ThreadsPerCore=2 RealMemory=90 Gres=""
            # ENDNODES
            """
        )
    )
    return p


def test_slurm_node_list(slurm_conf):
    r = list(node_list(slurm_conf))
    assert len(r) == 10
    assert r[0] == "t3-micro-0001"
    assert r[-1] == "t3-micro-0010"


def test_create_node(mocker):
    node_data = {
        "nodelist": "vm-standard-e2-2-ad3-0001",
        "statelong": "idle~",
        "reason": "none",
        "cpus": "4",
        "socketcorethread": "1:2:2",
        "memory": "13500",
        "features": "shape=VM.Standard.E2.2,ad=3",
        "gres": "(null)",
        "nodeaddr": "vm-standard-e2-2-ad3-0001",
        "timestamp": "Unknown",
    }
    sinfo_output = "".join(f"{node_data[f]:40}" for f in SlurmNode.SINFO_FIELDS)
    mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args="", returncode=0, stdout=sinfo_output.encode()
        ),
    )
    n = SlurmNode.from_name(node_data["nodelist"])

    assert n.state == "idle"


def test_parse_features(mocker):
    r = parse_features("shape=VM.Standard.E2.2,ad=3")
    expected = {
        "shape": "VM.Standard.E2.2",
        "ad": "3",
    }

    assert r == expected

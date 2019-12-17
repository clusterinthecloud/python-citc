import textwrap

from list_nodes import slurm_node_list


def test_slurm_node_list(tmp_path):
    p = tmp_path / "slurm.conf"
    p.write_text(textwrap.dedent("""
    # STARTNODES
    NodeName=t3-micro-0001   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    NodeName=t3-micro-0002   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    NodeName=t3-micro-0003   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    NodeName=t3-micro-0004   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    NodeName=t3-micro-0005   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    NodeName=t3-micro-0006   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    NodeName=t3-micro-0007   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    NodeName=t3-micro-0008   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    NodeName=t3-micro-0009   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    NodeName=t3-micro-0010   State=CLOUD   SocketsPerBoard=1  CoresPerSocket=1   ThreadsPerCore=2 RealMemory=900 Gres=""
    # ENDNODES
    """))
    r = list(slurm_node_list(p))
    assert len(r) == 10
    assert r[0] == "t3-micro-0001"
    assert r[-1] == "t3-micro-0010"

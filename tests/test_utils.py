from citc.utils import get_cloud_nodes

import pytest


def test_get_cloud_nodes_error(fs):
    fs.create_file("/etc/citc/startnode.yaml", contents="---\ncsp: blahblah")

    with pytest.raises(Exception):
        get_cloud_nodes()

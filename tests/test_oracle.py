import collections.abc
import json

import oci  # type: ignore
import pytest  # type: ignore
import requests_mock  # type: ignore
from typing import Any

from citc.oracle import OracleNode
from citc.cloud import NodeState


@pytest.fixture
def oci_config(tmp_path):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    config = {
        "user": "ocid1.user.oc1..aaaaa",
        "key_file": "/tmp/foo",
        "fingerprint": "6e:b9:17:06:13:37:b8:5e:b2:72:48:53:9e:3e:6b:01",
        "tenancy": "ocid1.tenancy.oc1..aaaaa",
        "region": "here",
    }

    key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    kf = tmp_path / config["key_file"]
    kf.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    return config


@pytest.fixture
def client(oci_config):
    return oci.core.ComputeClient(oci_config)


@pytest.fixture
def nodespace():
    return {
        "ad_root": "HERE-AD-",
        "compartment_id": "ocid1.compartment.oc1..aaaaa",
        "vcn_id": "ocid1.vcn.oc1..aaaaa",
        "region": "uk-london-1",
    }


def serialise(data: Any):
    """
    Turn any OCI model into its JSON equivalent
    """
    if isinstance(data, collections.abc.Iterable):
        return [serialise(d) for d in data]

    return {
        data.attribute_map[attr]: getattr(data, attr, None)
        for attr in data.swagger_types
    }


@pytest.fixture
def requests_mocker(mocker):
    adapter = requests_mock.Adapter()
    mocker.patch("oci._vendor.requests.Session.get_adapter", return_value=adapter)
    return adapter


def test_oraclenode(client, nodespace, requests_mocker):
    requests_mocker.register_uri(
        "GET",
        "/20160918/instances/?compartmentId=ocid1.compartment.oc1..aaaaa&displayName=foo",
        text=json.dumps(
            serialise(
                [
                    oci.core.models.Instance(
                        id="ocid0..instance.foo",
                        lifecycle_state="RUNNING",
                        display_name="foo",
                    ),
                ]
            )
        ),
    )

    node = OracleNode.from_name("foo", client, nodespace)
    assert node.name == "foo"
    assert node.state == NodeState.RUNNING


def test_all_nodes_empty(client, nodespace, requests_mocker):
    requests_mocker.register_uri(
        "GET",
        "/20160918/instances/?compartmentId=ocid1.compartment.oc1..aaaaa",
        text=json.dumps(serialise([])),
    )

    assert OracleNode.all(client, nodespace) == []


def test_all_nodes(client, nodespace, requests_mocker):
    requests_mocker.register_uri(
        "GET",
        "/20160918/instances/?compartmentId=ocid1.compartment.oc1..aaaaa",
        text=json.dumps(
            serialise(
                [
                    oci.core.models.Instance(
                        id="ocid0..instance.foo",
                        lifecycle_state="RUNNING",
                        display_name="foo",
                        freeform_tags={"type": "compute"},
                    ),
                ]
            )
        ),
    )

    nodes = OracleNode.all(client, nodespace)
    assert len(nodes) == 1

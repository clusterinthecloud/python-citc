import httplib2  # type: ignore
import googleapiclient.discovery  # type: ignore
import json
import pytest  # type: ignore
from urllib.parse import urlparse
from google.auth.credentials import Credentials  # type: ignore

from citc.google import GoogleNode
from citc.cloud import NodeState


@pytest.fixture
def nodespace():
    return {
        "compartment_id": "myproj-123456",
        "zone": "europe-west4-a",
    }


@pytest.fixture(scope="function")
def client():
    class MockCredentials(Credentials):
        def refresh(self, request):
            pass

        def before_request(self, request, method, url, headers):
            pass

    compute = googleapiclient.discovery.build(
        "compute", "v1", credentials=MockCredentials(), cache_discovery=False
    )
    return compute


def test_googlenode(client, nodespace, mocker):
    def request_mock(
        http, num_retries, req_type, sleep, rand, uri, method, *args, **kwargs
    ):
        url = urlparse(uri)
        project = nodespace["compartment_id"]
        zone = nodespace["zone"]
        if (
            url.path == f"/compute/v1/projects/{project}/zones/{zone}/instances"
            and url.query == "filter=%28name%3Dfoo%29&alt=json"
            and method == "GET"
        ):
            return (
                httplib2.Response({"status": 200, "reason": "OK"}),
                json.dumps({"items": [{"name": "foo", "status": "RUNNING"}]}),
            )

    mocker.patch("googleapiclient.http._retry_request", side_effect=request_mock)

    node = GoogleNode.from_name("foo", client, nodespace)
    assert node.name == "foo"
    assert node.state == NodeState.RUNNING


def test_all_nodes_empty(client, nodespace, mocker):
    def request_mock(
        http, num_retries, req_type, sleep, rand, uri, method, *args, **kwargs
    ):
        url = urlparse(uri)
        project = nodespace["compartment_id"]
        zone = nodespace["zone"]
        if (
            url.path == f"/compute/v1/projects/{project}/zones/{zone}/instances"
            and url.query == "alt=json"
            and method == "GET"
        ):
            return (
                httplib2.Response({"status": 200, "reason": "OK"}),
                json.dumps({}),
            )

    mocker.patch("googleapiclient.http._retry_request", side_effect=request_mock)

    assert GoogleNode.all(client, nodespace) == []

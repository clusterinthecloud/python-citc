import collections.abc
import contextlib
import functools
import mock
from collections import defaultdict
from typing import Any, Callable, Dict, List

import oci  # type: ignore


class DummyAsync:
    def __init__(self, function: Callable[[], Any]):
        self.function = function

    def execute(self) -> Any:
        return self.function()


class GoogleComputeClient:
    """
    A mocked version of googleapiclient.discovery.build("compute", "v1", ...)
    """

    def __init__(self, *args, **kwargs):
        self._instances = []

    def instances(self):
        return GoogleComputeInstances(self)


class GoogleComputeInstances:
    def __init__(self, client: GoogleComputeClient):
        self.client = client

    def list(self, project: str, zone: str, filter=""):
        def wrap_response():
            instances = list(self._filter_instances(self.client._instances, filter))
            if instances:
                return {"items": instances}
            else:
                return {}

        return DummyAsync(wrap_response)

    @staticmethod
    def _filter_instances(instances, filter=""):
        # TODO Full query syntax from https://cloud.google.com/sdk/gcloud/reference/topic/filters
        split_filter = filter.split("=")
        if len(split_filter) > 2:
            raise Exception

        if split_filter == [""]:
            yield from instances
            return

        for i in instances:
            if i[split_filter[0]] == split_filter[1]:
                yield i

    def insert(self, project: str, zone: str, body):
        inserter = functools.partial(
            self.client._instances.append, GoogleComputeNode(body)
        )
        return DummyAsync(inserter)


class GoogleComputeNode(collections.abc.Mapping):
    def __init__(self, body):
        self.data = {}
        self.data["name"] = body["name"]
        self.data["tags"] = body["tags"]
        self.data["status"] = "RUNNING"

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


@contextlib.contextmanager
def mock_google():
    def build_google_client(service_name, version, **kwargs):
        if service_name == "compute":
            if version != "v1":
                raise Exception
            return GoogleComputeClient()
        else:
            raise Exception

    with mock.patch("googleapiclient.discovery.build", new=build_google_client):
        yield


class OracleComputeClient:
    """
    A mocked version of oci.core.ComputeClient
    """

    def __init__(self, config: dict, **kwargs):
        self._instances: Dict[str, List[oci.core.models.Instance]] = defaultdict(list)

    def list_instances(self, compartment_id: str, **kwargs) -> oci.response.Response:
        return oci.response.Response(200, None, self._instances[compartment_id], None)

    def launch_instance(
        self, launch_instance_details: oci.core.models.LaunchInstanceDetails, **kwargs
    ):
        if "display_name" in kwargs or "lifecycle_state" in kwargs:
            raise NotImplementedError
        instance = oci.core.models.Instance(
            availability_domain=launch_instance_details.availability_domain,
            display_name=launch_instance_details.display_name,
            freeform_tags=launch_instance_details.freeform_tags,
            lifecycle_state="RUNNING",
        )
        self._instances[launch_instance_details.compartment_id].append(instance)


@contextlib.contextmanager
def mock_oracle():
    with mock.patch("oci.core.ComputeClient", new=OracleComputeClient):
        yield

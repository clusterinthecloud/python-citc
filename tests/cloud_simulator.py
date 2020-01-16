import collections.abc
import contextlib
import functools
import json
import mock
import urllib.request
from collections import defaultdict, namedtuple
from typing import Any, Dict, List
from urllib.parse import urlparse, parse_qs

import googleapiclient.discovery  # type: ignore
import oci  # type: ignore
from googleapiclient.http import HttpMock  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore


class GoogleState:
    def __init__(self):
        self.instances = []


@functools.lru_cache(maxsize=128)
def google_api_client(serviceName: str, version: str, *args, **kwargs):
    url = f"https://www.googleapis.com/discovery/v1/apis/{serviceName}/{version}/rest"
    data = urllib.request.urlopen(url).read().decode()
    return googleapiclient.discovery.build_from_document(data, http=HttpMock())


class GoogleComputeInstances:
    """
    A reimplementation of the Google cloud server-side for the ``instances`` resource
    """

    def __init__(self, state: GoogleState):
        self.state = state

    def list(self, project: str, zone: str, filter=None, alt="", body=None):
        if filter is not None:
            instances = list(self._filter_instances(self.state.instances, filter[0]))
        else:
            instances = self.state.instances
        return {"items": instances} if instances else {}

    def get(self, project: str, zone: str, instance: str, alt="", body=None):
        instances = [i for i in self.state.instances if i["name"] == instance]
        if instances:
            return instances[0]
        else:
            Response = namedtuple("Response", ["status", "reason"])
            reason = f"Instance {instance} not found in {project}/{zone}"
            resp = Response(status="404", reason=reason)
            raise HttpError(resp, b"{}", uri="<NotImplemented>")

    @staticmethod
    def _filter_instances(instances, filter=""):
        # TODO Full query syntax from https://cloud.google.com/sdk/gcloud/reference/topic/filters
        # Perhaps use lark
        split_filter = filter.split("=")
        if len(split_filter) > 2:
            raise NotImplementedError

        if split_filter == [""]:
            yield from instances
            return

        for i in instances:
            if i[split_filter[0]] == split_filter[1]:
                yield i

    def insert(self, project: str, zone: str, body, alt=""):
        print("inserting", body)
        return self.state.instances.append(GoogleComputeInstance(body))


class GoogleComputeInstance(collections.abc.Mapping):
    """
    A dictionary version of the Instance resource
    """

    def __init__(self, body):
        # Should match google_api_client("compute", "v1").instances()._schema.get("Instance")
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


def extract_path_parameters(path: str, template: str) -> Dict[str, str]:
    parameters = {}
    for p, t in zip(path.split("/"), template.split("/")):
        if t.startswith("{") and t.endswith("}"):
            var_name = t[1:-1]
            parameters[var_name] = p
    return parameters


def google_execute(
    request: googleapiclient.http.HttpRequest, state: GoogleState
) -> dict:
    api, resource, method = request.methodId.split(".")
    url = urlparse(request.uri)
    path = url.path
    query = parse_qs(url.query)
    body = json.loads(request.body) if request.body else {}

    api_version = path.split("/")[2]  # Hacky, I know
    r = getattr(google_api_client(api, api_version), resource)()
    base_path = urlparse(r._baseUrl).path
    method_schema = r._resourceDesc["methods"][method]
    method_path = method_schema["path"]
    path_template = base_path + method_path

    path_parameters = extract_path_parameters(path, path_template)

    all_parameters: Dict[str, Any] = {**path_parameters, **query, **{"body": body}}

    collection_map = {"compute": {"instances": GoogleComputeInstances}}

    try:
        resource_class = collection_map[api][resource]
    except KeyError:
        raise NotImplementedError(
            f"Resource collection {api}.{resource} is not implemented"
        )

    resource_object = resource_class(state)

    try:
        resource_method = getattr(resource_object, method)
    except AttributeError:
        raise NotImplementedError(
            f"Method {api}.{resource}.{method} is not implemented"
        )
    return resource_method(**all_parameters)


@contextlib.contextmanager
def mock_google():
    state = GoogleState()
    with mock.patch("googleapiclient.discovery.build", new=google_api_client):
        with mock.patch.object(
            googleapiclient.http.HttpRequest,
            "execute",
            new=functools.partialmethod(google_execute, state),
        ):
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

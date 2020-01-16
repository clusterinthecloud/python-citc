import googleapiclient.discovery  # type: ignore
import oci  # type: ignore

from .cloud_simulator import mock_google, mock_oracle, extract_path_parameters


def test_google_empty():
    with mock_google():
        compute = googleapiclient.discovery.build("compute", "v1")
        assert compute.instances().list(project="foo", zone="bar").execute() == {}


def test_google_one_round_trip():
    with mock_google():
        compute = googleapiclient.discovery.build("compute", "v1")
        compute.instances().insert(
            project="foo", zone="bar", body={"name": "foo", "tags": {}}
        ).execute()
        instances = compute.instances().list(project="foo", zone="bar").execute()
        assert "items" in instances
        assert len(instances["items"]) == 1
        assert instances["items"][0]["name"] == "foo"


def test_oracle_empty():
    with mock_oracle():
        compute = oci.core.ComputeClient(config={})
        assert compute.list_instances("foo").data == []


def test_oracle_one_round_trip():
    with mock_oracle():
        compute = oci.core.ComputeClient(config={})
        instance_details = oci.core.models.LaunchInstanceDetails(
            compartment_id="compartment_id", display_name="foo",
        )
        compute.launch_instance(instance_details)

        instances = compute.list_instances("compartment_id").data
        assert len(instances) == 1
        assert instances[0].display_name == "foo"


def test_extract_path_parameters():
    path = "/compute/v1/projects/prfoo/zones/zbar/instances"
    template = "/compute/v1/projects/{project}/zones/{zone}/instances"

    expected = {"project": "prfoo", "zone": "zbar"}

    assert extract_path_parameters(path, template) == expected

import math
import os
from pathlib import Path
from typing import Type

from google.oauth2 import service_account  # type: ignore
import googleapiclient.discovery  # type: ignore

from .cloud import CloudNode, NodeState


class NodeNotFound(Exception):
    pass


def client(nodespace: dict):
    service_account_file = Path(
        os.environ.get("SA_LOCATION", "/home/slurm/mgmt-sa-credentials.json")
    )
    if service_account_file.exists():
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file
        )
    else:
        credentials = None

    compute = googleapiclient.discovery.build(
        "compute", "v1", credentials=credentials, cache_discovery=False
    )

    return compute


class GoogleNode(CloudNode):
    @classmethod
    def from_name(
        cls: Type["GoogleNode"], nodename: str, client, nodespace: dict
    ) -> "GoogleNode":
        filter_clause = (
            f"name={nodename} AND "
            "status=(PROVISIONING, STAGING, RUNNING, STOPPING, SUSPENDING, SUSPENDED, REPAIRING)"
        )
        result = (
            client.instances()
            .list(
                project=nodespace["compartment_id"],
                zone=nodespace["zone"],
                filter=filter_clause,
            )
            .execute()
        )
        # TODO check for multiple returned matches
        if "items" in result:
            instance = result["items"][0]
        else:
            raise NodeNotFound(f"{nodename}")

        return cls.from_response(instance)

    @classmethod
    def from_response(cls: Type["GoogleNode"], response) -> "GoogleNode":
        state = response["status"]
        name = response["name"]

        node_state_map = {
            "PROVISIONING": NodeState.PENDING,
            "STAGING": NodeState.PENDING,
            "RUNNING": NodeState.RUNNING,
            "STOPPING": NodeState.STOPPING,
            "STOPPED": NodeState.STOPPED,
            "TERMINATED": NodeState.STOPPED,
            "SUSPENDING": NodeState.OTHER,
            "SUSPENDED": NodeState.OTHER,
        }
        node_state = node_state_map.get(state, NodeState.OTHER)

        ip = response["networkInterfaces"][0]["networkIP"]

        return cls(name=name, state=node_state, ip=ip, id=response["id"])

    @classmethod
    def all(cls, client, nodespace: dict):
        result = (
            client.instances()
            .list(project=nodespace["compartment_id"], zone=nodespace["zone"])
            .execute()
        )
        # TODO filter on not-terminated state
        # TODO check for multiple returned matches
        if "items" in result:
            instances = result["items"]
        else:
            instances = []

        return [cls.from_response(instance) for instance in instances]


def get_types_info(client, nodespace):
    machine_types = (
        client.machineTypes()
        .list(project=nodespace["compartment_id"], zone=nodespace["zone"])
        .execute()["items"]
    )
    return {
        mt["name"]: {
            "memory": int(math.pow(mt["memoryMb"], 0.7) * 0.9 + 500),
            "cores_per_socket": mt["guestCpus"],
            "threads_per_core": "1",
            # only C2 currently support compact placement groups
            "cluster_group": mt["name"].startswith("c2-"),
        }
        for mt in machine_types
    }

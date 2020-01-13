from typing import Type

import oci  # type: ignore

from .cloud import CloudNode, NodeState


class NodeNotFound(Exception):
    pass


def client(nodespace: dict):
    return oci.core.ComputeClient(oci.config.from_file())


class OracleNode(CloudNode):
    @classmethod
    def from_name(
        cls: Type["OracleNode"], nodename: str, client, nodespace: dict
    ) -> "OracleNode":
        matches = client.list_instances(
            compartment_id=nodespace["compartment_id"], display_name=nodename
        ).data
        still_exist = [i for i in matches if i.lifecycle_state != "TERMINATED"]

        if not still_exist:
            raise NodeNotFound(f"{nodename}")
        if len(still_exist) > 1:
            print("ERROR!")  # TODO

        return cls.from_response(still_exist[0])

    @classmethod
    def from_response(
        cls: Type["OracleNode"], response: oci.core.models.Instance
    ) -> "OracleNode":
        state = response.lifecycle_state
        name = response.display_name

        node_state_map = {
            "MOVING": NodeState.PENDING,
            "PROVISIONING": NodeState.PENDING,
            "CREATING_IMAGE": NodeState.PENDING,
            "STARTING": NodeState.PENDING,
            "RUNNING": NodeState.RUNNING,
            "STOPPING": NodeState.STOPPING,
            "STOPPED": NodeState.STOPPED,
            "TERMINATING": NodeState.TERMINATING,
            "TERMINATED": NodeState.TERMINATED,
        }
        node_state = node_state_map.get(state, NodeState.OTHER)

        return cls(name=name, state=node_state)

    @classmethod
    def all(cls, client, nodespace: dict):
        instances = client.list_instances(
            compartment_id=nodespace["compartment_id"]
        ).data
        nodes = [
            instance
            for instance in instances
            if instance.freeform_tags.get("type") == "compute"
        ]

        return [cls.from_response(instance) for instance in nodes]

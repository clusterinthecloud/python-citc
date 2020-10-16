from typing import Type

import oci  # type: ignore

from .cloud import CloudNode, NodeState


class NodeNotFound(Exception):
    pass


def get_config():
    return oci.config.from_file()


class OracleNode(CloudNode):
    @classmethod
    def from_name(
        cls: Type["OracleNode"], nodename: str, config: dict, nodespace: dict
    ) -> "OracleNode":
        client = oci.core.ComputeClient(config)
        matches = client.list_instances(
            compartment_id=nodespace["compartment_id"], display_name=nodename
        ).data
        still_exist = [i for i in matches if i.lifecycle_state != "TERMINATED"]

        if not still_exist:
            raise NodeNotFound(f"{nodename}")
        if len(still_exist) > 1:
            print("ERROR!")  # TODO

        return cls.from_response(still_exist[0], config)

    @classmethod
    def from_response(
        cls: Type["OracleNode"], response: oci.core.models.Instance, config: dict
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

        compute_client = oci.core.ComputeClient(config)
        virtual_network_client = oci.core.VirtualNetworkClient(config)

        node_id = response.id
        vnic_id = (
            compute_client.list_vnic_attachments(
                response.compartment_id, instance_id=node_id
            )
            .data[0]
            .vnic_id
        )
        ip = virtual_network_client.get_vnic(vnic_id).data.private_ip

        return cls(name=name, state=node_state, ip=ip, id=node_id)

    @classmethod
    def all(cls, config, nodespace: dict):
        client = oci.core.ComputeClient(config)
        instances = client.list_instances(
            compartment_id=nodespace["compartment_id"]
        ).data
        nodes = [
            instance
            for instance in instances
            if instance.freeform_tags.get("type") == "compute"
        ]

        return [cls.from_response(instance, config) for instance in nodes]

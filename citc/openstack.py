import openstack  # type: ignore


def client():
    return openstack.connect()


def get_types_info(client):
    flavors = client.compute.flavors()
    return {
        f["name"]: {
            "memory": int(f["ram"] * 0.8),
            "cores_per_socket": f["vcpus"],
            "threads_per_core": "1",
        }
        for f in flavors
    }

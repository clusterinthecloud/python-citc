from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TypedDict, Optional


class NodeState(Enum):
    """
    https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html
    https://cloud.google.com/compute/docs/instances/instance-life-cycle
    https://docs.microsoft.com/en-us/azure/virtual-machines/windows/states-lifecycle

    =========== ============= ===================== =========================================== ============
    State       AWS           Google                Oracle                                      Azure
    =========== ============= ===================== =========================================== ============
    PENDING     pending       PROVISIONING STAGING  MOVING PROVISIONING CREATING_IMAGE STARTING starting
    RUNNING     running       RUNNING               RUNNING                                     running
    STOPPING    stopping      STOPPING              STOPPING                                    stopping
    STOPPED     stopped       STOPPED TERMINATED    STOPPED                                     stopped
    TERMINATING shutting-down                       TERMINATING                                 deallocating
    TERMINATED  terminated                          TERMINATED                                  deallocated
    OTHER                     SUSPENDING, SUSPENDED
    =========== ============= ===================== =========================================== ============
    """

    PENDING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    TERMINATING = auto()
    TERMINATED = auto()
    NOT_FOUND = auto()
    OTHER = auto()


class CloudNode(ABC):
    name: str
    state: NodeState
    ip: str
    id: str

    def __init__(self, name, state, ip, id):
        self.name = name
        self.state = state
        self.ip = ip
        self.id = id

    @classmethod
    @abstractmethod
    def all(cls, client, nodespace: dict):
        pass


class NodeTypeInfo(TypedDict):
    memory: int
    cores_per_socket: int
    threads_per_core: int
    arch: Optional[str]
    cluster_group: bool

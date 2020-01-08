from abc import ABC, abstractmethod
from enum import Enum, auto


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

    def __init__(self, name, state):
        self.name = name
        self.state = state

    @classmethod
    @abstractmethod
    def all(cls, client, nodespace: dict):
        pass

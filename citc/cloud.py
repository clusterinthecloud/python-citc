from abc import ABC
from enum import Enum, auto


class NodeState(Enum):
    """
    https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html
    https://cloud.google.com/compute/docs/instances/instance-life-cycle

    =========== ============= ===================== ===========================================
    State       AWS           Google                Oracle
    =========== ============= ===================== ===========================================
    PENDING     pending       PROVISIONING STAGING  MOVING PROVISIONING CREATING_IMAGE STARTING
    RUNNING     running       RUNNING               RUNNING
    STOPPING    stopping      STOPPING              STOPPING
    STOPPED     stopped       STOPPED TERMINATED    STOPPED
    TERMINATING shutting-down                       TERMINATING
    TERMINATED  terminated                          TERMINATED
    OTHER                     SUSPENDING, SUSPENDED
    =========== ============= ===================== ===========================================
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

from abc import ABC
from enum import Enum, auto


class NodeState(Enum):
    RUNNING = auto()
    STOPPING = auto()
    NOT_FOUND = auto()
    OTHER = auto()


class CloudNode(ABC):
    name: str
    state: NodeState

    def __init__(self, name, state):
        self.name = name
        self.state = state

from __future__ import annotations
from typing import List

from src.messages import Message
from src.store import ArtifactStore

# forward reference to avoid circular import at runtime typing
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.bus import MessageBus

class BaseAgent:
    """
    Base class for agents.
    Agents are independent:
    - they do not call each other
    - they only react to messages
    - they emit new messages and artifacts via the bus
    """

    name: str = "base_agent"

    def handle(self, msg: Message, store: ArtifactStore, bus: "MessageBus") -> List[Message]:
        # Default behavior: do nothing.
        return []

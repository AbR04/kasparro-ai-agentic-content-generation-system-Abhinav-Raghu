from __future__ import annotations
from collections import deque
from typing import Deque, Dict, List, Type

from src.messages import Message, ArtifactCreated, Done
from src.store import Artifact, ArtifactStore


class MessageBus:
    """
    Event-driven orchestrator.

    Key properties:
    - Agents are independent. They never call each other.
    - Orchestrator only routes messages and holds shared store.
    - Flow is dynamic: tasks/messages determine what happens next.
    """

    def __init__(self, store: ArtifactStore) -> None:
        self.store = store
        self.queue: Deque[Message] = deque()
        self.subscribers: Dict[str, List["BaseAgent"]] = {}

        # Stop conditions:
        self._done = False
        self._done_reason = ""

    def subscribe(self, message_type: str, agent: "BaseAgent") -> None:
        self.subscribers.setdefault(message_type, []).append(agent)

    def publish(self, msg: Message) -> None:
        self.queue.append(msg)

    def publish_many(self, msgs: List[Message]) -> None:
        for m in msgs:
            self.publish(m)

    def put_artifact(self, key: str, value, produced_by: str) -> None:
        """
        Store an artifact AND emit an ArtifactCreated event.
        """
        self.store.put(Artifact(key=key, value=value, meta={"produced_by": produced_by}))
        self.publish(ArtifactCreated(key))

    def done(self, reason: str) -> None:
        self._done = True
        self._done_reason = reason
        self.publish(Done(reason))

    def run(self, max_steps: int = 10_000) -> None:
        """
        Runs until:
        - Done is triggered OR queue drains.
        """
        steps = 0
        while self.queue and not self._done:
            steps += 1
            if steps > max_steps:
                raise RuntimeError("Max steps exceeded. Possible infinite loop.")

            msg = self.queue.popleft()

            # Dispatch to subscribed agents
            agents = self.subscribers.get(msg.type, [])
            for agent in agents:
                new_msgs = agent.handle(msg, self.store, self)
                if new_msgs:
                    self.publish_many(new_msgs)

        # If done not set, we still stop when queue drains.
        # That’s okay, but in our main we'll ensure required outputs exist.

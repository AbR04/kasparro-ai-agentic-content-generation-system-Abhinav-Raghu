from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

# -----------------------------
# Core idea:
# - Orchestrator routes "messages"
# - Agents subscribe to message types
# - Agents emit new messages (dynamic coordination)
# -----------------------------

MessageType = Literal["Start", "Task", "ArtifactCreated", "NeedArtifact", "Done"]


@dataclass(frozen=True)
class Message:
    """Base message type. Concrete messages below."""
    type: MessageType


@dataclass(frozen=True)
class Start(Message):
    """Kick-off message. PlannerAgent reacts to this and creates tasks dynamically."""
    goal: str = "build_pages"

    def __init__(self, goal: str = "build_pages") -> None:
        object.__setattr__(self, "type", "Start")
        object.__setattr__(self, "goal", goal)


@dataclass(frozen=True)
class Task(Message):
    """
    A task message represents 'work to be done' at runtime.

    This is IMPORTANT:
    - Tasks are NOT hard-coded function calls.
    - PlannerAgent creates tasks dynamically and pushes them into the queue.
    - Worker agents pick tasks they know how to execute.
    """
    name: str
    requires: List[str] = field(default_factory=list)   # artifact keys required
    produces: List[str] = field(default_factory=list)   # artifact keys produced
    payload: Dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        name: str,
        requires: Optional[List[str]] = None,
        produces: Optional[List[str]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        object.__setattr__(self, "type", "Task")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "requires", requires or [])
        object.__setattr__(self, "produces", produces or [])
        object.__setattr__(self, "payload", payload or {})


@dataclass(frozen=True)
class ArtifactCreated(Message):
    """Emitted whenever an artifact is stored. Enables reactive agent behavior."""
    key: str

    def __init__(self, key: str) -> None:
        object.__setattr__(self, "type", "ArtifactCreated")
        object.__setattr__(self, "key", key)


@dataclass(frozen=True)
class NeedArtifact(Message):
    """
    Emitted when an agent cannot proceed because a required artifact is missing.
    Includes the original Task so it can be retried later.
    """
    task_name: str
    missing_key: str
    blocked_task: "Task"  # <-- add this

    def __init__(self, task_name: str, missing_key: str, blocked_task: "Task") -> None:
        object.__setattr__(self, "type", "NeedArtifact")
        object.__setattr__(self, "task_name", task_name)
        object.__setattr__(self, "missing_key", missing_key)
        object.__setattr__(self, "blocked_task", blocked_task)



@dataclass(frozen=True)
class Done(Message):
    """Completion signal."""
    reason: str = "All required outputs produced"

    def __init__(self, reason: str = "All required outputs produced") -> None:
        object.__setattr__(self, "type", "Done")
        object.__setattr__(self, "reason", reason)

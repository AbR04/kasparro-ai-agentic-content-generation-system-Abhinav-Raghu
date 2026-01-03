from __future__ import annotations
from typing import Dict, List, Set

from src.agents.base import BaseAgent
from src.messages import Message, NeedArtifact, ArtifactCreated, Task

class TaskCoordinatorAgent(BaseAgent):
    """
    Dynamic coordination mechanism:
    - Collects blocked tasks when agents emit NeedArtifact
    - Requeues them when the missing artifact is later created

    Fixes:
    1) Dedup is done per (task_id, missing_key) not per task_id alone
       so tasks can re-block on different missing artifacts.
    2) (Optional) Only requeue tasks when all required artifacts exist.
       This reduces useless retries, but still remains agentic.
    """
    name = "task_coordinator_agent"

    def __init__(self) -> None:
        # missing_key -> list of blocked tasks waiting on that artifact
        self.waiting: Dict[str, List[Task]] = {}

        # Dedup per (task_id + missing_key) to avoid duplicates,
        # BUT still allow the same task to wait on a different key later.
        self.seen_pairs: Set[str] = set()

    def _task_id(self, task: Task) -> str:
        # Deterministic ID for task "identity"
        return f"{task.name}|{'-'.join(task.requires)}|{'-'.join(task.produces)}"

    def handle(self, msg: Message, store, bus) -> List[Message]:
        # 1) When an agent says "I need X", store the blocked task under that key
        if msg.type == "NeedArtifact":
            need = msg  # type: ignore
            if not isinstance(need, NeedArtifact):
                return []

            t = need.blocked_task
            tid = self._task_id(t)

            # ✅ Fix Issue 1: dedup per (task + missing_key)
            pair_key = f"{tid}||{need.missing_key}"
            if pair_key in self.seen_pairs:
                return []

            self.seen_pairs.add(pair_key)
            self.waiting.setdefault(need.missing_key, []).append(t)
            return []

        # 2) When an artifact is created, requeue tasks waiting on it
        if msg.type == "ArtifactCreated":
            created = msg  # type: ignore
            if not isinstance(created, ArtifactCreated):
                return []

            missing_key = created.key
            if missing_key not in self.waiting:
                return []

            blocked_tasks = self.waiting.pop(missing_key)

            # ✅ Fix Issue 2 (efficiency): only requeue tasks that are now fully ready
            # Tasks that still miss other requires will be kept waiting under their next missing key
            ready: List[Task] = []
            for t in blocked_tasks:
                # If ALL requires exist -> ready to retry
                if all(store.has(req) for req in t.requires):
                    ready.append(t)
                else:
                    # Still missing something else -> re-register under the next missing key
                    # This keeps retries minimal and intelligent.
                    for req in t.requires:
                        if not store.has(req):
                            # Create a new "NeedArtifact" internally by just placing it back into waiting list
                            tid = self._task_id(t)
                            pair_key = f"{tid}||{req}"
                            if pair_key not in self.seen_pairs:
                                self.seen_pairs.add(pair_key)
                                self.waiting.setdefault(req, []).append(t)
                            break

            return ready

        return []

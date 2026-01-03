from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Artifact:
    """
    An artifact is a named, machine-readable output produced by an agent.
    Agents do not share global state. They communicate via artifacts in this store.
    """
    key: str
    value: Any
    meta: Dict[str, Any]


class ArtifactStore:
    """
    Central store of artifacts.
    Owned by the orchestrator (bus), not by agents.
    """

    def __init__(self) -> None:
        self._artifacts: Dict[str, Artifact] = {}

    def has(self, key: str) -> bool:
        return key in self._artifacts

    def get(self, key: str) -> Optional[Artifact]:
        return self._artifacts.get(key)

    def require(self, key: str) -> Artifact:
        art = self.get(key)
        if art is None:
            raise KeyError(f"Missing required artifact: {key}")
        return art

    def put(self, artifact: Artifact) -> None:
        self._artifacts[artifact.key] = artifact

    def keys(self) -> Dict[str, bool]:
        """Small helper for debugging."""
        return {k: True for k in self._artifacts.keys()}

"""
Orchestrator implements the "agentic system" backbone:

- Artifact: a message passed between agents
- Store: holds artifacts (shared state is controlled by orchestrator)
- AgentSpec: explicit agent boundaries (inputs/outputs)
- GraphRunner: runs agents when their inputs exist (DAG-ish execution)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Set


@dataclass(frozen=True)
class Artifact:
    """
    A unit of communication between agents.

    name: unique key (e.g., "product_model", "faq_page_json")
    payload: the actual data (dict/list/etc.)
    meta: provenance info (agent name, version notes)
    """
    name: str
    payload: Any
    meta: Dict[str, Any]


class Store:
    """
    Artifact store owned by orchestrator.

    Why this matters:
    - Agents do NOT call each other directly
    - Agents do NOT rely on hidden global variables
    - Inputs/outputs are explicit via artifact names
    """
    def __init__(self) -> None:
        self._artifacts: Dict[str, Artifact] = {}

    def put(self, artifact: Artifact) -> None:
        self._artifacts[artifact.name] = artifact

    def get(self, name: str) -> Optional[Artifact]:
        return self._artifacts.get(name)

    def require(self, name: str) -> Artifact:
        art = self.get(name)
        if art is None:
            raise KeyError(f"Missing required artifact: {name}")
        return art


@dataclass(frozen=True)
class AgentSpec:
    """
    Minimal agent spec:
    - name: unique agent name
    - inputs: artifact names required
    - outputs: artifact names produced
    """
    name: str
    inputs: List[str]
    outputs: List[str]


class Agent(Protocol):
    spec: AgentSpec

    def run(self, store: Store) -> List[Artifact]:
        ...


class GraphRunner:
    """
    Executes a list of agents based on dependencies:

    If an agent’s input artifacts exist in the store -> run it once.
    Keep looping until no more progress can be made.

    This forms a dependency-driven pipeline (DAG-ish).
    """
    def __init__(self, agents: List[Agent]) -> None:
        self.agents = agents
        self._validate_unique_names()

    def _validate_unique_names(self) -> None:
        names = [a.spec.name for a in self.agents]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate agent names found. Must be unique.")

    def describe(self) -> Dict[str, Dict[str, List[str]]]:
        return {a.spec.name: {"inputs": a.spec.inputs, "outputs": a.spec.outputs} for a in self.agents}

    def run(self, store: Store) -> None:
        completed: Set[str] = set()

        progress = True
        while progress:
            progress = False
            for agent in self.agents:
                if agent.spec.name in completed:
                    continue

                # agent is runnable only when all inputs exist
                if all(store.get(inp) is not None for inp in agent.spec.inputs):
                    outputs = agent.run(store)
                    for art in outputs:
                        store.put(art)
                    completed.add(agent.spec.name)
                    progress = True

        missing = [a.spec.name for a in self.agents if a.spec.name not in completed]
        if missing:
            raise RuntimeError(
                "Graph could not complete. These agents never ran due to unmet inputs: "
                + ", ".join(missing)
            )

from __future__ import annotations
import json

from src.bus import MessageBus
from src.data import PRODUCT_INPUT
from src.messages import Start
from src.store import Artifact, ArtifactStore

from src.agents.planner import PlannerAgent
from src.agents.parser import ParserAgent
from src.agents.questions import QuestionAgent
from src.agents.faq import FAQAgent
from src.agents.pages import PagesAgent
from src.agents.writer import WriterAgent
from src.agents.coordinator import TaskCoordinatorAgent



def main() -> None:
    # 1) Create orchestrator-owned store and bus
    store = ArtifactStore()
    bus = MessageBus(store)

    # 2) Seed the only input as an artifact (no hidden globals)
    store.put(Artifact(key="raw_product_input", value=PRODUCT_INPUT, meta={"source": "src/data.py"}))

    # 3) Create agents (independent) and subscribe them to message types
    agents = [
        PlannerAgent(),
        ParserAgent(),
        QuestionAgent(),
        FAQAgent(),
        PagesAgent(),
        WriterAgent(),
        TaskCoordinatorAgent(),
    ]

    # Subscriptions:
    # - Planner reacts to Start
    # - Worker agents react to Task
    for a in agents:
        if a.name == "planner_agent":
            bus.subscribe("Start", a)
        elif a.name == "task_coordinator_agent":
            bus.subscribe("NeedArtifact", a)
            bus.subscribe("ArtifactCreated", a)
        else:
            bus.subscribe("Task", a)


    # 4) Publish Start event (we do NOT call agents directly)
    bus.publish(Start(goal="build_pages"))

    # 5) Run event loop
    bus.run()

    # 6) Print proof of agentic execution
    print("✅ Agentic run complete.")
    if store.has("written_files"):
        print("Outputs:", store.require("written_files").value)
    else:
        print("⚠️ No written_files artifact found. Store keys:", store.keys())

    # Optional: print what artifacts exist (good debugging)
    # print("Artifacts:", json.dumps(store.keys(), indent=2))


if __name__ == "__main__":
    main()

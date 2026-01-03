from __future__ import annotations
import json
import os
from typing import List

from src.agents.base import BaseAgent
from src.messages import Message, Task, NeedArtifact

class WriterAgent(BaseAgent):
    name = "writer_agent"

    def handle(self, msg: Message, store, bus) -> List[Message]:
        if msg.type != "Task":
            return []

        task = msg  # type: ignore
        if not isinstance(task, Task) or task.name != "WriteOutputs":
            return []

        required = ["faq_page_json", "product_page_json", "comparison_page_json"]
        for k in required:
            if not store.has(k):
                return [NeedArtifact(task.name, k, task)]


        faq = store.require("faq_page_json").value
        prod = store.require("product_page_json").value
        comp = store.require("comparison_page_json").value

        os.makedirs("out", exist_ok=True)

        paths = [
            ("out/faq.json", faq),
            ("out/product_page.json", prod),
            ("out/comparison_page.json", comp),
        ]

        written = []
        for path, payload in paths:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            written.append(path)

        bus.put_artifact("written_files", {"files": written}, produced_by=self.name)
        bus.done("All required JSON pages written to /out")
        return []

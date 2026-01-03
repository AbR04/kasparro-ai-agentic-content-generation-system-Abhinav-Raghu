from __future__ import annotations
from typing import List

from src.agents.base import BaseAgent
from src.messages import Message, Task, NeedArtifact
from src.logic import assert_only_allowed_fields

class ParserAgent(BaseAgent):
    name = "parser_agent"

    def handle(self, msg: Message, store, bus) -> List[Message]:
        if msg.type != "Task":
            return []

        task = msg  # type: ignore
        if not isinstance(task, Task) or task.name != "ParseProduct":
            return []

        # Autonomy: refuse to run if prerequisites missing
        if not store.has("raw_product_input"):
            return [NeedArtifact(task.name, "raw_product_input", task)]

        raw = store.require("raw_product_input").value

        # Guardrail: no extra facts allowed
        assert_only_allowed_fields(raw)

        # Normalize (ensure types are consistent)
        product_model = {
            "product_name": str(raw["product_name"]),
            "concentration": str(raw["concentration"]),
            "skin_type": list(raw["skin_type"]),
            "key_ingredients": list(raw["key_ingredients"]),
            "benefits": list(raw["benefits"]),
            "how_to_use": str(raw["how_to_use"]),
            "side_effects": str(raw["side_effects"]),
            "price_inr": int(raw["price_inr"]),
        }

        bus.put_artifact("product_model", product_model, produced_by=self.name)
        return []

from __future__ import annotations
from typing import List

from src.agents.base import BaseAgent
from src.messages import Message, Task, NeedArtifact
from src.templates import TemplateEngine, faq_page_template, product_page_template, comparison_page_template

class PagesAgent(BaseAgent):
    name = "pages_agent"

    def handle(self, msg: Message, store, bus) -> List[Message]:
        if msg.type != "Task":
            return []

        task = msg  # type: ignore
        if not isinstance(task, Task):
            return []

        engine = TemplateEngine()

        # Render FAQ Page
        if task.name == "RenderFAQPage":
            if not store.has("product_model"):
                return [NeedArtifact(task.name, "product_model", task)]
            if not store.has("faq_content"):
                return [NeedArtifact(task.name, "faq_content", task)]

            ctx = {
                "product_model": store.require("product_model").value,
                "faq_content": store.require("faq_content").value,
            }
            page = engine.render(faq_page_template(), ctx)
            bus.put_artifact("faq_page_json", page, produced_by=self.name)
            return []

        # Render Product Page
        if task.name == "RenderProductPage":
            if not store.has("product_model"):
                return [NeedArtifact(task.name, "product_model", task)]

            ctx = {"product_model": store.require("product_model").value}
            page = engine.render(product_page_template(), ctx)
            bus.put_artifact("product_page_json", page, produced_by=self.name)
            return []

        # Build Comparison (create Product B + render comparison page)
        if task.name == "BuildComparison":
            if not store.has("product_model"):
                return [NeedArtifact(task.name, "product_model", task)]

            a = store.require("product_model").value

            # Fictional Product B (structured, explicitly fictional)
            product_b = {
                "product_name": "RadiantDrop Vitamin C Serum (Fictional)",
                "concentration": "5% Vitamin C",
                "skin_type": ["Combination"],
                "key_ingredients": ["Vitamin C"],
                "benefits": ["Brightening"],
                "how_to_use": "Apply a small amount in the morning.",
                "side_effects": "May cause mild irritation in sensitive skin.",
                "price_inr": 799,
                "fictional": True,
            }

            bus.put_artifact("product_b_model", product_b, produced_by=self.name)

            ctx = {
                "product_model": a,
                "product_b_model": product_b,
            }
            page = engine.render(comparison_page_template(), ctx)
            bus.put_artifact("comparison_page_json", page, produced_by=self.name)
            return []

        return []

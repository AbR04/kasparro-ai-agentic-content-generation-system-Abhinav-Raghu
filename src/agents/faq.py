from __future__ import annotations
from typing import List, Dict

from src.agents.base import BaseAgent
from src.messages import Message, Task, NeedArtifact

class FAQAgent(BaseAgent):
    name = "faq_agent"

    def handle(self, msg: Message, store, bus) -> List[Message]:
        if msg.type != "Task":
            return []

        task = msg  # type: ignore
        if not isinstance(task, Task) or task.name != "ComposeFAQ":
            return []

        # Autonomy: require both artifacts
        if not store.has("product_model"):
            return [NeedArtifact(task.name, "product_model", task)]
        if not store.has("question_bank"):
            return [NeedArtifact(task.name, "question_bank", task)]

        p = store.require("product_model").value
        qb = store.require("question_bank").value

        # Pick 5 questions across categories (deterministic selection)
        chosen = [
            ("Informational", qb["categories"]["Informational"][0]),
            ("Usage", qb["categories"]["Usage"][0]),
            ("Usage", qb["categories"]["Usage"][1]),
            ("Safety", qb["categories"]["Safety"][0]),
            ("Purchase", qb["categories"]["Purchase"][0]),
        ]

        # Build answers strictly from dataset fields only
        def answer(category: str, q: str) -> str:
            if "price" in q.lower():
                return f"The price is ₹{p['price_inr']}."
            if "side effect" in q.lower() or "tingling" in q.lower():
                return f"Possible side effect: {p['side_effects']}."
            if "when" in q.lower() or "apply" in q.lower() or "drops" in q.lower():
                return p["how_to_use"]
            if "skin" in q.lower():
                return f"Suitable for: {', '.join(p['skin_type'])} skin types."
            # fallback informational
            return f"{p['product_name']} is a Vitamin C serum ({p['concentration']}) with key ingredients {', '.join(p['key_ingredients'])}."

        qas: List[Dict[str, str]] = []
        for cat, q in chosen:
            qas.append({
                "category": cat,
                "question": q,
                "answer": answer(cat, q),
            })

        faq_content = {
            "product_name": p["product_name"],
            "qas": qas,
        }

        bus.put_artifact("faq_content", faq_content, produced_by=self.name)
        return []

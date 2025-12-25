"""
All agents in one file for easy learning.

Agents:
1) ParseNormalizeAgent -> product_model
2) QuestionBankAgent -> question_bank (>=15 categorized)
3) FAQComposerAgent -> faq_content (select 5 and answer from data only)
4) FAQPageAgent -> faq_page_json (template engine)
5) ProductPageAgent -> product_page_json (template engine)
6) ComparisonAgent -> product_b_model + comparison_page_json (template engine)
7) WriterAgent -> writes JSON files
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict, List

from src.orchestrator import AgentSpec, Artifact, Store
from src.logic import assert_only_allowed_fields
from src.templates import TemplateEngine, faq_template, product_page_template, comparison_template


class ParseNormalizeAgent:
    spec = AgentSpec(
        name="parse_normalize_agent",
        inputs=["raw_product_input"],
        outputs=["product_model"],
    )

    def run(self, store: Store) -> List[Artifact]:
        raw: Dict[str, Any] = store.require("raw_product_input").payload
        assert_only_allowed_fields(raw)

        # Normalization: make sure types are clean & consistent
        model = {
            "product_name": str(raw["product_name"]),
            "concentration": str(raw["concentration"]),
            "skin_type": [str(x) for x in raw["skin_type"]],
            "key_ingredients": [str(x) for x in raw["key_ingredients"]],
            "benefits": [str(x) for x in raw["benefits"]],
            "how_to_use": str(raw["how_to_use"]),
            "side_effects": str(raw["side_effects"]),
            "price_inr": int(raw["price_inr"]),
        }

        return [Artifact("product_model", model, {"agent": self.spec.name})]


class QuestionBankAgent:
    spec = AgentSpec(
        name="question_bank_agent",
        inputs=["product_model"],
        outputs=["question_bank"],
    )

    def run(self, store: Store) -> List[Artifact]:
        p = store.require("product_model").payload
        name = p["product_name"]
        conc = p["concentration"]
        skin = ", ".join(p["skin_type"])
        ingredients = ", ".join(p["key_ingredients"])
        benefits = ", ".join(p["benefits"])

        bank = {
            "Informational": [
                f"What is {name}?",
                f"What does {conc} mean in {name}?",
                f"Who is {name} suitable for?",
                f"What are the key ingredients in {name}?",
            ],
            "Usage": [
                f"How do I use {name}?",
                f"When should I apply {name}?",
                f"How many drops should I use?",
                f"Do I need sunscreen after {name}?",
            ],
            "Safety": [
                f"Are there side effects of {name}?",
                f"What should sensitive skin users expect from {name}?",
                f"What does mild tingling mean when using {name}?",
            ],
            "Purchase": [
                f"What is the price of {name}?",
                f"Is {name} priced at ₹{p['price_inr']}?",
                f"What do I get for ₹{p['price_inr']}?",
            ],
            "Fitment": [
                f"Is {name} suitable for {skin} skin?",
                f"Will {name} help with {benefits}?",
                f"Does {name} contain {ingredients}?",
            ],
            "Comparison": [
                f"How does {name} compare to a fictional alternative?",
                f"How does {name} compare by price to Product B?",
            ],
        }

        payload = {"total_questions": sum(len(v) for v in bank.values()), "categories": bank}
        return [Artifact("question_bank", payload, {"agent": self.spec.name})]


class FAQComposerAgent:
    spec = AgentSpec(
        name="faq_composer_agent",
        inputs=["product_model", "question_bank"],
        outputs=["faq_content"],
    )

    def run(self, store: Store) -> List[Artifact]:
        p = store.require("product_model").payload
        qb = store.require("question_bank").payload["categories"]

        selected = [
            ("Informational", qb["Informational"][0]),
            ("Informational", qb["Informational"][3]),
            ("Usage", qb["Usage"][0]),
            ("Safety", qb["Safety"][0]),
            ("Purchase", qb["Purchase"][0]),
        ]

        def answer(q: str) -> str:
            ql = q.lower()
            if ql.startswith("what is"):
                return f"{p['product_name']} is a skincare serum featuring {', '.join(p['key_ingredients'])}."
            if "key ingredients" in ql or "contain" in ql:
                return f"Key ingredients listed are: {', '.join(p['key_ingredients'])}."
            if "how do i use" in ql or "apply" in ql:
                return p["how_to_use"]
            if "side effects" in ql or "sensitive" in ql or "tingling" in ql:
                return p["side_effects"]
            if "price" in ql:
                return f"The price is ₹{p['price_inr']}."
            return "Answered strictly from the provided dataset."

        qas = [{"category": c, "question": q, "answer": answer(q)} for c, q in selected]
        return [Artifact("faq_content", {"qas": qas}, {"agent": self.spec.name, "min_qas": 5})]


class FAQPageAgent:
    spec = AgentSpec(
        name="faq_page_agent",
        inputs=["product_model", "faq_content"],
        outputs=["faq_page_json"],
    )

    def run(self, store: Store) -> List[Artifact]:
        engine = TemplateEngine()
        page = engine.render(
            faq_template(),
            context={
                "product": store.require("product_model").payload,
                "faq_content": store.require("faq_content").payload,
            },
        )
        return [Artifact("faq_page_json", page, {"agent": self.spec.name})]


class ProductPageAgent:
    spec = AgentSpec(
        name="product_page_agent",
        inputs=["product_model"],
        outputs=["product_page_json"],
    )

    def run(self, store: Store) -> List[Artifact]:
        engine = TemplateEngine()
        page = engine.render(product_page_template(), context={"product": store.require("product_model").payload})
        return [Artifact("product_page_json", page, {"agent": self.spec.name})]


class ComparisonAgent:
    spec = AgentSpec(
        name="comparison_agent",
        inputs=["product_model"],
        outputs=["product_b_model", "comparison_page_json"],
    )

    def run(self, store: Store) -> List[Artifact]:
        a = store.require("product_model").payload

        # Fictional Product B (structured + explicitly fictional)
        product_b = {
            "product_name": "RadiantShield Serum B (Fictional)",
            "key_ingredients": ["Niacinamide", "Hyaluronic Acid"],
            "benefits": ["Hydration", "Even-looking tone"],
            "price_inr": 799,
            "note": "Fictional comparator created solely for this assignment.",
        }

        engine = TemplateEngine()
        page = engine.render(comparison_template(), context={"product": a, "product_b": product_b})

        return [
            Artifact("product_b_model", product_b, {"agent": self.spec.name}),
            Artifact("comparison_page_json", page, {"agent": self.spec.name}),
        ]


class WriterAgent:
    spec = AgentSpec(
        name="writer_agent",
        inputs=["faq_page_json", "product_page_json", "comparison_page_json"],
        outputs=["written_files"],
    )

    def run(self, store: Store) -> List[Artifact]:
        os.makedirs("out", exist_ok=True)

        files = {
            "faq_page_json": "out/faq.json",
            "product_page_json": "out/product_page.json",
            "comparison_page_json": "out/comparison_page.json",
        }

        written = []
        for artifact_name, path in files.items():
            payload = store.require(artifact_name).payload
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            written.append(path)

        return [Artifact("written_files", {"files": written}, {"agent": self.spec.name})]

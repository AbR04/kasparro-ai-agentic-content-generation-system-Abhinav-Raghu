from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from src.logic import (
    format_price_inr,
    summary_block,
    ingredients_block,
    benefits_block,
    usage_block,
    safety_block,
    comparison_analysis,
)

@dataclass(frozen=True)
class FieldRule:
    name: str
    builder: Callable[[Dict[str, Any]], Any]
    depends_on: List[str]

@dataclass(frozen=True)
class Template:
    name: str
    version: str
    fields: List[FieldRule]

class TemplateEngine:
    """
    Custom template engine:
    - A Template is structured (fields + dependencies + builder rules)
    - Render produces machine-readable JSON (dict)
    """

    def render(self, template: Template, ctx: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {"template": {"name": template.name, "version": template.version}}

        for rule in template.fields:
            for dep in rule.depends_on:
                if dep not in ctx:
                    raise KeyError(f"Template missing dependency '{dep}' for field '{rule.name}'")
            out[rule.name] = rule.builder(ctx)

        return out

# -------------------
# Templates required by assignment
# -------------------

def faq_page_template() -> Template:
    return Template(
        name="FAQPage",
        version="1.0",
        fields=[
            FieldRule(
                name="product_name",
                depends_on=["product_model"],
                builder=lambda ctx: ctx["product_model"]["product_name"],
            ),
            FieldRule(
                name="faqs",
                depends_on=["faq_content"],
                builder=lambda ctx: ctx["faq_content"]["qas"],
            ),
        ],
    )

def product_page_template() -> Template:
    return Template(
        name="ProductPage",
        version="1.0",
        fields=[
            FieldRule(
                name="title",
                depends_on=["product_model"],
                builder=lambda ctx: ctx["product_model"]["product_name"],
            ),
            FieldRule(
                name="price",
                depends_on=["product_model"],
                builder=lambda ctx: {
                    "currency": "INR",
                    "value": int(ctx["product_model"]["price_inr"]),
                    "display": format_price_inr(int(ctx["product_model"]["price_inr"])),
                },
            ),
            FieldRule(
                name="summary",
                depends_on=["product_model"],
                builder=lambda ctx: summary_block(ctx["product_model"]),
            ),
            FieldRule(
                name="sections",
                depends_on=["product_model"],
                builder=lambda ctx: {
                    "ingredients": ingredients_block(ctx["product_model"]),
                    "benefits": benefits_block(ctx["product_model"]),
                    "usage": usage_block(ctx["product_model"]),
                    "safety": safety_block(ctx["product_model"]),
                },
            ),
        ],
    )

def comparison_page_template() -> Template:
    return Template(
        name="ComparisonPage",
        version="1.0",
        fields=[
            FieldRule(
                name="title",
                depends_on=["product_model", "product_b_model"],
                builder=lambda ctx: f"{ctx['product_model']['product_name']} vs {ctx['product_b_model']['product_name']}",
            ),
            FieldRule(
                name="products",
                depends_on=["product_model", "product_b_model"],
                builder=lambda ctx: {
                    "a": ctx["product_model"],
                    "b": ctx["product_b_model"],
                },
            ),
            FieldRule(
                name="analysis",
                depends_on=["product_model", "product_b_model"],
                builder=lambda ctx: comparison_analysis(ctx["product_model"], ctx["product_b_model"]),
            ),
            FieldRule(
                name="conclusion",
                depends_on=["product_model", "product_b_model"],
                builder=lambda ctx: "This comparison is generated deterministically from the provided dataset and a fictional competitor.",
            ),
        ],
    )

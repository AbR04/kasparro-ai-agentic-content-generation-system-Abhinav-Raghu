"""
Tiny template engine + 3 templates.

Template requirement:
- define templates for FAQ page, Product page, Comparison page
- template must specify fields + rules + dependencies on blocks
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from src.logic import (
    benefits_block,
    ingredients_block,
    safety_block,
    summary_block,
    usage_block,
    format_price_inr,
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
    def render(self, template: Template, context: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {"template": {"name": template.name, "version": template.version}}
        for rule in template.fields:
            for dep in rule.depends_on:
                if dep not in out and dep not in context:
                    raise ValueError(f"Missing dependency '{dep}' for field '{rule.name}' in {template.name}")
            out[rule.name] = rule.builder({**context, **out})
        return out


def faq_template() -> Template:
    def title(ctx: Dict[str, Any]) -> str:
        return f"FAQs: {ctx['product']['product_name']}"

    def items(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        return ctx["faq_content"]["qas"]

    return Template(
        name="faq_page",
        version="1.0",
        fields=[
            FieldRule("title", title, depends_on=["product"]),
            FieldRule("items", items, depends_on=["faq_content"]),
        ],
    )


def product_page_template() -> Template:
    def title(ctx: Dict[str, Any]) -> str:
        return ctx["product"]["product_name"]

    def price(ctx: Dict[str, Any]) -> Dict[str, Any]:
        p = ctx["product"]["price_inr"]
        return {"currency": "INR", "value": p, "display": format_price_inr(p)}

    def summary(ctx: Dict[str, Any]) -> Dict[str, Any]:
        return summary_block(ctx["product"])

    def sections(ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        p = ctx["product"]
        return [ingredients_block(p), benefits_block(p), usage_block(p), safety_block(p)]

    return Template(
        name="product_description_page",
        version="1.0",
        fields=[
            FieldRule("title", title, depends_on=["product"]),
            FieldRule("price", price, depends_on=["product"]),
            FieldRule("summary", summary, depends_on=["product"]),
            FieldRule("sections", sections, depends_on=["product"]),
        ],
    )


def comparison_template() -> Template:
    def title(ctx: Dict[str, Any]) -> str:
        return "Comparison: GlowBoost vs Product B"

    def products(ctx: Dict[str, Any]) -> Dict[str, Any]:
        return {"a": ctx["product"], "b": ctx["product_b"]}

    def analysis(ctx: Dict[str, Any]) -> Dict[str, Any]:
        return comparison_analysis(ctx["product"], ctx["product_b"])

    return Template(
        name="comparison_page",
        version="1.0",
        fields=[
            FieldRule("title", title, depends_on=["product", "product_b"]),
            FieldRule("products", products, depends_on=["product", "product_b"]),
            FieldRule("analysis", analysis, depends_on=["product", "product_b"]),
        ],
    )

"""
Reusable content logic blocks.

Rules:
- deterministic
- derive only from provided data fields
- no external facts
"""

from __future__ import annotations
from typing import Any, Dict, List, Set


ALLOWED_FIELDS: Set[str] = {
    "product_name",
    "concentration",
    "skin_type",
    "key_ingredients",
    "benefits",
    "how_to_use",
    "side_effects",
    "price_inr",
}


def assert_only_allowed_fields(model: Dict[str, Any]) -> None:
    """Guardrail: prevent accidental extra fields (no new facts)."""
    extra = set(model.keys()) - ALLOWED_FIELDS
    if extra:
        raise ValueError(f"Disallowed fields found: {sorted(extra)}")


def format_price_inr(price: int) -> str:
    return f"₹{price}"


def summary_block(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "one_liner": (
            f"{p['product_name']} is a Vitamin C serum for {', '.join(p['skin_type'])} skin types, "
            f"featuring {', '.join(p['key_ingredients'])}."
        ),
        "concentration": p["concentration"],
        "primary_benefits": list(p["benefits"]),
    }


def ingredients_block(p: Dict[str, Any]) -> Dict[str, Any]:
    return {"headline": "Key Ingredients", "items": [{"ingredient": x} for x in p["key_ingredients"]]}


def benefits_block(p: Dict[str, Any]) -> Dict[str, Any]:
    return {"headline": "Benefits", "items": [{"benefit": x} for x in p["benefits"]]}


def usage_block(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "headline": "How to Use",
        "exact_instruction_from_data": p["how_to_use"],
        "routine_skeleton": ["Cleanse face", "Apply serum", "Use sunscreen (per input)"],
    }


def safety_block(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "headline": "Safety & Side Effects",
        "side_effects": p["side_effects"],
        "note": "No medical claims added; derived strictly from provided data.",
    }


def compare_overlap(a: List[str], b: List[str]) -> Dict[str, Any]:
    a_set, b_set = set(a), set(b)
    return {
        "overlap": sorted(list(a_set & b_set)),
        "a_only": sorted(list(a_set - b_set)),
        "b_only": sorted(list(b_set - a_set)),
    }


def compare_price(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    if a["price_inr"] < b["price_inr"]:
        winner = "a"
    elif b["price_inr"] < a["price_inr"]:
        winner = "b"
    else:
        winner = "tie"

    return {"a": a["price_inr"], "b": b["price_inr"], "winner": winner, "rule": "Lower price wins; tie if equal."}


def comparison_analysis(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "price": compare_price(a, b),
        "ingredients": compare_overlap(a["key_ingredients"], b["key_ingredients"]),
        "benefits": compare_overlap(a["benefits"], b["benefits"]),
    }

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

def assert_only_allowed_fields(raw: Dict[str, Any]) -> None:
    extra = set(raw.keys()) - ALLOWED_FIELDS
    if extra:
        raise ValueError(f"Found disallowed fields: {sorted(extra)}")

def format_price_inr(price: int) -> str:
    return f"₹{int(price)}"

def summary_block(p: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "headline": f"{p['product_name']} — {p['concentration']}",
        "highlights": p["benefits"],
        "for_skin_type": p["skin_type"],
    }

def ingredients_block(p: Dict[str, Any]) -> Dict[str, Any]:
    return {"items": [{"name": ing} for ing in p["key_ingredients"]]}

def benefits_block(p: Dict[str, Any]) -> Dict[str, Any]:
    return {"items": [{"benefit": b} for b in p["benefits"]]}

def usage_block(p: Dict[str, Any]) -> Dict[str, Any]:
    # Keep the instruction exactly from dataset.
    return {"how_to_use": p["how_to_use"]}

def safety_block(p: Dict[str, Any]) -> Dict[str, Any]:
    return {"side_effects": p["side_effects"]}

def compare_overlap(list_a: List[str], list_b: List[str]) -> Dict[str, Any]:
    a, b = set(list_a), set(list_b)
    return {
        "overlap": sorted(list(a & b)),
        "only_a": sorted(list(a - b)),
        "only_b": sorted(list(b - a)),
    }

def comparison_analysis(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    price_a = int(a["price_inr"])
    price_b = int(b["price_inr"])
    price_winner = "A" if price_a < price_b else "B" if price_b < price_a else "Tie"

    return {
        "price": {
            "a": {"value": price_a, "display": format_price_inr(price_a)},
            "b": {"value": price_b, "display": format_price_inr(price_b)},
            "winner": price_winner,
        },
        "ingredients": compare_overlap(a["key_ingredients"], b["key_ingredients"]),
        "benefits": compare_overlap(a["benefits"], b["benefits"]),
    }

"""
Product description normalizer.
Uses dictionary (user-confirmed) first, falls back to LLM for unknown items.
"""

import json
import requests
from sqlalchemy.orm import Session

from app.config import OLLAMA_URL, OLLAMA_MODEL
from app.models.receipt import ProductDictionary

PRODUCT_CATEGORIES = [
    "Carnes/Proteínas",
    "Frutas/Verduras/Legumes",
    "Laticínios",
    "Padaria",
    "Bebidas",
    "Limpeza",
    "Higiene Pessoal",
    "Grãos/Cereais",
    "Molhos/Condimentos",
    "Congelados",
    "Snacks/Doces",
    "Outros",
]

NORMALIZE_PROMPT = """You are a Brazilian supermarket product identifier.
Given abbreviated product descriptions from a receipt, return the full product name and category.

Categories: {categories}

Return ONLY a JSON array. Each item must have:
- "name": full product name in Portuguese (e.g. "Extrato de Tomate Elefante 340g")
- "category": one of the categories listed above

Items to identify:
{items}"""


def normalize_items(
    raw_descriptions: list[str],
    user_id: int,
    db: Session,
) -> list[dict]:
    """Normalize product descriptions using dictionary + LLM fallback.
    
    Returns list of {"name": str, "category": str} in same order as input.
    """
    results = [None] * len(raw_descriptions)
    unknown_indices = []

    # Step 1: Check dictionary for known items
    for i, desc in enumerate(raw_descriptions):
        desc_upper = desc.strip().upper()
        entry = (
            db.query(ProductDictionary)
            .filter(
                ProductDictionary.user_id == user_id,
                ProductDictionary.raw_description == desc_upper,
            )
            .first()
        )
        if entry:
            results[i] = {"name": entry.normalized_name, "category": entry.category}
        else:
            unknown_indices.append(i)

    # Step 2: If there are unknown items, ask LLM
    if unknown_indices:
        unknown_descs = [raw_descriptions[i] for i in unknown_indices]
        llm_results = _ask_llm(unknown_descs)

        for j, idx in enumerate(unknown_indices):
            if j < len(llm_results):
                results[idx] = llm_results[j]
            else:
                results[idx] = {
                    "name": raw_descriptions[idx],
                    "category": "Outros",
                }

    return results


def _ask_llm(descriptions: list[str]) -> list[dict]:
    """Ask LLM to normalize and categorize unknown product descriptions."""
    items_list = "\n".join(f"{i+1}. {d}" for i, d in enumerate(descriptions))
    prompt = NORMALIZE_PROMPT.format(
        categories=", ".join(PRODUCT_CATEGORIES),
        items=items_list,
    )

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 2048,
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()["response"].strip()

        # Parse JSON
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()

        parsed = json.loads(result)
        if isinstance(parsed, list):
            # Validate categories
            for item in parsed:
                if item.get("category") not in PRODUCT_CATEGORIES:
                    item["category"] = "Outros"
            return parsed

    except Exception:
        pass

    # Fallback: return as-is
    return [{"name": d, "category": "Outros"} for d in descriptions]


def save_to_dictionary(
    raw_description: str,
    normalized_name: str,
    category: str,
    user_id: int,
    db: Session,
):
    """Save a user-confirmed product mapping to the dictionary."""
    raw_upper = raw_description.strip().upper()

    existing = (
        db.query(ProductDictionary)
        .filter(
            ProductDictionary.user_id == user_id,
            ProductDictionary.raw_description == raw_upper,
        )
        .first()
    )

    if existing:
        existing.normalized_name = normalized_name
        existing.category = category
    else:
        entry = ProductDictionary(
            user_id=user_id,
            raw_description=raw_upper,
            normalized_name=normalized_name,
            category=category,
        )
        db.add(entry)

    db.commit()

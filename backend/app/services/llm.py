"""
LLM service - used ONLY for categorizing transactions.
Extraction is handled by regex for 100% accuracy.
"""

import json
import requests

from app.config import OLLAMA_URL, OLLAMA_MODEL

CATEGORIES = [
    "Transporte",
    "Alimentação",
    "Mercado",
    "Telefone/Internet/Streaming",
    "Saúde/Academia",
    "Compras",
    "Viagem/Lazer",
    "Taxas/Seguros",
    "Assinaturas",
    "Outros",
]

CATEGORIZE_PROMPT = """Classify each transaction description into exactly one category.

Categories:
- Transporte (Uber, 99, taxi, rides, gas stations)
- Alimentação (restaurants, bakeries, food delivery, snack bars)
- Mercado (supermarkets, grocery stores, mercadinhos)
- Telefone/Internet/Streaming (phone bills, internet, Netflix, Crunchyroll, Spotify)
- Saúde/Academia (gyms, Wellhub, clinics, dentists, pharmacies)
- Compras (Amazon, Shopee, Americanas, clothing, electronics stores)
- Viagem/Lazer (flights, hotels, tickets, cinema, concerts, courses)
- Taxas/Seguros (IOF, insurance, card fees, bank fees)
- Assinaturas (recurring monthly subscriptions, plans)
- Outros (anything that doesn't fit above)

Return ONLY a JSON array of strings (one category per transaction, in the same order).
Example: ["Transporte", "Mercado", "Compras"]

Transactions to classify:
{descriptions}"""


def categorize_transactions(transactions: list[dict]) -> list[dict]:
    """Use LLM to categorize a list of transactions by their descriptions.
    
    Takes transactions with date/description/amount and adds a 'category' field.
    """
    if not transactions:
        return transactions

    descriptions = [t["description"] for t in transactions]

    # Format descriptions as numbered list for clarity
    desc_list = "\n".join(f"{i+1}. {d}" for i, d in enumerate(descriptions))

    prompt = CATEGORIZE_PROMPT.format(descriptions=desc_list)

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

        # Parse JSON from response
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()

        categories = json.loads(result)

        # Validate and apply categories
        if isinstance(categories, list) and len(categories) == len(transactions):
            for i, cat in enumerate(categories):
                if cat in CATEGORIES:
                    transactions[i]["category"] = cat
                else:
                    transactions[i]["category"] = "Outros"
        else:
            # If LLM returned wrong count, fall back to rule-based
            transactions = _fallback_categorize(transactions)

    except Exception:
        # If LLM fails, use rule-based categorization
        transactions = _fallback_categorize(transactions)

    return transactions


def _fallback_categorize(transactions: list[dict]) -> list[dict]:
    """Rule-based fallback categorization when LLM is unavailable."""
    for t in transactions:
        desc = t["description"].upper()

        if any(x in desc for x in ["UBER", "DL*UBERRIDES", "99 TECNOLOGIA", "99 - NUPAY", "99*", "99 NUPAY", "99 -"]):
            t["category"] = "Transporte"
        elif any(x in desc for x in ["PASTELOTTA", "BOLO FIT", "HOLYPAES", "GOURMET", "SORVE", "CHINAI", "BRAMEX", "RESTAUR", "PAES"]):
            t["category"] = "Alimentação"
        elif any(x in desc for x in ["MERCADINHO", "MERCADO", "SUPERMARKET", "SUPERMERCADO", "JIM.COM", "MULTTI BY"]):
            t["category"] = "Mercado"
        elif any(x in desc for x in ["TIM*", "TIM ", "CLARO", "VIVO", "VIVOEASY", "CRUNCHYROLL", "GOOGLE FLO"]):
            t["category"] = "Telefone/Internet/Streaming"
        elif any(x in desc for x in ["WELLHUB", "GYMPASS", "CLINICA", "ODONT", "FARMACIA", "PHARMACY"]):
            t["category"] = "Saúde/Academia"
        elif any(x in desc for x in ["AMAZON", "SHOPEE", "AMERICANAS", "BEMOL", "LOJAS"]):
            t["category"] = "Compras"
        elif any(x in desc for x in ["LATAM", "GOL", "AEREO", "TKT AER", "INGRESSO", "FUNDACAO", "QCONCURS"]):
            t["category"] = "Viagem/Lazer"
        elif any(x in desc for x in ["IOF", "SEGURO", "ANUIDADE", "TARIFA", "CUSTO TRANS"]):
            t["category"] = "Taxas/Seguros"
        elif any(x in desc for x in ["MERCADOPAGO", "BMB *"]):
            t["category"] = "Assinaturas"
        else:
            t["category"] = "Outros"

    return transactions

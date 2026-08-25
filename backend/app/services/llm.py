import json
import re
import requests

from app.config import OLLAMA_URL, OLLAMA_MODEL

PROMPT_TEMPLATE = """Extract ALL purchase transactions from this credit card invoice page.

Return ONLY a valid JSON array. Each object must have exactly these 4 fields:
- "date": string (e.g. "24/03" or "27 JAN")
- "description": string (merchant name, short)
- "amount": number (decimal with dot, e.g. 17.45)
- "category": string (one of: "Transporte", "Alimentação", "Mercado", "Telefone/Internet/Streaming", "Saúde/Academia", "Compras", "Viagem/Lazer", "Taxas/Seguros", "Assinaturas", "Outros")

Rules:
- ONLY include actual purchases/charges
- Do NOT include payments of previous invoices, credits, totals, summary lines, or fees info
- If there are no transactions on this page, return []
- Start response with [ and end with ]

Text:
{text}"""


def _try_parse_json(text: str) -> list[dict] | None:
    """Try to parse JSON from LLM response, handling common issues."""
    text = text.strip()

    # Extract from markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    # Try direct parse
    try:
        result = json.loads(text)
        if isinstance(result, list):
            return result
    except json.JSONDecodeError:
        pass

    # Try to find a JSON array in the text
    match = re.search(r'\[.*', text, re.DOTALL)
    if match:
        json_text = match.group()
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            pass

        # If truncated, close at last complete object
        last_brace = json_text.rfind("}")
        if last_brace > 0:
            truncated = json_text[: last_brace + 1] + "]"
            try:
                return json.loads(truncated)
            except json.JSONDecodeError:
                pass

    return None


def _call_ollama(prompt: str) -> str:
    """Make a single call to Ollama and return the response text."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 4096,
            },
        },
        timeout=180,
    )
    response.raise_for_status()
    return response.json()["response"]


def extract_transactions_from_pages(pages_text: list[str]) -> list[dict] | None:
    """Extract transactions by processing each PDF page separately."""

    all_transactions = []

    # Find pages that likely contain transaction listings
    # by looking for patterns like dates followed by amounts
    transaction_pages = []
    for i, page in enumerate(pages_text):
        # Look for transaction-like patterns (date + description + amount)
        import re
        # Bradesco: DD/MM ... VALUE
        # Nubank: DD MES ... R$ VALUE
        bradesco_pattern = re.findall(r'\d{2}/\d{2}\s+\S+.*\d+,\d{2}', page)
        nubank_pattern = re.findall(r'\d{2}\s+(?:JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ)\s+.+R\$\s+\d', page)

        # If page has 5+ transaction-like lines, it's probably a transaction page
        if len(bradesco_pattern) >= 5 or len(nubank_pattern) >= 5:
            transaction_pages.append(i)

    # If no transaction pages found, try all pages except first
    if not transaction_pages:
        transaction_pages = list(range(1 if len(pages_text) > 1 else 0, len(pages_text)))

    for i in transaction_pages:
        page_text = pages_text[i]
        if not page_text.strip():
            continue

        prompt = PROMPT_TEMPLATE.format(text=page_text)
        result = _call_ollama(prompt)
        transactions = _try_parse_json(result)

        if transactions:
            for t in transactions:
                amount = t.get("amount", 0)
                if isinstance(amount, (int, float)) and amount > 0:
                    all_transactions.append(t)

    if not all_transactions:
        raise ValueError("LLM returned invalid JSON response")

    # Deduplicate by (date, amount, first 15 chars of description)
    seen = set()
    unique = []
    for t in all_transactions:
        desc_short = str(t.get("description", "")).strip().upper()[:15]
        key = (
            str(t.get("date", "")).strip(),
            desc_short,
            round(float(t.get("amount", 0)), 2),
        )
        if key not in seen:
            seen.add(key)
            unique.append(t)

    return unique


def extract_transactions_with_llm(pdf_text: str, pages: list[str] = None) -> list[dict] | None:
    """Use local LLM (Ollama) to extract transactions from invoice text.
    
    If pages are provided, processes each page separately for better accuracy.
    Otherwise falls back to processing the full text.
    """
    try:
        if pages:
            return extract_transactions_from_pages(pages)

        # Fallback: process full text (for shorter invoices)
        prompt = PROMPT_TEMPLATE.format(text=pdf_text)
        result = _call_ollama(prompt)
        transactions = _try_parse_json(result)

        if not transactions:
            raise ValueError("LLM returned invalid JSON response")

        return [t for t in transactions if isinstance(t.get("amount", 0), (int, float)) and t["amount"] > 0]

    except requests.exceptions.ConnectionError:
        raise ConnectionError("Could not connect to Ollama. Make sure it's running with: ollama serve")
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error communicating with Ollama: {e}")

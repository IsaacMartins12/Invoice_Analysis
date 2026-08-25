"""
Hybrid extraction: Regex for precise data extraction + LLM for categorization.

Each bank has its own regex pattern for extracting transactions (date, description, amount).
The LLM is only used for categorizing the descriptions into spending categories.
"""

import re


def detect_bank(text: str) -> str:
    """Detect which bank issued the invoice based on content patterns."""
    text_upper = text.upper()
    if "NUBANK" in text_upper or "NU PAGAMENTOS" in text_upper or "NUPAY" in text_upper:
        return "nubank"
    elif "BRADESCO" in text_upper or "BANCO BRADESCO" in text_upper:
        return "bradesco"
    else:
        return "unknown"


def extract_bradesco(text: str) -> list[dict]:
    """Extract transactions from Bradesco invoice PDF text.
    
    Pattern: DD/MM  DESCRIPTION  VALUE (comma as decimal separator)
    """
    pattern = re.compile(r"(\d{2}/\d{2})\s+(.+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})")
    transactions = []

    for date, description, amount in pattern.findall(text):
        description_upper = description.strip().upper()

        # Filter out non-transaction lines
        if any(word in description_upper for word in [
            "PAG BOLETO BANCARIO",
            "FATURA MENSAL",
        ]):
            continue

        # Convert amount: "1.234,56" -> 1234.56
        amount_float = float(
            amount.replace(".", "").replace(",", ".")
        )

        if amount_float <= 0:
            continue

        transactions.append({
            "date": date,
            "description": description.strip(),
            "amount": amount_float,
        })

    return transactions


def extract_nubank(text: str) -> list[dict]:
    """Extract transactions from Nubank invoice PDF text.
    
    Pattern: DD MÊS  DESCRIPTION  R$ VALUE
    """
    months = "JAN|FEV|MAR|ABR|MAI|JUN|JUL|AGO|SET|OUT|NOV|DEZ"
    pattern = re.compile(
        rf"(\d{{2}}\s+(?:{months}))\s+(.+?)\s+R\$\s+(\d{{1,3}}(?:\.\d{{3}})*,\d{{2}})"
    )
    transactions = []

    # Lines to skip (summary data, not transactions)
    skip_words = [
        "FATURA ANTERIOR", "PAGAMENTO RECEBIDO", "TOTAL A PAGAR",
        "LIMITE TOTAL", "SALDO EM ABERTO", "FECHAMENTO",
        "SAQUE NO CRÉDITO", "PIX NO CRÉDITO", "SAQUE NO CREDITO",
        "PIX NO CREDITO", "PAGAMENTOS DE BOLETO", "CARTÃO DE CRÉDITO",
        "CARTAO DE CREDITO",
    ]

    for date, description, amount in pattern.findall(text):
        description_upper = description.strip().upper()

        # Skip summary lines
        if any(word in description_upper for word in skip_words):
            continue

        # Skip lines that look like subtotals (user name lines)
        # e.g. "Isaac D S Martins"
        if re.match(r"^[A-Z][A-Z]+ [A-Z] [A-Z] [A-Z]", description_upper):
            continue
        if re.match(r"^[A-Z]+\s+[A-Z]\s+[A-Z]\s+[A-Z]+", description_upper):
            continue

        # Skip period range lines like "a 24 FEV"
        if re.match(r"^A\s+\d{2}\s", description_upper):
            continue

        # Convert amount
        amount_float = float(
            amount.replace(".", "").replace(",", ".")
        )

        if amount_float <= 0:
            continue

        transactions.append({
            "date": date,
            "description": description.strip(),
            "amount": amount_float,
        })

    return transactions


def extract_transactions(text: str) -> tuple[list[dict], str]:
    """Extract transactions from invoice text using appropriate regex.
    
    Returns:
        Tuple of (transactions, bank_name)
    """
    bank = detect_bank(text)

    if bank == "bradesco":
        transactions = extract_bradesco(text)
    elif bank == "nubank":
        transactions = extract_nubank(text)
    else:
        transactions = []

    return transactions, bank

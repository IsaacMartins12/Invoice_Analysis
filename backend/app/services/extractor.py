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
    elif (
        "CONTA DO INTER" in text_upper
        or "07790.00116" in text_upper
        or ("DESPESAS DA FATURA" in text_upper and "VALOR ANTECIPADO" in text_upper)
    ):
        return "inter"
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


def extract_inter(text: str) -> list[dict]:
    """Extract purchases from a Banco Inter invoice PDF text.

    Pattern: DD de month. YYYY  DESCRIPTION  -  [+] R$ VALUE
    A leading ``+`` identifies payments/credits and is intentionally skipped.
    """
    months = (
        r"jan(?:\.)?|fev(?:\.)?|mar(?:\.)?|abr(?:\.)?|mai(?:\.)?|jun(?:\.)?|"
        r"jul(?:\.)?|ago(?:\.)?|set(?:\.)?|out(?:\.)?|nov(?:\.)?|dez(?:\.)?"
    )
    pattern = re.compile(
        rf"^\s*(\d{{2}}\s+de\s+(?:{months})\s+\d{{4}})"
        rf"\s+([^\r\n]+?)\s+-\s+(\+?)\s*R\$\s*"
        rf"(\d{{1,3}}(?:\.\d{{3}})*,\d{{2}})\s*$",
        re.IGNORECASE | re.MULTILINE,
    )
    transactions = []

    for date, description, sign, amount in pattern.findall(text):
        # Banco Inter prints payments as positive credits, e.g. "+ R$ 884,12".
        if sign == "+" or "PAGAMENTO" in description.upper():
            continue

        transactions.append({
            "date": date.strip(),
            "description": description.strip(),
            "amount": float(amount.replace(".", "").replace(",", ".")),
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
    elif bank == "inter":
        transactions = extract_inter(text)
    else:
        transactions = []

    return transactions, bank


MONTH_MAP = {
    "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAI": 5, "JUN": 6,
    "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12,
    "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "ABRIL": 4, "MAIO": 5,
    "JUNHO": 6, "JULHO": 7, "AGOSTO": 8, "SETEMBRO": 9, "OUTUBRO": 10,
    "NOVEMBRO": 11, "DEZEMBRO": 12,
}


def detect_invoice_period(text: str, bank: str) -> tuple[int | None, int | None]:
    """Try to detect the invoice month/year from the PDF content.
    
    Returns:
        Tuple of (month, year) or (None, None) if not detected.
    """
    text_upper = text.upper()

    if bank == "bradesco":
        # Bradesco: "Vencimento 05/05/2026"
        match = re.search(r"VENCIMENTO\s+(\d{2})/(\d{2})/(\d{4})", text_upper)
        if match:
            month = int(match.group(2))
            year = int(match.group(3))
            return month, year

        # Fallback: "Fatura Mensal" page date pattern
        match = re.search(r"(\d{2})/(\d{2})/(\d{4})", text)
        if match:
            month = int(match.group(2))
            year = int(match.group(3))
            return month, year

    elif bank == "nubank":
        # Nubank: "FATURA 03 MAR 2026"
        match = re.search(r"FATURA\s+\d{2}\s+(\w{3})\s+(\d{4})", text_upper)
        if match:
            month_str = match.group(1)
            year = int(match.group(2))
            month = MONTH_MAP.get(month_str, None)
            if month:
                return month, year

        # Fallback: "Data de vencimento: 03 MAR 2026"
        match = re.search(r"VENCIMENTO[:\s]+\d{2}\s+(\w{3})\s+(\d{4})", text_upper)
        if match:
            month_str = match.group(1)
            year = int(match.group(2))
            month = MONTH_MAP.get(month_str, None)
            if month:
                return month, year

    # Generic fallback: look for any date pattern with year
    match = re.search(r"(\d{2})/(\d{2})/(\d{4})", text)
    if match:
        month = int(match.group(2))
        year = int(match.group(3))
        if 1 <= month <= 12 and 2020 <= year <= 2030:
            return month, year

    return None, None

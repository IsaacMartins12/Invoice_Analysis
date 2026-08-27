"""Tests for the regex extractor service."""

from app.services.extractor import (
    detect_bank,
    extract_bradesco,
    extract_nubank,
    extract_inter,
    extract_transactions,
    detect_invoice_period,
)


# --- Bank detection ---

def test_detect_bradesco():
    text = "Banco Bradesco S/A - CNPJ 60.746.948/0001-12"
    assert detect_bank(text) == "bradesco"


def test_detect_nubank():
    text = "Esta é a sua fatura de março, NuPay transactions"
    assert detect_bank(text) == "nubank"


def test_detect_inter():
    text = "Faça o pagamento pela conta do Inter. Despesas da fatura"
    assert detect_bank(text) == "inter"


def test_detect_unknown():
    text = "Algum texto aleatório sem banco"
    assert detect_bank(text) == "unknown"


# --- Bradesco extraction ---

def test_bradesco_basic_transaction():
    text = "24/03 MERCADINHO GR MANAUS 8,00"
    txns = extract_bradesco(text)
    assert len(txns) == 1
    assert txns[0]["date"] == "24/03"
    assert txns[0]["amount"] == 8.0
    assert "MERCADINHO" in txns[0]["description"]


def test_bradesco_filters_payment():
    text = "31/03 PAG BOLETO BANCARIO 2.159,57"
    txns = extract_bradesco(text)
    assert len(txns) == 0


def test_bradesco_large_amount():
    text = "14/01 Tkt Aer*LATAM AIRLIN04/04 SAO PAULO 1.346,48"
    txns = extract_bradesco(text)
    assert len(txns) == 1
    assert txns[0]["amount"] == 1346.48


def test_bradesco_multiple_transactions():
    text = """24/03 MERCADINHO GR MANAUS 8,00
24/03 DL*UberRides Sao Paulo 7,92
25/03 UBER* TRIP WWW.UBER.COM. 21,98"""
    txns = extract_bradesco(text)
    assert len(txns) == 3
    total = sum(t["amount"] for t in txns)
    assert abs(total - 37.90) < 0.01


# --- Nubank extraction ---

def test_nubank_basic_transaction():
    text = "29 JAN 99 - NuPay R$ 17,45"
    txns = extract_nubank(text)
    assert len(txns) == 1
    assert txns[0]["date"] == "29 JAN"
    assert txns[0]["amount"] == 17.45


def test_nubank_filters_summary_lines():
    text = """24 FEV Isaac D S Martins R$ 422,89
27 JAN a 24 FEV R$ 30,00
29 JAN 99 - NuPay R$ 17,45"""
    txns = extract_nubank(text)
    assert len(txns) == 1
    assert txns[0]["amount"] == 17.45


def test_nubank_with_parcel():
    text = "27 JAN •••• 1460 Bmb *Vivoeasy Lite - Parcela 5/12 R$ 30,00"
    txns = extract_nubank(text)
    assert len(txns) == 1
    assert txns[0]["amount"] == 30.0


# --- Banco Inter extraction ---

def test_inter_extracts_purchases_and_skips_payment():
    text = """04 de jun. 2026   PAGAMENTO ON LINE                  -   + R$ 884,12
27 de nov. 2025   AMAZON BR (Parcela 08 de 08)             -     R$ 74,13
10 de jun. 2026   OPENAI *CHATGPT SUBSCR                   -     R$ 99,90"""
    txns = extract_inter(text)
    assert len(txns) == 2
    assert txns[0] == {
        "date": "27 de nov. 2025",
        "description": "AMAZON BR (Parcela 08 de 08)",
        "amount": 74.13,
    }
    assert txns[1]["amount"] == 99.90


def test_inter_accepts_single_space_between_pdf_columns():
    text = "05 de jun. 2026 IFD*IFOOD CLUB - R$ 5,95"
    txns = extract_inter(text)
    assert txns == [{
        "date": "05 de jun. 2026",
        "description": "IFD*IFOOD CLUB",
        "amount": 5.95,
    }]


def test_extract_transactions_inter():
    text = """Faça o pagamento pela conta do Inter
Despesas da fatura
12 de jun. 2026   MP *MAUROAGIOTA (Parcela 01 de 08)       -   R$ 145,93"""
    txns, bank = extract_transactions(text)
    assert bank == "inter"
    assert len(txns) == 1
    assert txns[0]["amount"] == 145.93


# --- Period detection ---

def test_detect_period_bradesco():
    text = "Vencimento 05/05/2026"
    month, year = detect_invoice_period(text, "bradesco")
    assert month == 5
    assert year == 2026


def test_detect_period_nubank():
    text = "FATURA 03 MAR 2026"
    month, year = detect_invoice_period(text, "nubank")
    assert month == 3
    assert year == 2026


def test_detect_period_unknown():
    text = "Nenhuma data aqui"
    month, year = detect_invoice_period(text, "unknown")
    assert month is None
    assert year is None


# --- Full flow ---

def test_extract_transactions_bradesco():
    text = """Banco Bradesco S/A
24/03 MERCADINHO GR MANAUS 8,00
31/03 PAG BOLETO BANCARIO 2.159,57
25/03 UBER* TRIP SAO PAULO 21,98"""
    txns, bank = extract_transactions(text)
    assert bank == "bradesco"
    assert len(txns) == 2  # payment filtered out
    total = sum(t["amount"] for t in txns)
    assert abs(total - 29.98) < 0.01


def test_extract_transactions_unknown_bank():
    text = "Random text without bank markers"
    txns, bank = extract_transactions(text)
    assert bank == "unknown"
    assert len(txns) == 0

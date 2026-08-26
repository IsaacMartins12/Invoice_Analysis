"""
Parser for NFC-e (Nota Fiscal de Consumidor Eletrônica).
Extracts items from the SEFAZ URL found in the QR Code of a receipt.
"""

import re
import requests
from dataclasses import dataclass


@dataclass
class ParsedItem:
    raw_description: str
    quantity: float
    unit: str
    unit_price: float
    total_price: float


@dataclass
class ParsedReceipt:
    store_name: str
    store_cnpj: str
    date: str
    total: float
    access_key: str
    items: list[ParsedItem]


def parse_nfce_url(url: str) -> ParsedReceipt:
    """Fetch and parse a NFC-e from its SEFAZ URL.
    
    The URL typically comes from scanning the QR Code on the receipt.
    """
    try:
        response = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        response.raise_for_status()
        html = response.text
    except Exception as e:
        raise ConnectionError(f"Could not fetch NFC-e: {e}")

    return _parse_nfce_html(html, url)


def _parse_nfce_html(html: str, url: str = "") -> ParsedReceipt:
    """Parse NFC-e HTML page to extract store info and items."""

    # Extract access key from URL or page
    access_key = ""
    key_match = re.search(r'chNFe=(\d{44})', url)
    if key_match:
        access_key = key_match.group(1)
    else:
        key_match = re.search(r'(\d{44})', html)
        if key_match:
            access_key = key_match.group(1)

    # Extract store name
    store_name = "Desconhecido"
    store_match = re.search(r'<span class="txtTopo"[^>]*>(.*?)</span>', html)
    if store_match:
        store_name = store_match.group(1).strip()
    else:
        store_match = re.search(r'class="txtTopo">(.*?)<', html)
        if store_match:
            store_name = store_match.group(1).strip()

    # Extract CNPJ
    store_cnpj = ""
    cnpj_match = re.search(r'CNPJ:\s*([\d./-]+)', html)
    if cnpj_match:
        store_cnpj = cnpj_match.group(1).strip()

    # Extract date
    date = ""
    date_match = re.search(r'Emiss[ãa]o:\s*(\d{2}/\d{2}/\d{4})', html)
    if date_match:
        date = date_match.group(1)
    else:
        date_match = re.search(r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})', html)
        if date_match:
            date = date_match.group(1)

    # Extract items
    items = _extract_items(html)

    # Extract total
    total = 0.0
    total_match = re.search(r'Valor total R\$\s*([\d.,]+)', html)
    if total_match:
        total = _parse_brl(total_match.group(1))
    else:
        total_match = re.search(r'vNF.*?>([\d.,]+)<', html)
        if total_match:
            total = _parse_brl(total_match.group(1))
        elif items:
            total = sum(i.total_price for i in items)

    return ParsedReceipt(
        store_name=store_name,
        store_cnpj=store_cnpj,
        date=date,
        total=total,
        access_key=access_key,
        items=items,
    )


def _extract_items(html: str) -> list[ParsedItem]:
    """Extract product items from NFC-e HTML."""
    items = []

    # Common NFC-e HTML pattern for items
    # Pattern 1: table-based layout
    item_blocks = re.findall(
        r'class="txtTit"[^>]*>(.*?)</span>.*?'
        r'Qtde\.?:?\s*([\d.,]+)\s*'
        r'(?:UN|un|Un|KG|kg|Kg|LT|lt|Lt|UN\.?|PC|pc)?\s*'
        r'(?:x|X)?\s*'
        r'(?:Vl\.\s*Unit\.?:?\s*)?([\d.,]+).*?'
        r'(?:Vl\.\s*Total:?\s*)?([\d.,]+)',
        html, re.DOTALL
    )

    if item_blocks:
        for desc, qty, unit_price, total_price in item_blocks:
            desc_clean = re.sub(r'<[^>]+>', '', desc).strip()
            items.append(ParsedItem(
                raw_description=desc_clean,
                quantity=_parse_brl(qty),
                unit="UN",
                unit_price=_parse_brl(unit_price),
                total_price=_parse_brl(total_price),
            ))
        return items

    # Pattern 2: span-based layout (different SEFAZ states)
    item_pattern = re.findall(
        r'(?:txtTit|xProd)["\s>]+([^<]+)<.*?'
        r'(?:qCom|[Qq]tde)["\s:>]+([\d.,]+).*?'
        r'(?:uCom|[Uu][Nn])["\s:>]+(\w+).*?'
        r'(?:vUnCom|[Vv]l\.?\s*[Uu]nit)["\s:>]+([\d.,]+).*?'
        r'(?:vProd|[Vv]l\.?\s*[Tt]otal)["\s:>]+([\d.,]+)',
        html, re.DOTALL
    )

    if item_pattern:
        for desc, qty, unit, unit_price, total_price in item_pattern:
            desc_clean = re.sub(r'<[^>]+>', '', desc).strip()
            items.append(ParsedItem(
                raw_description=desc_clean,
                quantity=_parse_brl(qty),
                unit=unit.upper(),
                unit_price=_parse_brl(unit_price),
                total_price=_parse_brl(total_price),
            ))
        return items

    return items


def parse_manual_items(items_text: str) -> list[ParsedItem]:
    """Parse manually entered items (fallback when QR code doesn't work).
    
    Expected format per line: DESCRIPTION | QTY | UNIT_PRICE
    """
    items = []
    for line in items_text.strip().split("\n"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 3:
            desc = parts[0]
            qty = _parse_brl(parts[1])
            price = _parse_brl(parts[2])
            items.append(ParsedItem(
                raw_description=desc,
                quantity=qty,
                unit="UN",
                unit_price=price,
                total_price=round(qty * price, 2),
            ))
    return items


def _parse_brl(value: str) -> float:
    """Parse Brazilian number format: '1.234,56' -> 1234.56"""
    value = value.strip()
    value = value.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return 0.0

"""福福トレカ用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。
.card-itemが1商品のブロックで、.card-item__title(カード名+型番+レアリティ)
と.card-item__price(価格)を持つ。64件確認できた。
"""
from __future__ import annotations

import re
from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price

CODE_RARITY_RE = re.compile(r"^(.*?)\(([^)]+)\)\[([^\]]+)\]")


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for item in soup.select(".card-item"):
        title_el = item.select_one(".card-item__title")
        if not title_el:
            continue
        raw_title = title_el.get_text(strip=True)

        price_el = item.select_one(".card-item__price")
        if not price_el:
            continue
        price = parse_price(price_el.get_text(" ", strip=True))
        if price is None:
            continue

        m = CODE_RARITY_RE.match(raw_title)
        if m:
            card_name, set_code, rarity = m.group(1).strip(), m.group(2), m.group(3)
        else:
            card_name, set_code, rarity = raw_title, None, None

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, set_code, rarity, buy_price, sell_price, source_site, fetched_at))

    return records

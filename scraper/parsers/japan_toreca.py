"""Japan-toreca用パーサー(販売価格のみ、PSA鑑定品コレクション)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。Shopify製
ストアで、.innerer単位に商品が構造化されている
(.product-block__title=カード名、.product-block_price=価格)。1ページ目
39件、最高42万円を確認済み。
"""
from __future__ import annotations

import re
from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso

PRICE_RE = re.compile(r"¥\s*([\d,]+)")


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for item in soup.select(".innerer"):
        title_el = item.select_one(".product-block__title")
        price_el = item.select_one(".product-block_price")
        if not title_el or not price_el:
            continue
        card_name = title_el.get_text(strip=True)

        m = PRICE_RE.search(price_el.get_text(" ", strip=True))
        if not m:
            continue
        price = int(m.group(1).replace(",", ""))

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, None, None, buy_price, sell_price, source_site, fetched_at))

    return records

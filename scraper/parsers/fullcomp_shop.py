"""フルコンプ ONLINE SHOP用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。Shopify製
ストアで、.product-card__content単位に商品が構造化されている。商品名は
Shopifyのビルドごとに変わりうるCSS Modulesクラスを避け、
`<a aria-label="...">`から直接取得する。40件確認済み。
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

    for item in soup.select(".product-card__content"):
        a = item.select_one("a[aria-label]")
        if not a:
            continue
        card_name = a["aria-label"]

        price_el = item.select_one("span.price")
        if not price_el:
            continue
        m = PRICE_RE.search(price_el.get_text(" ", strip=True))
        if not m:
            continue
        price = int(m.group(1).replace(",", ""))

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, None, None, buy_price, sell_price, source_site, fetched_at))

    return records

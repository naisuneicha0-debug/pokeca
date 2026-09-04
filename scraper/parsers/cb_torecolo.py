"""CBトレコロ用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。MakeShop系
ECテンプレートで、GA Enhanced Ecommerce用のクラス名
(.js-enhanced-ecommerce-item)で商品ブロックが構造化されている。
"""
from __future__ import annotations

import re
from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price

CODE_RE = re.compile(r"/shop/g/g([\w\-]+)/")


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for item in soup.select(".js-enhanced-ecommerce-item"):
        name_el = item.select_one(".js-enhanced-ecommerce-goods-name")
        if not name_el:
            continue
        card_name = name_el.get_text(strip=True)

        price_el = item.select_one(".js-enhanced-ecommerce-goods-price")
        if not price_el:
            continue
        price = parse_price(price_el.get_text(" ", strip=True))
        if price is None:
            continue

        rarity_el = item.select_one(".block-thumbnail-t--goods-category")
        rarity = rarity_el.get_text(strip=True) if rarity_el else None

        set_code = None
        m = CODE_RE.search(name_el.get("href", ""))
        if m:
            set_code = m.group(1)

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, set_code, rarity, buy_price, sell_price, source_site, fetched_at))

    return records

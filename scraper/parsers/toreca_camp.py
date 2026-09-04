"""トレカキャンプ用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。Shopify製
ストアで、商品ブロック(.product-item)ごとにタイトル・価格が構造化されて
いる。価格は状態別に「¥780～¥4,980」のようなレンジ表記のため、
HIGH_VALUE_THRESHOLDとの相性を考えレンジの上限(最高値)を採用する。
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

    for item in soup.select(".product-item"):
        title_el = item.select_one(".product-item__title")
        if not title_el:
            continue
        card_name = title_el.get_text(strip=True)

        price_el = item.select_one(".price")
        if not price_el:
            continue
        prices = [int(m.replace(",", "")) for m in PRICE_RE.findall(price_el.get_text(" ", strip=True))]
        if not prices:
            continue
        price = max(prices)

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, None, None, buy_price, sell_price, source_site, fetched_at))

    return records

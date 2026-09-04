"""トレカプラザ55用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。
.c-item-list__item単位で商品(全ジャンル混在)が構造化されており、
カード名末尾の[ポケモンカードゲーム]表記で絞り込む。
"""
from __future__ import annotations

from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for item in soup.select(".c-item-list__item"):
        ttl_el = item.select_one(".c-item-list__ttl")
        if not ttl_el:
            continue
        card_name = ttl_el.get_text(strip=True)
        if "ポケモンカードゲーム" not in card_name:
            continue

        price_el = item.select_one(".c-item-list__price")
        if not price_el:
            continue
        price = parse_price(price_el.get_text(" ", strip=True))
        if price is None:
            continue

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, None, None, buy_price, sell_price, source_site, fetched_at))

    return records

"""福福トレカコレクション用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。
div.c-itemsが全商品を包む1つのコンテナで、個別商品は
`a[href^="?pid="]`単位。日本語カード名は
`.c-items-name span.language.ja`、価格は`.c-items-price`から取得する
(カテゴリページ全78件確認済み)。
"""
from __future__ import annotations

from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    container = soup.select_one("div.c-items")
    if container is None:
        return records

    for a in container.find_all("a", href=True, recursive=False):
        name_el = a.select_one(".c-items-name span.language.ja") or a.select_one(".c-items-name")
        if not name_el:
            continue
        card_name = name_el.get_text(strip=True)

        price_el = a.select_one(".c-items-price")
        if not price_el:
            continue
        price = parse_price(price_el.get_text(" ", strip=True))
        if price is None:
            continue

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, None, None, buy_price, sell_price, source_site, fetched_at))

    return records

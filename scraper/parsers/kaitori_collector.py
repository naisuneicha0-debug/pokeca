"""買取コレクター用パーサー(買取価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-03)。
このページは全カードの網羅的な価格表ではなく、ジャンル別「買取実績
ハイライト」のカルーセルが複数(玩具・フィギュア等も含め5ジャンル分)
並んでいる構成だった。カルーセル自体は全ジャンル共通の構造
(a.slide.splide__slide > .slide_txt > .product_name / .product_price)
なので、リンク先URLが /card-kind/pokemoncard/ のものだけに絞り込む。
価格非公開の実績(価格が取れない項目)は除外する。
"""
from __future__ import annotations

import re
from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price

TRAILING_LABEL_RE = re.compile(r"(買取価格|買取上限価格|買取実績価格)\s*$")


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for a in soup.select("a.slide.splide__slide"):
        href = a.get("href", "")
        if "/card-kind/pokemoncard/" not in href:
            continue

        name_el = a.select_one(".product_name")
        price_el = a.select_one(".product_price")
        if not name_el or not price_el:
            continue

        price = parse_price(price_el.get_text(" ", strip=True))
        if price is None:
            continue

        name = name_el.get_text(" ", strip=True)
        name = TRAILING_LABEL_RE.sub("", name).strip()
        if not name:
            continue

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(name, None, None, buy_price, sell_price, source_site, fetched_at))

    return records

"""イエローサブマリン用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-06)。EC-CUBE系
テンプレートで.ec-shelfGrid__item単位に商品が構造化されている
(カード名を含むpタグ+.price02-default)。ただしポケモンカードカテゴリ
ページ自体の掲載件数が少なく(2件)、サプライ品中心でシングルカードの
専用カテゴリは見つかっていない。
"""
from __future__ import annotations

from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for item in soup.select(".ec-shelfGrid__item"):
        price_el = item.select_one(".price02-default")
        if not price_el:
            continue
        price = parse_price(price_el.get_text(" ", strip=True).replace("￥", "") + "円")
        if price is None:
            continue

        name_el = price_el.find_previous_sibling("p")
        if not name_el:
            continue
        card_name = name_el.get_text(strip=True)
        if not card_name:
            continue

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, None, None, buy_price, sell_price, source_site, fetched_at))

    return records

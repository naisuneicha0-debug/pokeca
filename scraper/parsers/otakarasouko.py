"""お宝創庫用パーサー(買取価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。
ul.bl_productが1商品のブロックで、[カテゴリー/商品名/買取参考価格]の
3項目を持つ。全ジャンル混在のページのため、カテゴリーが「ポケモン」を
含むものだけに絞り込む(1935件中1934件がポケモンカードだった)。
50万円以上のカードも複数確認できている。
"""
from __future__ import annotations

import re
from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for item in soup.select("ul.bl_product"):
        cat_el = item.select_one(".product_maker p")
        category = cat_el.get_text(strip=True) if cat_el else ""
        if "ポケモン" not in category:
            continue

        name_el = item.select_one(".product_title p")
        if not name_el:
            continue
        card_name = name_el.get_text(strip=True)

        price_el = item.select_one(".product_price p")
        if not price_el:
            continue
        price = parse_price(price_el.get_text(strip=True))
        if price is None:
            continue

        set_code = None
        m = re.search(r"\((\d{1,4}/\d{1,4})\)", card_name)
        if m:
            set_code = m.group(1)

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, set_code, None, buy_price, sell_price, source_site, fetched_at))

    return records

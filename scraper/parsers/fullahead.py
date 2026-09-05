"""フルアヘッド用パーサー(販売価格のみ、PSA鑑定品専門コーナー)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。
.itemName(カード名+型番)と.itemPrice(価格)がそれぞれ商品数分並ぶ構造
(親要素での1商品単位のラップが浅く直接対応付けできないため、出現順で
zipして対応させる)。1ページ目で50件、最高45.8万円を確認済み。
"""
from __future__ import annotations

import re
from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso

PRICE_RE = re.compile(r"([\d,]+)\s*円")
CODE_RE = re.compile(r"(PK-[\w\-]+)")


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    names = soup.select(".itemName")
    prices = soup.select(".itemPrice")

    for name_el, price_el in zip(names, prices):
        raw_name = name_el.get_text(strip=True)
        m = PRICE_RE.search(price_el.get_text(" ", strip=True))
        if not m:
            continue
        price = int(m.group(1).replace(",", ""))

        code_m = CODE_RE.search(raw_name)
        set_code = code_m.group(1) if code_m else None
        card_name = CODE_RE.sub("", raw_name).strip()

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, set_code, None, buy_price, sell_price, source_site, fetched_at))

    return records

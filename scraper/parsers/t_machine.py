"""たいむましん用パーサー(買取価格のみ、旧裏面専門)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。
table#tbl_modern内のtr.pokemon行が[カード名/シリーズ(旧裏面等)/買取価格]
の3列構造。103行中94件に実際の価格が入っていた。
"""
from __future__ import annotations

from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for tr in soup.select("tr.pokemon"):
        tds = tr.find_all("td")
        if len(tds) < 3:
            continue
        card_name = tds[0].get_text(strip=True)
        series = tds[1].get_text(strip=True)
        price = parse_price(tds[2].get_text(strip=True) + "円")
        if price is None or not card_name:
            continue

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, None, series or None, buy_price, sell_price, source_site, fetched_at))

    return records

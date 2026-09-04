"""オタチュウ用パーサー(買取価格のみ、PSA10鑑定品専門)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。シリーズ
ごとに複数のテーブル(id="tbl_modern"等)があり、いずれも
[No./レア/カード名/買取金額/更新]の5列構造。973行中872件に実際の価格が
入っており、50万円以上も20件確認できた(PSA10専門店のため高額カードが
多い)。
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

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for tr in rows:
            tds = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(tds) < 4:
                continue
            set_code, rarity, card_name, price_text = tds[0], tds[1], tds[2], tds[3]
            m = PRICE_RE.search(price_text)
            if not m:
                continue
            price = int(m.group(1).replace(",", ""))
            if not card_name:
                continue

            buy_price = price if direction == "buy" else None
            sell_price = price if direction == "sell" else None
            records.append(
                make_record(card_name, set_code or None, rarity or None, buy_price, sell_price, source_site, fetched_at)
            )

    return records

"""ポケキング用パーサー(買取価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。WordPress
ブロックエディタのdiv.wp-block-columnが1商品のブロックで、パイプ区切りで
テキスト化すると「カード名|型番|シリーズ|価格買取」(型番が無いものは3項目)
の順で並んでいる。件数は少ない(9件、ピックアップ商品のみ)。
"""
from __future__ import annotations

import re
from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso

PRICE_RE = re.compile(r"^([\d,]+)円買取$")


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for col in soup.select("div.wp-block-column"):
        parts = [p.strip() for p in col.get_text("|", strip=True).split("|") if p.strip()]
        if len(parts) < 3:
            continue
        m = PRICE_RE.match(parts[-1])
        if not m or "最大" in parts[-1]:
            continue
        price = int(m.group(1).replace(",", ""))
        card_name = parts[0]
        set_code = parts[1] if len(parts) >= 4 else None

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, set_code, None, buy_price, sell_price, source_site, fetched_at))

    return records

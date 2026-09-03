"""トレトク用パーサー(買取価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み。各カードは
<li data-name="..." data-price="..." data-modelNumber="..." data-rarity="...">
というdata属性付き要素で表現されている。
"""
from __future__ import annotations

from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for li in soup.select("li[data-price]"):
        attrs = {k.lower(): v for k, v in li.attrs.items()}
        price_raw = attrs.get("data-price")
        if not price_raw:
            continue
        try:
            price = int(price_raw)
        except ValueError:
            continue

        name = (attrs.get("data-name") or "").strip()
        model_number = (attrs.get("data-modelnumber") or "").strip()
        rarity = (attrs.get("data-rarity") or "").strip() or None

        card_name = name
        suffix = " ".join(p for p in (model_number, rarity) if p)
        if suffix and card_name.endswith(suffix):
            card_name = card_name[: -len(suffix)].strip()

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(
            make_record(card_name or name, model_number or None, rarity, buy_price, sell_price, source_site, fetched_at)
        )

    return records

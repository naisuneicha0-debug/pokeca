"""トイズキング用パーサー(買取価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。買取価格
表ページ内のJSリンク先が、S3上に直接公開されたJSON
(config/pricelistの2キーを持つオブジェクト。各商品はname/price等)を
指しており、そちらを直接叩けば静的に取得できる(hareruya2と同様の
パターン)。ページあたりの件数が少ない(3件)ため全カード網羅ではなく
ピックアップ商品と思われる。
"""
from __future__ import annotations

import json
from typing import List, Dict

from .base import make_record, now_iso


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    fetched_at = now_iso()
    records: List[Dict] = []

    try:
        data = json.loads(html)
    except ValueError:
        return records

    for product in data.get("pricelist", []):
        card_name = product.get("name")
        price = product.get("price")
        if not card_name or price is None:
            continue

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(
            make_record(card_name, product.get("optional_name") or None, None, buy_price, sell_price, source_site, fetched_at)
        )

    return records

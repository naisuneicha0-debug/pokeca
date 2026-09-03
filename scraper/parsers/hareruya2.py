"""晴れる屋2用パーサー。

buying-listページ内のJSに埋め込まれていた公開JSON API
(https://api.corp.hareruyamtg.com/user_data/hareruya2/json/products_all.json)
から取得したJSONをそのままパースする(2026-09-03確認)。

レスポンス形式: {"count": <int>, "products": [<product>, ...]}
各productには buy_price / sell_price が両方(整数、0=取り扱いなしの意味で
使われている)含まれており、1回のリクエストで買取・売値どちらも取れる。
そのためdirection引数は無視して両方のフィールドをそのまま使う。

titleフィールド例: "AZ(CP){サポート}〈138/171〉[XY/171]"
"""
from __future__ import annotations

import json
import re
from typing import List, Dict, Optional

from .base import make_record, now_iso

TITLE_RE = re.compile(r"^(?P<name>.+?)\((?P<rarity>[^)]*)\)")


def _parse_title(title: str) -> tuple[str, Optional[str]]:
    m = TITLE_RE.match(title.strip())
    if not m:
        return title.strip(), None
    name = m.group("name").strip()
    rarity = m.group("rarity").strip() or None
    return name, rarity


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    try:
        data = json.loads(html)
    except json.JSONDecodeError:
        return []

    products = data.get("products", [])
    fetched_at = now_iso()
    records: List[Dict] = []

    for p in products:
        title = p.get("title") or ""
        name, rarity = _parse_title(title)
        if not name:
            continue

        collection_number = p.get("collection_number")
        set_name = p.get("set_name")
        if collection_number and collection_number != "-":
            set_code = f"{set_name}-{collection_number}" if set_name else collection_number
        else:
            set_code = set_name

        buy_price = p.get("buy_price") or None
        sell_price = p.get("sell_price") or None
        if buy_price is None and sell_price is None:
            continue

        records.append(make_record(name, set_code, rarity, buy_price, sell_price, source_site, fetched_at))

    return records

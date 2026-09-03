"""フルコンプ秋葉原店用パーサー(買取価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み。ページ内に
`var tableData = [[...], [...], ...];` というJS配列でカード一覧が
直接埋め込まれている(DataTables.jsに渡すデータ)。
各行: [連番, カテゴリ, タイプ, レアリティ, "【rarity】名前(printed)setcode", "", "", 価格]
"""
from __future__ import annotations

import json
import re
from typing import List, Dict, Optional, Tuple

from .base import make_record, now_iso

TABLE_DATA_RE = re.compile(r"var\s+tableData\s*=\s*(\[.*?\]);", re.S)
NAME_RE = re.compile(r"^【[^】]*】(?P<name>.+?)\((?P<printed>\d+/[\w\-]+)\)(?P<set>\S*)$")


def _parse_name_cell(cell: str) -> Tuple[str, Optional[str]]:
    m = NAME_RE.match(cell.strip())
    if not m:
        return cell.strip(), None
    set_seg = m.group("set")
    printed = m.group("printed")
    set_code = f"{set_seg}-{printed}" if set_seg else printed
    return m.group("name").strip(), set_code


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    m = TABLE_DATA_RE.search(html)
    if not m:
        return []

    # 配列末尾にトレーリングカンマが入っている場合があり、JSONとして無効なため除去する。
    raw = re.sub(r",(\s*\])", r"\1", m.group(1))
    try:
        rows = json.loads(raw)
    except json.JSONDecodeError:
        return []

    fetched_at = now_iso()
    records: List[Dict] = []
    for row in rows:
        if len(row) < 8:
            continue
        rarity = (row[3] or "").strip() or None
        name_cell = row[4] or ""
        price_raw = row[7]

        try:
            price = int(str(price_raw).replace(",", ""))
        except (TypeError, ValueError):
            continue

        card_name, set_code = _parse_name_cell(name_cell)
        if not card_name:
            continue

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, set_code, rarity, buy_price, sell_price, source_site, fetched_at))

    return records

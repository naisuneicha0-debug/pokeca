"""遊々亭パーサー。

Claude.ai側でmarkdown変換後テキストに対して検証済みの正規表現
(引き継ぎ資料参照)を、生HTML(BeautifulSoup)向けに書き直したもの。
生HTML自体の構造は未検証のため、実行結果を見て要調整。
"""
from __future__ import annotations

import re
from typing import List, Dict, Optional, Tuple

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price

LINK_RE = re.compile(r"^/(?:buy|sell)/poc/card/([\w\-]+)/(\d+)$")
NAME_RE = re.compile(r"^([\w./\-]+)\s+([A-Z\-]+)\s+(.+)$")


def _parse_link_text(text: str) -> Optional[Tuple[str, str, str]]:
    text = " ".join(text.split())
    m = NAME_RE.match(text)
    if not m:
        return None
    printed_no, rarity, rest = m.groups()
    # 「メガリザードンXex メガリザードンXex」のようにカード名が2回連続する
    # 表示パターンを1つに畳む(検証済み正規表現の \3\] 部分に相当)。
    parts = rest.split()
    if len(parts) % 2 == 0:
        half = len(parts) // 2
        if parts[:half] == parts[half:]:
            rest = " ".join(parts[:half])
    return printed_no, rarity, rest


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for a in soup.find_all("a", href=True):
        m = LINK_RE.match(a["href"])
        if not m:
            continue
        set_seg, card_id = m.groups()

        parsed_name = _parse_link_text(a.get_text(" ", strip=True))
        if not parsed_name:
            continue
        printed_no, rarity, name = parsed_name

        price = None
        container = a.find_parent(["li", "tr", "div"]) or a.parent
        if container is not None:
            price = parse_price(container.get_text(" ", strip=True))
        if price is None:
            node = a.find_next(string=re.compile("円"))
            for _ in range(4):
                if node is None:
                    break
                price = parse_price(str(node))
                if price is not None:
                    break
                node = node.find_next(string=re.compile("円"))
        if price is None:
            continue

        set_code = f"{set_seg}-{printed_no}"
        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(name, set_code, rarity, buy_price, sell_price, source_site, fetched_at))

    return records

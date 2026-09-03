from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional, List, Dict

from bs4 import BeautifulSoup

PRICE_RE = re.compile(r"([\d,]{2,})\s*円")
# 例: sv08-132/106 のような型番、または末尾に printedNo/total が付くパターン
SET_CODE_RE = re.compile(r"\b([A-Za-z]{1,4}\d{1,3}[A-Za-z]{0,2})[-\s]?(\d{1,3}/\d{1,3})\b")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_price(text: str) -> Optional[int]:
    m = PRICE_RE.search(text)
    if not m:
        return None
    return int(m.group(1).replace(",", ""))


def make_record(
    card_name: str,
    set_code: Optional[str],
    rarity: Optional[str],
    buy_price: Optional[int],
    sell_price: Optional[int],
    source_site: str,
    fetched_at: Optional[str] = None,
) -> Dict:
    return {
        "card_name": card_name,
        "set_code": set_code,
        "rarity": rarity,
        "buy_price": buy_price,
        "sell_price": sell_price,
        "source_site": source_site,
        "fetched_at": fetched_at or now_iso(),
    }


def generic_text_list_parse(html: str, source_site: str, direction: str) -> List[Dict]:
    """汎用フォールバックパーサー。

    HTMLをテキスト化して行に分解し、「◯◯円」を含む行を価格行とみなして
    直前の非空行をカード名候補として組み合わせる。CSSクラス名に依存しない分
    壊れにくいが、精度は専用パーサーに劣る。実際のサイト構造が判明したら
    ショップ別の専用パーサーに置き換えること。
    """
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    lines = [line.strip() for line in soup.get_text("\n").splitlines()]
    lines = [line for line in lines if line]

    records: List[Dict] = []
    fetched_at = now_iso()
    for i, line in enumerate(lines):
        price = parse_price(line)
        if price is None:
            continue

        name = None
        for back in range(1, 4):
            j = i - back
            if j < 0:
                break
            candidate = lines[j]
            if parse_price(candidate) is not None:
                continue
            if len(candidate) < 2:
                continue
            name = candidate
            break
        if not name:
            continue

        m = SET_CODE_RE.search(name) or SET_CODE_RE.search(line)
        set_code = f"{m.group(1)}-{m.group(2)}" if m else None

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(name, set_code, None, buy_price, sell_price, source_site, fetched_at))
    return records

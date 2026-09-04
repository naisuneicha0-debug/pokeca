"""スニーカーダンク用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。CSS
Modulesのハッシュ付きクラス名(ビルドごとに変わりうる)を避け、
`<a href="/apparels/...">`のaria-label属性
(例: "メガリザードンXex MA [M2a 223/193](ハイクラスパック「MEGAドリームex」) - ¥3,300")
から直接カード名・型番・価格を抽出する。50件確認済み(フリマ型の出品
ベースの相場のため、通販サイトと同様sellとして扱う)。
"""
from __future__ import annotations

import re
from typing import List, Dict

from bs4 import BeautifulSoup

from .base import make_record, now_iso

LABEL_RE = re.compile(r"^(.*?)\s*-\s*¥([\d,]+)$")
CODE_RE = re.compile(r"\[([^\]]+)\]")


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for a in soup.find_all("a", attrs={"aria-label": True}):
        href = a.get("href", "")
        if "/apparels/" not in href:
            continue
        label = a["aria-label"]
        m = LABEL_RE.match(label)
        if not m:
            continue
        name_part, price_text = m.group(1), m.group(2)
        price = int(price_text.replace(",", ""))

        code_m = CODE_RE.search(name_part)
        set_code = code_m.group(1) if code_m else None
        card_name = CODE_RE.sub("", name_part).strip()

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, set_code, None, buy_price, sell_price, source_site, fetched_at))

    return records

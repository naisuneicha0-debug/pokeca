"""古本市場(ふるいち)用パーサー(買取価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-03)。ページ
ビルダー(.cp-brand_item)のブロック単位でカード名/型番/レアリティ/価格が
構造化されている。価格は「¥25」「,000」のように¥記号とカンマ区切り数字が
別テキストノードに分かれているため、base.pyの円ベースparse_priceは使えず、
ブロック全体のテキストから¥記号ベースで抽出する。
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

    for item in soup.select(".cp-brand_item"):
        titles = [t.get_text(" ", strip=True) for t in item.select(".cp-brand_item-title")]
        titles = [t for t in titles if t]
        if not titles:
            continue
        card_name = titles[0]
        set_code = titles[1] if len(titles) > 1 else None
        rarity = titles[2] if len(titles) > 2 else None

        price_el = item.select_one(".cp-brand_item-grid-text")
        if price_el is None:
            continue
        # 「¥25」「,000」のように¥記号と桁区切り部分が別ノードに分かれている
        # ため、get_textの区切り文字を空にして連結してから抽出する。
        m = PRICE_RE.search(price_el.get_text("", strip=True))
        if not m:
            continue
        price = int(m.group(1).replace(",", ""))

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, set_code, rarity, buy_price, sell_price, source_site, fetched_at))

    return records

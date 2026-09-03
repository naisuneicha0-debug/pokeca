"""カードラッシュ・カードラボ共通パーサー。

両サイトとも同じECカートシステムのテンプレートを使っており、商品リストの
DOM構造(a.item_data_link > .goods_name / .price .figure)がほぼ同一。
デバッグ用HTML取得(debug_fetch)で実構造を確認済み。
"""
from __future__ import annotations

import re
from typing import List, Dict, Optional, Tuple

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price

RARITY_RE = re.compile(r"【([^】]*)】")
PRINTED_RE = re.compile(r"(\d{1,4}/[\w\-]+)")


def _parse_goods_name(raw: str) -> Tuple[str, Optional[str], Optional[str]]:
    rarities = RARITY_RE.findall(raw)
    # レアリティは末尾の【】に入っていることが多い(例: 【ポケカ】名前【-】PROMO 235/S-P)。
    # 先頭の【ポケカ】のようなカテゴリタグと紛れるため、必ず最後の1つだけを見る。
    # "-" はレアリティ無し(ノーマル等)を表す明示的な値のため、その場合は他の
    # 括弧にフォールバックせずNoneにする。
    rarity = rarities[-1] if rarities else None
    if rarity == "-":
        rarity = None

    m = PRINTED_RE.search(raw)
    printed = m.group(1) if m else None

    cleaned = raw.replace("☆SALE☆", "")
    cleaned = RARITY_RE.sub("", cleaned)
    if printed:
        cleaned = re.sub(r"[\{\(]?" + re.escape(printed) + r"[\}\)]?", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned, rarity, printed


def parse_ec_platform(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for link in soup.select("a.item_data_link"):
        name_el = link.select_one(".goods_name")
        if not name_el:
            continue
        raw_name = name_el.get_text(" ", strip=True)

        price_el = link.select_one(".price .figure") or link.select_one(".selling_price .figure")
        if not price_el:
            continue
        # c_laboは "180<span>円</span>" のように円がネストしている場合があるため
        # get_text側で結合してから解析する(カードラッシュは "280円" のフラット構造)。
        price = parse_price(price_el.get_text(" ", strip=True))
        if price is None:
            continue

        card_name, rarity, printed = _parse_goods_name(raw_name)
        if not card_name:
            continue

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(card_name, printed, rarity, buy_price, sell_price, source_site, fetched_at))

    return records

"""晴れる屋2用パーサー(買取価格)。

以下は、旧URL(buying-listページ、Playwrightでレンダリング後のHTML)向けに
実装したロジック。ページ内JSに全商品データの取得元として公開JSON API
(https://api.corp.hareruyamtg.com/user_data/hareruya2/json/products_all.json)
が埋め込まれているのを発見したため、config.pyのbuy_urlはそちらに切り替え
済み。JSON構造はまだ未確認のため、このパーサーはまだJSON向けに書き換えて
いない(現状は非HTML入力に対して黙って空リストを返すだけ)。次のステップは
実際のJSONレスポンスを確認し、このパーサーをJSON用に全面的に書き換えること。

以下のHTML用ロジックはページ内リンク経由で再度使う可能性を考え参考として残す:
`<li><div class="product-title">名前(レアリティ){エネルギー}〈printed〉[set]
</div>...<span class="buy">¥価格</span></li>` という構造の商品リスト
(50件/ページ、確認時点で全8,785件のページネーションあり)。
"""
from __future__ import annotations

import re
from typing import List, Dict, Optional, Tuple

from bs4 import BeautifulSoup

from .base import make_record, now_iso, parse_price

TITLE_RE = re.compile(
    r"^(?P<name>.+?)\((?P<rarity>[^)]+)\)(?:\{[^}]*\})?"
    r"(?:〈(?P<printed>[^〉]+)〉)?(?:\[(?P<set>[^\]]+)\])?$"
)


def _parse_title(raw: str) -> Tuple[str, Optional[str], Optional[str]]:
    raw = raw.strip()
    m = TITLE_RE.match(raw)
    if not m:
        return raw, None, None
    name = m.group("name").strip()
    rarity = m.group("rarity")
    printed = m.group("printed")
    set_seg = m.group("set")
    set_code = f"{set_seg}-{printed}" if set_seg and printed else (printed or set_seg)
    return name, rarity, set_code


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    fetched_at = now_iso()
    records: List[Dict] = []

    for li in soup.select("ul#productList > li"):
        title_el = li.select_one(".product-title")
        price_el = li.select_one(".price-row .buy")
        if not title_el or not price_el:
            continue

        price = parse_price(price_el.get_text(" ", strip=True).replace("¥", "") + "円")
        if price is None:
            continue

        name, rarity, set_code = _parse_title(title_el.get_text(" ", strip=True))
        if not name:
            continue

        buy_price = price if direction == "buy" else None
        sell_price = price if direction == "sell" else None
        records.append(make_record(name, set_code, rarity, buy_price, sell_price, source_site, fetched_at))

    return records

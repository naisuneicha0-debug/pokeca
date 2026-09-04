"""トレカジパング用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み(2026-09-04)。
トレカキャンプ(toreca_camp)と同じShopifyテーマ(.product-item構造)を
使っているため、そちらのパーサーをそのまま再利用する。
"""
from typing import List, Dict

from .toreca_camp import parse as _parse


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    return _parse(html, source_site, direction)

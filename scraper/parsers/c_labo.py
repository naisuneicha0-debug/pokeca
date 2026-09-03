"""カードラボ用パーサー(販売価格のみ)。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み。カードラッシュと
同じECカートシステムのテンプレートのため、共通実装(ec_common)を使う。
"""
from typing import List, Dict

from .ec_common import parse_ec_platform


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    return parse_ec_platform(html, source_site, direction)

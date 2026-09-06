"""X(Twitter)検証用パーサー(技術検証のみ)。

実サイトのHTML構造が未検証のため、汎用テキストパターンマッチ
(generic_text_list_parse)を暫定使用している。
"""
from typing import List, Dict

from .base import generic_text_list_parse


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    return generic_text_list_parse(html, source_site, direction)

"""hobbystation_single用パーサー(販売価格のみ)。

実サイトのHTML構造が未検証のため、汎用テキストパターンマッチ
(generic_text_list_parse)を暫定使用している。GitHub Actions実行後の
ログ・取得結果を見て、専用のセレクタベース実装に置き換えること。
"""
from typing import List, Dict

from .base import generic_text_list_parse


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    return generic_text_list_parse(html, source_site, direction)

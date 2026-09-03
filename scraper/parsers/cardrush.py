"""カードラッシュ用パーサー。

デバッグ用HTML取得(debug_fetch)で実構造を確認済み。カードラボと同じ
ECカートシステムのテンプレートのため、共通実装(ec_common)を使う。

注意: 買取URL(https://cardrush.media/pokemon/buying_prices)は本番run時に
403 Forbiddenで拒否されている。別ドメイン(cardrush.media)側でbot対策が
入っている可能性があり、要調査(URL自体の見直しも含む)。
販売URL側(www.cardrush-pokemon.jp)はトップページのため、商品一覧の一部
しか拾えていない可能性が高い。本来の全カード一覧ページ(カテゴリ別など)の
URLへの差し替えが望ましい。
"""
from typing import List, Dict

from .ec_common import parse_ec_platform


def parse(html: str, source_site: str, direction: str) -> List[Dict]:
    return parse_ec_platform(html, source_site, direction)

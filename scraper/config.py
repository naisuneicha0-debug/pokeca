from dataclasses import dataclass
from typing import Optional, List

# ロードマップ ステップ2「高額カード優先」の基準
HIGH_VALUE_THRESHOLD = 500_000


@dataclass(frozen=True)
class ShopConfig:
    shop_id: str
    shop_name: str
    buy_url: Optional[str]
    sell_url: Optional[str]
    shop_type: str  # "buy_only" / "sell_only" / "both"
    parser: str  # scraper.parsers.<parser> の parse() を呼ぶ


# 注意: 以下URLはネットワーク制限下(egress遮断)で実サイトにアクセスできないまま
# 引き継ぎ資料の記載を元に設定したもの。「TODO要検証」の付いた項目は
# GitHub Actions実行時のログ・取得結果を見ながら実URL・実構造に合わせて修正が必要。
SHOPS: List[ShopConfig] = [
    ShopConfig(
        shop_id="yuyu_tei",
        shop_name="遊々亭",
        buy_url="https://yuyu-tei.jp/buy/poc/list",  # TODO要検証: 一覧URLの実際のパス・クエリ
        sell_url="https://yuyu-tei.jp/sell/poc/list",  # TODO要検証
        shop_type="both",
        parser="yuyu_tei",
    ),
    ShopConfig(
        shop_id="cardrush",
        shop_name="カードラッシュ",
        buy_url="https://cardrush.media/pokemon/buying_prices",
        sell_url="https://www.cardrush-pokemon.jp/",  # TODO要検証: トップページの可能性が高く、実際の価格一覧ページに要修正
        shop_type="both",
        parser="cardrush",
    ),
    ShopConfig(
        shop_id="c_labo",
        shop_name="カードラボ",
        buy_url=None,  # TODO要確認: 買取価格ページが別途存在するか要調査
        sell_url="https://www.c-labo-online.jp/product-group/2413",
        shop_type="sell_only",
        parser="c_labo",
    ),
    ShopConfig(
        shop_id="hareruya2",
        shop_name="晴れる屋2",
        buy_url="https://www.hareruya2.com/",  # TODO要検証: 引き継ぎ資料でURL末尾が省略されていた
        sell_url=None,  # TODO要確認: 販売価格ページのURLが不明
        shop_type="buy_only",
        parser="hareruya2",
    ),
    ShopConfig(
        shop_id="toretoku",
        shop_name="トレトク",
        buy_url="https://kaitori-toretoku.jp/buypricelist/pokemon",
        sell_url=None,
        shop_type="buy_only",
        parser="toretoku",
    ),
    ShopConfig(
        shop_id="fullcomp",
        shop_name="フルコンプ秋葉原店",
        buy_url="https://www.fullcomp.jp/akihabara/kaitori/19879",
        sell_url=None,
        shop_type="buy_only",
        parser="fullcomp",
    ),
    ShopConfig(
        shop_id="kaitori_collector",
        shop_name="買取コレクター",
        buy_url="https://kaitoricollector.com/card-kind/pokemoncard/price/",
        sell_url=None,
        shop_type="buy_only",
        parser="kaitori_collector",
    ),
    ShopConfig(
        shop_id="nin_nin",
        shop_name="ニンニン",
        buy_url="https://nin-nin-pokeka.jp/kakaku/tcg/pokemon/",
        sell_url=None,  # TODO要確認: 同一ページ内に販売価格が併記されている可能性あり
        shop_type="buy_only",
        parser="nin_nin",
    ),
]

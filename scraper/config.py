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


# GitHub Actionsのdebug_fetch_html.ymlで実HTMLを取得・確認しながら調整中。
# 各エントリのコメントに現状の検証状況を残す。
SHOPS: List[ShopConfig] = [
    ShopConfig(
        shop_id="yuyu_tei",
        shop_name="遊々亭",
        # buy/sellとも403 Forbiddenで拒否される(2026-09-03確認)。bot対策か
        # URL自体の誤りの可能性があり、実HTMLが取得できておらず未解決。
        buy_url="https://yuyu-tei.jp/buy/poc/list",  # TODO要検証
        sell_url="https://yuyu-tei.jp/sell/poc/list",  # TODO要検証
        shop_type="both",
        parser="yuyu_tei",
    ),
    ShopConfig(
        shop_id="cardrush",
        shop_name="カードラッシュ",
        # buy_url(cardrush.media)は403 Forbidden(2026-09-03確認)、要調査。
        # sell_url(トップページ)は取得できており、カードラボと同じECテンプレート
        # 用の専用パーサー(ec_common)で実データが抽出できることを確認済み。
        # ただしトップページのため一部しか拾えておらず、本来の全カード一覧
        # ページのURLへの差し替えが望ましい。
        buy_url="https://cardrush.media/pokemon/buying_prices",  # TODO要検証
        sell_url="https://www.cardrush-pokemon.jp/",  # TODO要検証: トップページの一部のみ
        shop_type="both",
        parser="cardrush",
    ),
    ShopConfig(
        shop_id="c_labo",
        shop_name="カードラボ",
        buy_url=None,  # TODO要確認: 買取価格ページが別途存在するか要調査
        # sell_urlは専用パーサー(ec_common、カードラッシュと共通)で実データ
        # 抽出できることを確認済み(2026-09-03)。
        sell_url="https://www.c-labo-online.jp/product-group/2413",
        shop_type="sell_only",
        parser="c_labo",
    ),
    ShopConfig(
        shop_id="hareruya2",
        shop_name="晴れる屋2",
        # ShopifyベースのECサイトのトップページになっており、買取価格の
        # 一覧ページではないことを実HTMLで確認済み(2026-09-03)。正しい
        # 買取ページURLの特定が必要。
        buy_url="https://www.hareruya2.com/",  # TODO要検証
        sell_url=None,  # TODO要確認: 販売価格ページのURLが不明
        shop_type="buy_only",
        parser="hareruya2",
    ),
    ShopConfig(
        shop_id="toretoku",
        shop_name="トレトク",
        # 実HTML確認済み(2026-09-03)。data-name/data-price等の属性を持つ
        # <li>要素から専用パーサーで実データ329件抽出できることを確認。
        buy_url="https://kaitori-toretoku.jp/buypricelist/pokemon",
        sell_url=None,
        shop_type="buy_only",
        parser="toretoku",
    ),
    ShopConfig(
        shop_id="fullcomp",
        shop_name="フルコンプ秋葉原店",
        # 実HTML確認済み(2026-09-03)。ページ内のvar tableData=[...]という
        # JS配列から専用パーサーで実データ5267件抽出できることを確認。
        buy_url="https://www.fullcomp.jp/akihabara/kaitori/19879",
        sell_url=None,
        shop_type="buy_only",
        parser="fullcomp",
    ),
    ShopConfig(
        shop_id="kaitori_collector",
        shop_name="買取コレクター",
        # 初回scrape.yml実行では79件取得できたが中身は「買取価格」等の見出し
        # ラベルを拾っただけでカード名になっていなかった。debug_fetch実行時は
        # 接続タイムアウトで再現できず、実HTML構造が未確認のまま。要再調査。
        buy_url="https://kaitoricollector.com/card-kind/pokemoncard/price/",  # TODO要検証
        sell_url=None,
        shop_type="buy_only",
        parser="kaitori_collector",
    ),
    ShopConfig(
        shop_id="nin_nin",
        shop_name="ニンニン",
        # 実HTML確認済み(2026-09-03)。このURLは価格表そのものではなく、
        # BW/XY・GX SA・SS以降HR/SAR等のカテゴリへのリンク一覧(index)ページ
        # だった。実データを取るには各カテゴリのサブページURLを個別に
        # 巡回する実装への変更が必要。
        buy_url="https://nin-nin-pokeka.jp/kakaku/tcg/pokemon/",  # TODO要修正: カテゴリindexページ
        sell_url=None,
        shop_type="buy_only",
        parser="nin_nin",
    ),
]

from dataclasses import dataclass
from typing import Optional, List

# 収集対象は50万円以上のみ(上限なし)。買取・売値どちらかがこの金額以上なら残す。
HIGH_VALUE_THRESHOLD = 500_000


@dataclass(frozen=True)
class ShopConfig:
    shop_id: str
    shop_name: str
    buy_url: Optional[str]  # shops.json表示用の代表URL
    sell_url: Optional[str]
    shop_type: str  # "buy_only" / "sell_only" / "both"
    parser: str  # scraper.parsers.<parser> の parse() を呼ぶ
    # 実際に巡回するURL群。カテゴリ別に複数ページある場合はここに列挙する。
    # 指定が無ければ buy_url/sell_url を単独のURLとして使う。
    buy_urls: Optional[List[str]] = None
    sell_urls: Optional[List[str]] = None
    # True の場合、requestsではなくheadless browser(Playwright)でJS
    # レンダリング後のHTMLを取得する(クライアントサイドJSで価格表を
    # 描画するサイト向け)。
    render_js: bool = False


def get_urls(shop: ShopConfig, direction: str) -> List[str]:
    if direction == "buy":
        if shop.buy_urls:
            return shop.buy_urls
        return [shop.buy_url] if shop.buy_url else []
    if shop.sell_urls:
        return shop.sell_urls
    return [shop.sell_url] if shop.sell_url else []


# ニンニンの買取価格表はカテゴリ別のサブページに分かれている(index.htmlは
# 各カテゴリへのリンク一覧に過ぎない)。debug_fetch_html.ymlで実HTMLを確認し
# 判明したサブページURL一覧。
_NIN_NIN_CATEGORY_URLS = [
    "https://nin-nin-pokeka.jp/kakaku/bw-xy/",
    "https://nin-nin-pokeka.jp/kakaku/gx%e3%80%80sar/",
    "https://nin-nin-pokeka.jp/kakaku/ss%e4%bb%a5%e9%99%8d%e3%83%9d%e3%82%b1%e3%83%a2%e3%83%b3hr%e3%80%81sar/",
    "https://nin-nin-pokeka.jp/kakaku/sm%e4%bb%a5%e9%99%8d%e3%82%b5%e3%83%9d%e3%83%bc%e3%83%88sr%e3%80%81sar/",
    "https://nin-nin-pokeka.jp/kakaku/%e3%83%97%e3%83%ad%e3%83%a2/",
    "https://nin-nin-pokeka.jp/kakaku/%e3%82%ab%e3%83%bc%e3%83%89%e3%83%80%e3%82%b9/",
    "https://nin-nin-pokeka.jp/kakaku/%e3%83%88%e3%83%83%e3%83%97%e3%82%b5%e3%83%b3/",
    "https://nin-nin-pokeka.jp/kakaku/cp%e3%82%b7%e3%83%aa%e3%83%bc%e3%82%ba%e3%83%bbsc/",
    "https://nin-nin-pokeka.jp/kakaku/%e3%83%ac%e3%82%b8%e3%82%a7%e3%83%b3%e3%83%89%e3%83%bb%e3%82%b0%e3%83%ac%e3%83%bc%e3%83%88/",
    "https://nin-nin-pokeka.jp/kakaku/lv-x/",
    "https://nin-nin-pokeka.jp/kakaku/ex%e3%82%b7%e3%83%aa%e3%83%bc%e3%82%ba%e3%83%bb%e3%83%87%e3%83%ab%e3%82%bf%e7%a8%ae%e3%83%bb%e3%82%b9%e3%82%bf%e3%83%bc/",
    "https://nin-nin-pokeka.jp/kakaku/web-vs/",
    "https://nin-nin-pokeka.jp/kakaku/e%e3%82%ab%e3%83%bc%e3%83%89/",
    "https://nin-nin-pokeka.jp/kakaku/%e6%97%a7%e8%a3%8f/",
]

# GitHub Actionsのdebug_fetch_html.ymlで実HTMLを取得・確認しながら調整中。
# 各エントリのコメントに現状の検証状況を残す。
SHOPS: List[ShopConfig] = [
    ShopConfig(
        shop_id="yuyu_tei",
        shop_name="遊々亭",
        # buy/sellとも403 Forbiddenで拒否される(2026-09-03確認、標準的な
        # Accept/Accept-Languageヘッダーを付けても変化なし)。bot対策による
        # 明確な自動アクセス拒否と判断し、対象から除外(buy_url/sell_urlを
        # None化)。ヘッダー偽装等でのすり抜けは意図的に行わない。
        buy_url=None,
        sell_url=None,
        shop_type="both",
        parser="yuyu_tei",
    ),
    ShopConfig(
        shop_id="cardrush",
        shop_name="カードラッシュ",
        # buy_url(cardrush.media)は403 Forbidden(2026-09-03確認、ヘッダー
        # 改善後も変化なし)。bot対策による拒否と判断し除外(None化)。
        # sell_url(トップページ)は取得できており、カードラボと同じEC
        # テンプレート用の専用パーサー(ec_common)で実データ抽出を確認済み。
        # ただしトップページのため一部しか拾えておらず、本来の全カード
        # 一覧ページのURLへの差し替えが望ましい。
        buy_url=None,
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
        # buying-listページ(Playwrightでレンダリング確認済み、2026-09-03)の
        # JS内に全商品データの取得元として
        # https://api.corp.hareruyamtg.com/user_data/hareruya2/json/products_all.json
        # という公開JSON APIのURLが埋め込まれているのを発見した。全8,785件
        # (確認時点)を1回のリクエストで取得できるため、Playwright(render_js)
        # ではなくrequestsで直接このJSONを取得する方式に切り替えた。
        # JSON構造は未確認のため、専用パーサーは実際のレスポンスを見てから実装する。
        buy_url="https://api.corp.hareruyamtg.com/user_data/hareruya2/json/products_all.json",  # TODO要検証: JSON構造を確認しパーサー実装
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
        # 実HTML確認済み(2026-09-03)。ただしこのページは全カード網羅の
        # 価格表ではなく、ジャンル横断(玩具・フィギュア等含む)の「買取実績
        # ハイライト」カルーセルだった。リンク先が/card-kind/pokemoncard/の
        # ものだけに絞る専用パーサーで、実在するポケカの買取実績9件を確認。
        # 件数は少ないが実データ(価格非公開の実績は除外済み)。
        buy_url="https://kaitoricollector.com/card-kind/pokemoncard/price/",
        sell_url=None,
        shop_type="buy_only",
        parser="kaitori_collector",
    ),
    ShopConfig(
        shop_id="nin_nin",
        shop_name="ニンニン",
        # indexページ(buy_url)はカテゴリへのリンク一覧に過ぎないことを実HTMLで
        # 確認済み(2026-09-03)。buy_urlsに列挙した各カテゴリのサブページも
        # 確認したが、価格情報はテキストではなく買取表を撮影した画像
        # (JPG/PNG)として掲載されており、通常のスクレイピングでは取得
        # 不可能と判明。OCR実装が必要なため今回は未対応。
        buy_url="https://nin-nin-pokeka.jp/kakaku/tcg/pokemon/",
        buy_urls=_NIN_NIN_CATEGORY_URLS,
        sell_url=None,
        shop_type="buy_only",
        parser="nin_nin",
    ),
    ShopConfig(
        shop_id="suruga_ya",
        shop_name="駿河屋",
        # Web検索で追加(2026-09-03)。403 Forbiddenで拒否される
        # (ヘッダー改善後も変化なし)。bot対策による明確な拒否と判断し
        # 除外(None化)。
        buy_url=None,
        sell_url=None,
        shop_type="buy_only",
        parser="suruga_ya",
    ),
    ShopConfig(
        shop_id="netoff_moetaku",
        shop_name="ネットオフ もえたく!",
        # Web検索で追加(2026-09-03)。ランディングページ・検索結果ページ
        # ともJSレンダリング後も個別カードの価格表は見つからず、ページ内の
        # 「円」表記は全てYotpoのお客様レビュー本文(お礼コメント中の
        # 「計7点で107,300円のお買取り」のような合計額の言及)だった。
        # このショップは静的な価格一覧を公開しておらず、実際の査定は
        # 「AIがカード写真から査定」等インタラクティブな機能のみと判断。
        # スクレイピング可能な価格表が存在しないため対象除外(None化)。
        buy_url=None,
        sell_url=None,
        shop_type="buy_only",
        parser="netoff_moetaku",
    ),
]

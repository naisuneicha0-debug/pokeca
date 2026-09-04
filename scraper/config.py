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
        # 改善後も変化なし)。2026-09-04にクエリパラメータ付きの詳細URL
        # (ソート・絞り込み条件付き)で再検証したが、やはり403 Forbiddenで
        # 拒否された。bot対策による明確な拒否と判断し、これ以上の再検証は
        # 行わず対象除外(None化)を確定する。
        # 2026-09-03 WebSearchで、同じcardrush-pokemon.jpドメイン内に
        # 「買取リスト」ページ群(/page/38,39,40,41,42,45)を発見したが、
        # 価格表自体はページ内に無くGoogleスプレッドシートの公開ビュー
        # (pubhtml)をiframe埋め込みしている構造だった(/page/40のみ注意事項
        # のみで対象外)。pubhtmlはJSレンダリング必須で静的取得不可、CSV
        # エクスポート(/pub?output=csv)なら静的取得はできたものの、中身が
        # 全シート"#REF!"エラーまたは「只今準備中です」で実データが入って
        # いなかった(2026-09-03、シート自体が壊れている/未整備と判断)。
        # 買取側はこれ以上の対応方法が無いため対象外とし、sell_urlのみ運用。
        buy_url=None,
        sell_url="https://www.cardrush-pokemon.jp/",  # TODO要検証: トップページの一部のみ
        shop_type="both",
        parser="cardrush",
    ),
    ShopConfig(
        shop_id="c_labo",
        shop_name="カードラボ",
        # 2026-09-03 WebSearchで、通販サイト(c-labo-online.jp)とは別ドメインの
        # 買取専用サイト(c-labo-kaitori.jp)を発見。debug_fetchで実HTML確認済み:
        # /page/10はカテゴリ一覧(シリーズ別リンク集)のみで価格情報は無かった。
        # リンク先が/product-group/<id>で通販サイトと同じOCNKベースのURL体系
        # だったため、「人気高レアリティ一覧」(product-group/341)に変更し
        # 実データ35件抽出できることを確認済み(2026-09-03、既存の
        # ec_commonパーサーがそのまま使えた)。
        buy_url="https://www.c-labo-kaitori.jp/product-group/341",
        # sell_urlは専用パーサー(ec_common、カードラッシュと共通)で実データ
        # 抽出できることを確認済み(2026-09-03)。
        sell_url="https://www.c-labo-online.jp/product-group/2413",
        shop_type="both",
        parser="c_labo",
    ),
    ShopConfig(
        shop_id="hareruya2",
        shop_name="晴れる屋2",
        # buying-listページのJS内に全商品データの取得元として
        # https://api.corp.hareruyamtg.com/user_data/hareruya2/json/products_all.json
        # という公開JSON APIのURLが埋め込まれているのを発見した。実際に取得・
        # パース確認済み(2026-09-03): {"count": int, "products": [...]}形式で、
        # 各productにbuy_price/sell_priceが両方含まれる。22,645件中43件が
        # 50万円以上。1回のリクエストで買取・売値どちらも取れるため、
        # sell_urlは設定せずbuy_url一本(パーサー内でdirectionを無視し両方
        # 出力)にしている。
        buy_url="https://api.corp.hareruyamtg.com/user_data/hareruya2/json/products_all.json",
        sell_url=None,
        shop_type="both",
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
        shop_id="dorasuta",
        shop_name="ドラゴンスター(ネット買取)",
        # WebSearchで発見(2026-09-03)。debug_fetchで実アクセスした結果
        # 403 Forbiddenで拒否された。他の除外ショップ同様、bot対策による
        # 明確な拒否と判断しヘッダー偽装等での回避は行わず除外(None化)。
        buy_url=None,
        sell_url=None,
        shop_type="buy_only",
        parser="dorasuta",
    ),
    ShopConfig(
        shop_id="ka_nabell",
        shop_name="カーナベル",
        # WebSearchで発見(2026-09-03)。debug_fetchで実アクセスした結果
        # 403 Forbiddenで拒否された。他の除外ショップ同様、bot対策による
        # 明確な拒否と判断しヘッダー偽装等での回避は行わず除外(None化)。
        buy_url=None,
        sell_url=None,
        shop_type="buy_only",
        parser="ka_nabell",
    ),
    ShopConfig(
        shop_id="hbst",
        shop_name="ホビーステーション",
        # WebSearchで発見(2026-09-03)。debug_fetchで実HTML確認済み: 403等の
        # 拒否はされないが、「高価買取リスト」検索フォーム(purchase/)の
        # game選択肢にウィクロス/ヴァイス/Z-X/MTG/DM/遊戯王のみが並び、
        # ポケモンカードの選択肢が無かった。買取ページ本体(/selling/)も
        # 確認したがポケモンカードへの導線が無かった。店舗ブログ記事
        # (?p=...)個別に買取表が掲載されている可能性はあるが、体系的な
        # 一覧ページが見つからないため対象除外(None化)。
        buy_url=None,
        sell_url=None,
        shop_type="buy_only",
        parser="hbst",
    ),
    ShopConfig(
        shop_id="furuichi",
        shop_name="古本市場(ふるいち)",
        # WebSearchで発見(2026-09-03)。debug_fetchで実HTML確認・専用パーサー
        # (.cp-brand_itemブロック単位)で実データ抽出できることを確認済み
        # (2026-09-03、6件)。ただし掲載されているのは「ポケカ買取特選タイトル」
        # というハイライトのみで、最高額でも25,000円程度とHIGH_VALUE_THRESHOLD
        # (50万円)には遠く及ばない。全カード網羅の一覧ページは見つかって
        # いない(店舗持ち込みのみ対応で宅配・ネット買取非対応のショップ)。
        buy_url="https://www.furu1.net/kaitori/sell_toreca/pk",
        sell_url=None,
        shop_type="buy_only",
        parser="furuichi",
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
    ShopConfig(
        shop_id="pokeking",
        shop_name="ポケキング",
        # WebSearchで発見(2026-09-04)。debug_fetchで実HTML確認済み:
        # WordPressブロックエディタのdiv.wp-block-column単位でカード名・
        # 型番・買取価格が構造化されている。実データ9件抽出できることを
        # 確認済み(ピックアップ商品のみで全カード網羅ではない)。
        buy_url="https://pokeking.sangatuusagi.com/card/",
        sell_url=None,
        shop_type="buy_only",
        parser="pokeking",
    ),
    ShopConfig(
        shop_id="toysking",
        shop_name="トイズキング",
        # WebSearchで発見(2026-09-04)。debug_fetchで実HTML確認済み: 買取
        # 価格表は別ドメイン(kakaku.yamato-gp.net)の価格表一覧ページに
        # あり、そこから「ポケモンカード買取価格表」のリンク先として、
        # S3上に直接公開されているJSON
        # (https://manage-s3.s3.amazonaws.com/static/dist/pricelist/toysking/toysking/pokeca.json)
        # を発見した(hareruya2と同様のパターン)。静的取得でき実データ3件
        # 抽出できることを確認済み(2026-09-04。ページあたりの件数が
        # 少なくピックアップ商品のみと思われる)。
        buy_url="https://manage-s3.s3.amazonaws.com/static/dist/pricelist/toysking/toysking/pokeca.json",
        sell_url=None,
        shop_type="buy_only",
        parser="toysking",
    ),
    ShopConfig(
        shop_id="otakarasouko",
        shop_name="お宝創庫",
        # WebSearchで発見(2026-09-04)。debug_fetchで実HTML確認済み:
        # ul.bl_product単位で商品(全ジャンル混在)が構造化されており、
        # カテゴリーに「ポケモン」を含むものだけ抽出して実データ1,934件
        # 抽出できることを確認済み。うち5件が50万円以上(最高180万円)と、
        # 高額カードの収集元として非常に有力。
        buy_url="https://www.otakarasouko.com/pokemoncard/",
        sell_url=None,
        shop_type="buy_only",
        parser="otakarasouko",
    ),
    ShopConfig(
        shop_id="clove_base",
        shop_name="Clove Base",
        # WebSearchで発見(2026-09-04)。店舗買取の価格表ページ。debug_fetchで
        # 2回アクセスしたがいずれも429 Too Many Requestsで拒否された。他の
        # ショップへのリクエストの合間の単発アクセスでも継続して429になる
        # ため、レート制限が厳しいサイトと判断。しばらく間隔を空けて再検証
        # する余地はあるが、現時点では未解決のまま保留。
        buy_url="https://base.clove.jp/prices/pokemon",
        sell_url=None,
        shop_type="buy_only",
        parser="clove_base",
    ),
    ShopConfig(
        shop_id="t_machine",
        shop_name="たいむましん",
        # WebSearchで発見(2026-09-04)。旧裏面(絶版・初期カード)専門の買取
        # 価格表。debug_fetchで実HTML確認済み: table#tbl_modern内の
        # tr.pokemon行で実データ94件抽出できることを確認済み(最高16万円。
        # 50万円には届かないが実データとしては有用)。
        buy_url="https://t-machine.jp/tradingcard/pokemon/fd/",
        sell_url=None,
        shop_type="buy_only",
        parser="t_machine",
    ),
    ShopConfig(
        shop_id="otachu",
        shop_name="オタチュウ",
        # WebSearchで発見(2026-09-04)。PSA10鑑定品専門の買取価格表。
        # debug_fetchで実HTML確認済み: シリーズ別に複数のtable要素
        # ([No./レア/カード名/買取金額/更新]の5列)があり、実データ872件
        # 抽出できることを確認済み。うち20件が50万円以上(最高220万円)と
        # 高額カードの収集元として非常に有力(お宝創庫に次ぐ収穫)。
        buy_url="https://otachu-akiba.com/1gocard/buying_price/psa-pokemon-cards/",
        sell_url=None,
        shop_type="buy_only",
        parser="otachu",
    ),
    ShopConfig(
        shop_id="fukufuku_toreca",
        shop_name="福福トレカ",
        # WebSearchで発見(2026-09-04)。debug_fetchで実HTML確認済み:
        # .card-item単位で商品(カード名・型番・レアリティ・価格)が構造化
        # されており、実データ64件抽出できることを確認済み。
        buy_url=None,
        sell_url="https://pokemon.fukufukutoreka.com/",
        shop_type="sell_only",
        parser="fukufuku_toreca",
    ),
    ShopConfig(
        shop_id="toreca_zipangu",
        shop_name="トレカジパング",
        # WebSearchで発見(2026-09-04)。debug_fetchで実HTML確認済み:
        # トップページ(Shopify製ストア)には商品一覧が無かったため、
        # Shopify標準の全商品一覧URL(/collections/all)に変更したところ、
        # トレカキャンプと同じShopifyテーマ構造(.product-item)で実データ
        # 24件抽出できることを確認済み(パーサーはtoreca_campを再利用)。
        buy_url=None,
        sell_url="https://tracazipangu.com/collections/all",
        shop_type="sell_only",
        parser="toreca_zipangu",
    ),
    ShopConfig(
        shop_id="torema",
        shop_name="トレマ",
        # WebSearchで発見(2026-09-04)。debug_fetchで実アクセスした結果
        # 403 Forbiddenで拒否された。他の除外ショップ同様、bot対策による
        # 明確な拒否と判断しヘッダー偽装等での回避は行わず除外(None化)。
        buy_url=None,
        sell_url=None,
        shop_type="sell_only",
        parser="torema",
    ),
    ShopConfig(
        shop_id="bee_honpo",
        shop_name="Bee本舗",
        # WebSearchで発見(2026-09-04)。debug_fetch実行時、取得したページ内に
        # 実際のものと思われるAmazon OAuthクライアントID/シークレットが
        # 埋め込まれておりGitHub Push Protectionでコミット自体がブロック
        # された(該当ページ自体の実装ミスによる情報漏洩と推測)。他社の
        # 認証情報をリポジトリに取り込むリスクがあるため、このショップは
        # 対象から除外する(None化。debug_html保存対象にもしない)。
        buy_url=None,
        sell_url=None,
        shop_type="buy_only",
        parser="bee_honpo",
    ),
    ShopConfig(
        shop_id="toreca_camp",
        shop_name="トレカキャンプ",
        # WebSearchで発見(2026-09-04)。debug_fetchで実HTML確認済み:
        # Shopify製ストアで.product-item単位に構造化されており、実データ
        # 65件抽出できることを確認済み(価格は状態別レンジ表記のため
        # 上限値を採用)。
        buy_url=None,
        sell_url="https://torecacamp-pokemon.com/",
        shop_type="sell_only",
        parser="toreca_camp",
    ),
    ShopConfig(
        shop_id="cb_torecolo",
        shop_name="CBトレコロ",
        # WebSearchで発見(2026-09-04)。debug_fetchで実HTML確認済み:
        # MakeShop系ECテンプレート(.js-enhanced-ecommerce-item)で実データ
        # 25件抽出できることを確認済み。
        buy_url=None,
        sell_url="https://www.torecolo.jp/shop/c/c1074/",
        shop_type="sell_only",
        parser="cb_torecolo",
    ),
]

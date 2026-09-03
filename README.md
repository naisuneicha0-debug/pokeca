# ポケカ価格情報収集パイプライン

複数の買取/販売ショップの価格を定期的に取得し、`data/` 配下にJSONとして
出力・公開するパイプライン。UI(React側)はこのJSONを
`raw.githubusercontent.com` 経由でfetchする前提。

## 構成

```
scraper/
  config.py         # 対象ショップ一覧(shops)の定義。render_js=Trueで
                     #   headless browser経由の取得に切り替え
  rate_limiter.py    # requests/headless browser共通のレート制限ロジック
  robots.py          # 実行時にrobots.txtを取得し、アクセス可否を判定
  http_client.py     # requestsベースのクライアント + 文字コード判定
  browser_client.py  # Playwright(Chromium)でJS動的レンダリング後のHTMLを取得
  fetcher.py         # ショップ設定に応じてrequests/browserを使い分ける共通ロジック
  parsers/           # ショップ別パーサー(base.pyに共通ユーティリティ、ec_common.pyは複数ショップ共通)
  output.py          # data/shops.json, data/card_price.json への書き出し
  runner.py          # 全ショップを順に処理するエントリポイント(50万円未満を除外)
  debug_fetch.py     # 各ショップの生HTMLをdebug_html/に保存するデバッグ用スクリプト
.github/workflows/
  scrape.yml            # 定期実行 + 差分コミットpush(本番)
  debug_fetch_html.yml   # 手動実行のみ。生HTMLをartifact化 + リポジトリにも直接コミット
data/
  shops.json          # ショップ一覧(実行のたびに再生成)
  card_price.json      # 価格データ(実行のたびに最新スナップショットで上書き。50万円以上のみ)
```

## 実行方法

```
pip install -r requirements.txt
python -m scraper.runner
```

実行後、コンソールに収集サマリー(ショップ別取得件数・失敗/除外理由・
高額カード件数・価格帯)が出力される。

GitHub Actions (`scrape.yml`) は毎日1回自動実行し、`data/*.json` に変更が
あればコミット・pushする。手動実行は Actions タブから
`workflow_dispatch` で可能。

## スクレイピング時の配慮事項(実装済み)

- リクエストは `RateLimiter` を通して**常に直列**で行い、直前のリクエスト
  から2〜3秒(ランダム)空けてから次を投げる。requestsベースの取得と
  Playwright(headless browser)ベースの取得で同じRateLimiterインスタンスを
  共有しており、取得方式が混在しても全体を通して直列・一定間隔になる
- 各URLへのアクセス前に `robots.py` が対象ドメインの `robots.txt` を
  実行時に取得し、`Disallow` に該当する場合はアクセスをスキップして
  ログに理由を残す(コード側での自動判定。手動での利用規約確認は別途
  必要な場合がある)
- User-Agent は `PokecaPriceCompareBot/1.0` を名乗る(個人情報は含めない)
- 403 Forbiddenが繰り返され明確にbot対策と判断できるショップ(遊々亭・
  カードラッシュ買取・駿河屋)は、ヘッダー偽装等での回避は行わず対象から
  除外している(`scraper/config.py` 参照)

## 開発環境の制約

このセッション(Claude Code)自体のネットワークegressポリシーが対象
ショップドメインを直接ブロックするため、実サイトへの疎通確認はここでは
できない。そのため `debug_fetch_html.yml`(手動実行、生HTMLをリポジトリの
`debug_html/` に直接コミット)でGitHub Actions側から実HTMLを取得し、その
内容を見ながら `scraper/parsers/*.py` を実サイト構造に合わせて実装する
運用にしている。

## 現状の検証状況(2026-09-03時点)

`scraper/config.py` の各ショップのコメントに詳細と根拠を記載している。

- 実データ抽出できているショップ: トレトク(329件)、フルコンプ秋葉原店
  (5,267件)、カードラッシュ(sellのみ84件)、カードラボ(48件)、
  買取コレクター(ジャンル横断ハイライトの一部、9件)
- 対象除外(bot対策による403 Forbiddenが継続、回避は行わない方針):
  遊々亭、カードラッシュ(buy_urlのみ)、駿河屋
- Playwright導入済みだが専用パーサー未実装(汎用フォールバックのまま):
  晴れる屋2、ネットオフ もえたく!(いずれもJS動的レンダリングで
  `render_js=True`に設定済み。実レンダリング結果を見てのパーサー実装が
  次のステップ)
- 未解決: ニンニン(価格表が画像として掲載されており、通常の
  スクレイピング/JSレンダリングでは取得不可。OCRが必要)

## 高額カードのしきい値

`scraper/config.py` の `HIGH_VALUE_THRESHOLD`(50万円)。買取価格・売値
価格のいずれかがこの金額**以上**(上限なし)のレコードのみを
`data/card_price.json` に出力する。しきい値未満のレコードは収集はする
ものの、最終出力からは除外される(`runner.py` でフィルタ)。

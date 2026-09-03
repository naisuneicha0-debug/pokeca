# ポケカ価格情報収集パイプライン

複数の買取/販売ショップの価格を定期的に取得し、`data/` 配下にJSONとして
出力・公開するパイプライン。UI(React側)はこのJSONを
`raw.githubusercontent.com` 経由でfetchする前提。

## 構成

```
scraper/
  config.py        # 対象ショップ一覧(shops)の定義
  robots.py         # 実行時にrobots.txtを取得し、アクセス可否を判定
  http_client.py     # 直列アクセス・2〜3秒間隔のレート制限クライアント
  parsers/           # ショップ別パーサー(base.pyに共通ユーティリティ)
  output.py          # data/shops.json, data/card_price.json への書き出し
  runner.py          # 全ショップを順に処理するエントリポイント
.github/workflows/scrape.yml  # 定期実行 + 差分コミットpush
data/
  shops.json          # ショップ一覧(実行のたびに再生成)
  card_price.json      # 価格データ(実行のたびに最新スナップショットで上書き)
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

- リクエストは `RateLimitedClient` を通して**常に直列**で行い、直前の
  リクエストから2〜3秒(ランダム)空けてから次を投げる
- 各URLへのアクセス前に `robots.py` が対象ドメインの `robots.txt` を
  実行時に取得し、`Disallow` に該当する場合はアクセスをスキップして
  ログに理由を残す(コード側での自動判定。手動での利用規約確認は別途
  必要な場合がある)
- User-Agent は `PokecaPriceCompareBot/1.0` を名乗る(個人情報は含めない)

## 既知の制限・要検証事項(重要)

このパイプラインは、開発環境(Claude Code のネットワークegressポリシー)
の制約により、**対象ショップサイトへの実アクセスを一度も行わずに実装した**。
そのため以下は未検証:

- 各ショップの実際のHTML構造(遊々亭以外は`generic_text_list_parse`という
  汎用フォールバックパーサーを暫定使用)
- 一部ショップのURL(`scraper/config.py` 内の `TODO要検証` / `TODO要確認`
  コメント参照): 遊々亭の一覧URL、カードラッシュの販売URL、カードラボの
  買取URLの有無、晴れる屋2の買取URL・売URL、ニンニンの売URLなど
- 各ショップの `robots.txt` の実際の内容(実行時チェックのロジックは
  実装済みだが、動作は未確認)

引き継ぎ資料の要件どおり、**最初の数回のGitHub Actions実行結果は人間側で
確認**し、`data/card_price.json` の中身とActionsログのサマリーを見ながら
`scraper/config.py` のURLと `scraper/parsers/*.py` の各パーサーを
実サイト構造に合わせて調整していく想定。

## 高額カードのしきい値

`scraper/config.py` の `HIGH_VALUE_THRESHOLD`(50万円)。現状は全件を
収集した上でサマリー内で高額カード件数を集計する形にしている。

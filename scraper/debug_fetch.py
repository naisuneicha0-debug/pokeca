"""デバッグ用: 各ショップのbuy_url/sell_urlの生HTMLをそのままファイルに保存する。

パーサーの精度を上げるには実際のHTML構造を見る必要があるが、開発環境からは
対象サイトにアクセスできないため、GitHub Actions上でこのスクリプトを実行し、
結果をartifactとして取得して確認する運用にする。

出力先: debug_html/<shop_id>_<direction>.html (成功時)
        debug_html/<shop_id>_<direction>.error.txt (失敗時)
"""
from __future__ import annotations

from pathlib import Path

from .config import SHOPS
from .http_client import RateLimitedClient, USER_AGENT
from .robots import is_allowed

OUT_DIR = Path(__file__).resolve().parent.parent / "debug_html"


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    client = RateLimitedClient()

    for shop in SHOPS:
        for direction, url in (("buy", shop.buy_url), ("sell", shop.sell_url)):
            if not url:
                continue

            base_name = f"{shop.shop_id}_{direction}"

            if not is_allowed(url, USER_AGENT):
                msg = f"robots.txtにより除外: {url}"
                (OUT_DIR / f"{base_name}.error.txt").write_text(msg, encoding="utf-8")
                print(f"[SKIP] {shop.shop_name} ({direction}): {msg}")
                continue

            try:
                resp = client.get(url)
                status = resp.status_code
                resp.raise_for_status()
            except Exception as e:  # noqa: BLE001
                msg = f"URL: {url}\nエラー: {e}"
                (OUT_DIR / f"{base_name}.error.txt").write_text(msg, encoding="utf-8")
                print(f"[ERROR] {shop.shop_name} ({direction}): {e}")
                continue

            html_path = OUT_DIR / f"{base_name}.html"
            html_path.write_text(resp.text, encoding="utf-8")
            print(f"[OK] {shop.shop_name} ({direction}): status={status} bytes={len(resp.text)} -> {html_path.name}")


if __name__ == "__main__":
    run()

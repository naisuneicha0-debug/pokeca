"""デバッグ用: 各ショップのbuy_url/sell_url(複数ページある場合は全て)の
生HTML(render_js=Trueのショップはheadless browserでレンダリング後のHTML)
をそのままファイルに保存する。

パーサーの精度を上げるには実際のHTML構造を見る必要があるが、開発環境からは
対象サイトにアクセスできないため、GitHub Actions上でこのスクリプトを実行し、
結果をartifact化 + リポジトリに直接コミットして確認する運用にする。

出力先: debug_html/<shop_id>_<direction>_<連番>.html (成功時)
        debug_html/<shop_id>_<direction>_<連番>.error.txt (失敗時)
"""
from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path

from .config import SHOPS, get_urls
from .browser_client import browser_session
from .fetcher import Fetcher
from .rate_limiter import RateLimiter

OUT_DIR = Path(__file__).resolve().parent.parent / "debug_html"


def run() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rate_limiter = RateLimiter()

    needs_browser = any(shop.render_js for shop in SHOPS)

    with ExitStack() as stack:
        browser = None
        if needs_browser:
            try:
                browser = stack.enter_context(browser_session())
            except Exception as e:  # noqa: BLE001 - browser起動失敗でも他ショップは継続させる
                print(f"[ERROR] headless browser起動失敗: {e}")

        fetcher = Fetcher(rate_limiter, browser)

        for shop in SHOPS:
            for direction in ("buy", "sell"):
                for i, url in enumerate(get_urls(shop, direction)):
                    base_name = f"{shop.shop_id}_{direction}_{i}"

                    try:
                        text = fetcher.fetch(shop, url)
                    except Exception as e:  # noqa: BLE001
                        msg = f"URL: {url}\nエラー: {e}"
                        (OUT_DIR / f"{base_name}.error.txt").write_text(msg, encoding="utf-8")
                        print(f"[ERROR] {shop.shop_name} ({direction}) {url}: {e}")
                        continue

                    html_path = OUT_DIR / f"{base_name}.html"
                    html_path.write_text(text, encoding="utf-8")
                    print(
                        f"[OK] {shop.shop_name} ({direction}) {url}: "
                        f"bytes={len(text)} -> {html_path.name}"
                    )


if __name__ == "__main__":
    run()

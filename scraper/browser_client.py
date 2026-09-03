"""JSで動的にレンダリングされるページ用のheadless browserクライアント。

requestsでは静的HTMLしか取れないため、晴れる屋2・ネットオフ もえたく!の
ように価格一覧をクライアントサイドJSで描画するサイトはPlaywright
(Chromium)でレンダリング後のDOMを取得する。

同じRateLimiterインスタンスをRateLimitedClientと共有することで、取得方式が
混在してもアクセス全体が直列・一定間隔になる(「同時並列アクセスはしない」
「リクエスト間隔は最低2〜3秒空ける」の厳守事項に対応)。
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

from playwright.sync_api import sync_playwright, Browser

from .http_client import USER_AGENT
from .rate_limiter import RateLimiter

# ページ読み込み(networkidle)後、追加でJSの非同期描画を待つ猶予時間
RENDER_WAIT_MS = 3000
NAVIGATION_TIMEOUT_MS = 30000


@contextmanager
def browser_session() -> Iterator[Optional[Browser]]:
    """Chromiumを起動し、Browserインスタンスをwithブロックに渡す。"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            browser.close()


def fetch_rendered_html(browser: Browser, url: str, rate_limiter: RateLimiter) -> str:
    rate_limiter.wait()
    page = browser.new_page(user_agent=USER_AGENT)
    try:
        page.goto(url, wait_until="networkidle", timeout=NAVIGATION_TIMEOUT_MS)
        page.wait_for_timeout(RENDER_WAIT_MS)
        return page.content()
    finally:
        page.close()

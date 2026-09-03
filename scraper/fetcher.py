"""ショップ設定(render_js)に応じてrequests/headless browserを使い分けて
HTMLを取得する共通ロジック。runner.py / debug_fetch.py の両方から使う。
"""
from __future__ import annotations

from typing import Optional

from .browser_client import fetch_rendered_html
from .config import ShopConfig
from .http_client import RateLimitedClient, USER_AGENT, decode_html
from .rate_limiter import RateLimiter
from .robots import is_allowed


class Fetcher:
    def __init__(self, rate_limiter: RateLimiter, browser=None) -> None:
        self.client = RateLimitedClient(rate_limiter)
        self.rate_limiter = rate_limiter
        self.browser = browser  # playwright.sync_api.Browser、不要なら None

    def fetch(self, shop: ShopConfig, url: str) -> str:
        """指定URLのHTMLを取得する。robots.txtで禁止されている場合は
        PermissionErrorを送出する。"""
        if not is_allowed(url, USER_AGENT):
            raise PermissionError(f"robots.txtにより除外: {url}")

        if shop.render_js:
            if self.browser is None:
                raise RuntimeError("render_js=Trueのショップだがbrowserが未初期化")
            return fetch_rendered_html(self.browser, url, self.rate_limiter)

        resp = self.client.get(url)
        resp.raise_for_status()
        return decode_html(resp)

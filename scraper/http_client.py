import random
import time
import requests

# 「同時並列アクセスはしない」「リクエスト間隔は最低2〜3秒空ける」の厳守事項に対応。
# このクライアントを使い回す限り、直列実行かつ直前リクエストからの経過時間を
# 常に測って待機するため、呼び出し側が複数ショップ・複数ページをループしても
# 全体を通してレート制限がかかる。
USER_AGENT = "Mozilla/5.0 (compatible; PokecaPriceCompareBot/1.0)"
MIN_DELAY_SEC = 2.0
MAX_DELAY_SEC = 3.0


class RateLimitedClient:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self._last_request_at = 0.0

    def get(self, url: str, **kwargs) -> requests.Response:
        self._wait()
        kwargs.setdefault("timeout", 20)
        try:
            return self.session.get(url, **kwargs)
        finally:
            self._last_request_at = time.monotonic()

    def _wait(self) -> None:
        delay = random.uniform(MIN_DELAY_SEC, MAX_DELAY_SEC)
        elapsed = time.monotonic() - self._last_request_at
        remaining = delay - elapsed
        if remaining > 0:
            time.sleep(remaining)

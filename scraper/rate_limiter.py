import random
import time

# 「同時並列アクセスはしない」「リクエスト間隔は最低2〜3秒空ける」の厳守事項に
# 対応する共通ロジック。requestsベースのHTTPクライアントとheadless browser
# (browser_client.py)の両方から、同じインスタンスを使い回して呼び出すことで、
# 取得方式が混在しても全体を通して直列・一定間隔のアクセスになる。
MIN_DELAY_SEC = 2.0
MAX_DELAY_SEC = 3.0


class RateLimiter:
    def __init__(self) -> None:
        self._last_request_at = 0.0

    def wait(self) -> None:
        delay = random.uniform(MIN_DELAY_SEC, MAX_DELAY_SEC)
        elapsed = time.monotonic() - self._last_request_at
        remaining = delay - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last_request_at = time.monotonic()

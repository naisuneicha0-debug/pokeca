import random
import re
import time
import requests

_META_CHARSET_RE = re.compile(rb'charset=["\']?([\w-]+)', re.I)


def decode_html(resp: requests.Response) -> str:
    """レスポンス本文をHTMLとして正しくデコードする。

    requestsはHTTPヘッダにcharsetが無いとISO-8859-1にフォールバックし、
    日本語サイト(UTF-8/Shift_JISなど)で文字化けする。HTML内のmeta charset
    宣言を優先的に見て、それも無ければapparent_encodingで推定する。
    """
    content = resp.content
    m = _META_CHARSET_RE.search(content[:2000])
    if m:
        try:
            return content.decode(m.group(1).decode("ascii"), errors="replace")
        except LookupError:
            pass

    if resp.encoding and resp.encoding.lower() != "iso-8859-1":
        return resp.text

    return content.decode(resp.apparent_encoding or "utf-8", errors="replace")

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

import re
from typing import Optional

import requests

from .rate_limiter import RateLimiter

_META_CHARSET_RE = re.compile(rb'charset=["\']?([\w-]+)', re.I)

USER_AGENT = "Mozilla/5.0 (compatible; PokecaPriceCompareBot/1.0)"


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


class RateLimitedClient:
    """「同時並列アクセスはしない」「リクエスト間隔は最低2〜3秒空ける」の
    厳守事項に対応するHTTPクライアント。

    rate_limiterを外から渡せば、browser_client.pyのheadless browser経由の
    アクセスと同じRateLimiterを共有でき、取得方式が混在しても全体を通して
    直列・一定間隔のアクセスになる。省略時は専用のRateLimiterを新規作成する。
    """

    def __init__(self, rate_limiter: Optional[RateLimiter] = None) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            }
        )
        self._limiter = rate_limiter or RateLimiter()

    def get(self, url: str, **kwargs) -> requests.Response:
        self._limiter.wait()
        kwargs.setdefault("timeout", 20)
        return self.session.get(url, **kwargs)

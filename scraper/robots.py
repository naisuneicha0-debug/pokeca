import urllib.robotparser
from urllib.parse import urlparse
from typing import Dict
import requests

_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}


def is_allowed(url: str, user_agent: str) -> bool:
    """robots.txtを実行時に取得して当該URLへのアクセス可否を判定する。
    取得失敗時(robots.txtが存在しない等)は許可扱いとする。
    """
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    rp = _cache.get(origin)
    if rp is None:
        rp = urllib.robotparser.RobotFileParser()
        robots_url = f"{origin}/robots.txt"
        try:
            resp = requests.get(robots_url, timeout=10, headers={"User-Agent": user_agent})
            if resp.status_code == 200:
                rp.parse(resp.text.splitlines())
            else:
                rp.parse([])
        except requests.RequestException:
            rp.parse([])
        _cache[origin] = rp
    return rp.can_fetch(user_agent, url)

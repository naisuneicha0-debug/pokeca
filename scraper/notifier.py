from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

import requests

from .config import PRICE_CHANGE_ABS_THRESHOLD, PRICE_CHANGE_PCT_THRESHOLD

DISCORD_WEBHOOK_ENV = "DISCORD_WEBHOOK_URL"
_DISCORD_CONTENT_LIMIT = 2000

RecordKey = Tuple[str, str, Optional[str], Optional[str]]


def _key(r: Dict) -> RecordKey:
    return (r["source_site"], r["card_name"], r["set_code"], r["rarity"])


def _is_significant(old_price: Optional[int], new_price: Optional[int]) -> bool:
    if old_price is None or new_price is None:
        return False
    diff = abs(new_price - old_price)
    if diff == 0:
        return False
    if diff >= PRICE_CHANGE_ABS_THRESHOLD:
        return True
    return old_price > 0 and diff / old_price >= PRICE_CHANGE_PCT_THRESHOLD


def detect_changes(previous_records: List[Dict], current_records: List[Dict]) -> Dict[str, List[Dict]]:
    """前回スナップショットと今回の収集結果を比較し、通知に値する変化を抽出する。

    - "changed": 既存カードの買取/売値が閾値以上動いたもの
    - "new": 前回は50万円条件を満たしていなかった(=存在しなかった)が今回新規に条件を満たしたもの
    """
    previous_by_key = {_key(r): r for r in previous_records}

    changed: List[Dict] = []
    new: List[Dict] = []

    for r in current_records:
        old = previous_by_key.get(_key(r))
        if old is None:
            new.append(r)
            continue

        for field in ("buy_price", "sell_price"):
            if _is_significant(old[field], r[field]):
                changed.append(
                    {
                        "card_name": r["card_name"],
                        "set_code": r["set_code"],
                        "rarity": r["rarity"],
                        "source_site": r["source_site"],
                        "field": field,
                        "old_price": old[field],
                        "new_price": r[field],
                    }
                )

    return {"changed": changed, "new": new}


def _field_label(field: str) -> str:
    return "買取価格" if field == "buy_price" else "売値"


def format_discord_message(changes: Dict[str, List[Dict]]) -> Optional[str]:
    changed = changes["changed"]
    new = changes["new"]
    if not changed and not new:
        return None

    lines = ["## ポケカ高額カード価格変動通知"]

    if changed:
        lines.append(f"\n### 価格変動({len(changed)}件)")
        for c in changed:
            diff = c["new_price"] - c["old_price"]
            sign = "+" if diff > 0 else ""
            lines.append(
                f"- [{c['source_site']}] {c['card_name']} {_field_label(c['field'])}: "
                f"{c['old_price']:,}円 → {c['new_price']:,}円 ({sign}{diff:,}円)"
            )

    if new:
        lines.append(f"\n### 新規に50万円以上を検出({len(new)}件)")
        for r in new:
            price_parts = []
            if r["buy_price"]:
                price_parts.append(f"買取{r['buy_price']:,}円")
            if r["sell_price"]:
                price_parts.append(f"売値{r['sell_price']:,}円")
            lines.append(f"- [{r['source_site']}] {r['card_name']} ({', '.join(price_parts)})")

    message = "\n".join(lines)
    if len(message) > _DISCORD_CONTENT_LIMIT:
        message = message[: _DISCORD_CONTENT_LIMIT - 20].rstrip() + "\n...(以下省略)"
    return message


def send_discord_notification(message: str, webhook_url: Optional[str] = None) -> bool:
    webhook_url = webhook_url or os.environ.get(DISCORD_WEBHOOK_ENV)
    if not webhook_url:
        print("[INFO] DISCORD_WEBHOOK_URL未設定のため通知をスキップします")
        return False

    resp = requests.post(webhook_url, json={"content": message}, timeout=10)
    resp.raise_for_status()
    return True


def load_previous_records(path) -> List[Dict]:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def notify_price_changes(previous_records: List[Dict], current_records: List[Dict]) -> None:
    changes = detect_changes(previous_records, current_records)
    message = format_discord_message(changes)
    if message is None:
        print("[INFO] 通知に値する価格変動なし")
        return

    try:
        sent = send_discord_notification(message)
    except requests.RequestException as e:
        print(f"[ERROR] Discord通知送信失敗: {e}")
        return

    if sent:
        print(f"[INFO] Discord通知送信済み(変動{len(changes['changed'])}件, 新規{len(changes['new'])}件)")

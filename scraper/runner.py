from __future__ import annotations

from typing import List, Dict

from .config import SHOPS, HIGH_VALUE_THRESHOLD, get_urls
from .http_client import RateLimitedClient, USER_AGENT, decode_html
from .robots import is_allowed
from .parsers import get_parser
from .output import write_shops, write_card_price


def run() -> None:
    client = RateLimitedClient()
    all_records: List[Dict] = []
    summary = []

    for shop in SHOPS:
        shop_result = {
            "shop_id": shop.shop_id,
            "shop_name": shop.shop_name,
            "buy": 0,
            "sell": 0,
            "skipped": [],
            "errors": [],
        }
        parser = get_parser(shop.parser)

        for direction in ("buy", "sell"):
            urls = get_urls(shop, direction)

            for url in urls:
                if not is_allowed(url, USER_AGENT):
                    msg = f"robots.txtにより除外: {url}"
                    shop_result["skipped"].append(msg)
                    print(f"[SKIP] {shop.shop_name} ({direction}): {msg}")
                    continue

                try:
                    resp = client.get(url)
                    resp.raise_for_status()
                except Exception as e:  # noqa: BLE001 - ショップ単位で失敗を切り分けたい
                    shop_result["errors"].append(f"{direction}取得失敗 ({url}): {e}")
                    print(f"[ERROR] {shop.shop_name} ({direction}) fetch {url}: {e}")
                    continue

                try:
                    records = parser(decode_html(resp), shop.shop_name, direction)
                except Exception as e:  # noqa: BLE001
                    shop_result["errors"].append(f"{direction}パース失敗 ({url}): {e}")
                    print(f"[ERROR] {shop.shop_name} ({direction}) parse {url}: {e}")
                    continue

                shop_result[direction] += len(records)
                all_records.extend(records)

        summary.append(shop_result)

    # 収集対象は50万円以上のみ(上限なし)。買取・売値のどちらかが
    # しきい値を超えていれば残す。
    high_value_records = [
        r
        for r in all_records
        if (r["buy_price"] or 0) >= HIGH_VALUE_THRESHOLD or (r["sell_price"] or 0) >= HIGH_VALUE_THRESHOLD
    ]

    write_shops()
    write_card_price(high_value_records)

    _print_summary(summary, all_records, high_value_records)


def _print_summary(summary: list, all_records: List[Dict], high_value_records: List[Dict]) -> None:
    print("\n===== 収集サマリー =====")
    total = 0
    for s in summary:
        n = s["buy"] + s["sell"]
        total += n
        status_parts = []
        if s["skipped"]:
            status_parts.append(f"除外{len(s['skipped'])}件")
        if s["errors"]:
            status_parts.append(f"エラー{len(s['errors'])}件")
        status_str = f" [{', '.join(status_parts)}]" if status_parts else ""
        print(f"- {s['shop_name']}: 買取{s['buy']}件 / 売値{s['sell']}件{status_str}")
        for e in s["errors"]:
            print(f"    ! {e}")
        for sk in s["skipped"]:
            print(f"    - {sk}")

    prices = [p for r in high_value_records for p in (r["buy_price"], r["sell_price"]) if p is not None]

    print(f"\nスキャン総件数: {total}")
    print(f"収集対象({HIGH_VALUE_THRESHOLD:,}円以上、上限なし)件数: {len(high_value_records)}")
    if prices:
        print(f"価格帯: {min(prices):,}円 〜 {max(prices):,}円")
    else:
        print("価格帯: データなし")

    failed_shops = [s["shop_name"] for s in summary if s["errors"] and s["buy"] == 0 and s["sell"] == 0]
    if failed_shops:
        print(f"完全に失敗したショップ: {', '.join(failed_shops)}")
    print("=========================\n")


if __name__ == "__main__":
    run()

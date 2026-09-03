import json
from pathlib import Path
from typing import List, Dict

from .config import SHOPS

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def write_shops() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    shops = [
        {
            "shop_id": s.shop_id,
            "shop_name": s.shop_name,
            "buy_url": s.buy_url,
            "sell_url": s.sell_url,
            "shop_type": s.shop_type,
        }
        for s in SHOPS
    ]
    path = DATA_DIR / "shops.json"
    path.write_text(json.dumps(shops, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_card_price(records: List[Dict]) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "card_price.json"
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

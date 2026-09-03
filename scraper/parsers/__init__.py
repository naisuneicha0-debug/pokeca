import importlib
from typing import Callable, List, Dict


def get_parser(name: str) -> Callable[[str, str, str], List[Dict]]:
    module = importlib.import_module(f"scraper.parsers.{name}")
    return module.parse

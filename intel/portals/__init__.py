"""Multi-portal dispatcher.

Each engine module exposes `scrape_portal(portal, keywords, pages) -> list[dict]`
returning flat rows ready for the normal enrich/upsert pipeline (source,
portal_code, bid_number, title, status, end_date, source_url, _raw).

The `gem` and `cppp` sources are handled by their original modules (gem.py /
cppp.py) and are kept OUT of this dispatcher.
"""
from __future__ import annotations

import importlib

from config import PORTALS, PORTAL_ENGINES

_T = ("drupal", "nprocure", "generic", "health", "bihar", "telangana")


def engine_for(portal: dict):
    eng = portal.get("engine")
    if eng in _T:
        return importlib.import_module(f"portals.{eng}")
    return importlib.import_module("portals.generic")


def scrape_portal(portal: dict, keywords: list[str], pages: int = 3) -> list[dict]:
    mod = engine_for(portal)
    fn = getattr(mod, "scrape_portal", None)
    if fn is None:
        from . import generic
        fn = generic.scrape_listings
    rows = fn(portal, keywords, pages=pages)
    for r in rows:
        r["portal_code"] = portal["code"]
        r["source"] = f"{portal['code']}:{portal.get('engine', 'generic')}"
    return rows


def all_portals() -> list[dict]:
    return [p for p in PORTALS if p.get("engine") != "gem"]


def portal(code: str) -> dict | None:
    for p in PORTALS:
        if p["code"] == code and p.get("engine") != "gem":
            return p
    return None
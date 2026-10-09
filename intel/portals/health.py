"""Medical supplies corporations / hospital-sector procurement pages.

These bodies usually buy on GeM for the bulk and run small own-site call
notices for the rest. There is no shared engine, so this adaptor is a thin
wrapper over `generic.scrape_listings` with their typical notice paths.
"""
from __future__ import annotations

from . import generic

_PATHS = ["/", "/tenders", "/procurement", "/notices", "/tender-notice",
          "/call-for-bids", "/e-tender", "/uploads/tender"]


def scrape_portal(portal: dict, keywords: list[str], pages: int = 3) -> list[dict]:
    cfg = {**portal, "paths": _PATHS}
    return generic.scrape_listings(cfg, keywords, pages=pages)
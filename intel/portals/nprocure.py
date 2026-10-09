"""Gujarat nprocure.com adaptor (ASP.NET engine).

Like CPPP, keyword search on nprocure requires a logged-in session/CAPTCHA
for the tender search, so the initial implementation mines public listing
pages and filters locally. Returns rows via `generic.scrape_listings`.
"""
from __future__ import annotations

from . import generic

_PATHS = ["/", "/View_All_Tenders", "/tenders", "/Tender", "/TenderListPage"]


def scrape_portal(portal: dict, keywords: list[str], pages: int = 3) -> list[dict]:
    cfg = {**portal, "paths": _PATHS}
    return generic.scrape_listings(cfg, keywords, pages=pages)
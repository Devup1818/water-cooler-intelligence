"""Drupal eprocure engine (CPPP + most state portals).

The eprocure family shares a Drupal 7 form with `form_id`,
`form_build_id`, `form_token` and a keyword field. On most deployments the
search POST is CAPTCHA-gated, so we ALWAYS fall back to public listing pages
(best-effort keyword sampling) exactly like CPPP.

Action-path candidates vary per state, so we probe a small list and take the
first that yields rows; otherwise we hand off to `generic.scrape_listings`.
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.request

from config import HTTP_HEADERS, REQUEST_TIMEOUT

from . import base

_FORM_IDS = ["tendersearch_form", "eproc_form_search", "search_form"]
_ACTION_CANDIDATES = [
    "cppp/tendersearch/cpppdata",
    "tendersearch/cpppdata",
    "eprocure/tendersearch/nit",
    "tendersearch/getdata",
]


def search_form(portal: dict, keywords: list[str], pages: int = 3,
                timeout: int = 40) -> list[dict]:
    base_url = portal["base"].rstrip("/")
    for action in _ACTION_CANDIDATES:
        try:
            rows = _try_form(base_url + "/" + action, portal, keywords)
        except Exception:
            rows = []
        if rows:
            return rows
    return []


def _try_form(action_url: str, portal: dict, keywords: list[str]) -> list[dict]:
    # fetch a page to learn the CSRF tokens
    probe_urls = (portal.get("search") and [portal["search"]]) or [portal["base"] + "/tendersearch"]
    form_html = ""
    for u in probe_urls:
        form_html = base.fetch(u, portal["code"]) or ""
        if form_html:
            break
    if not form_html:
        return []
    form_build = re.search(r'name="form_build_id" value="([^"]+)"', form_html)
    form_token = re.search(r'name="form_token" value="([^"]+)"', form_html)

    rows: list[dict] = []
    for form_id in _FORM_IDS:
        if not (form_build and form_token):
            continue
        for kw in keywords:
            data = {
                "form_id": form_id,
                "form_build_id": form_build.group(1),
                "form_token": form_token.group(1),
                "keyword": kw,
                "op": "Search",
            }
            body = urllib.parse.urlencode(data).encode("utf-8")
            html = None
            try:
                req = urllib.request.Request(
                    action_url, data=body,
                    headers={"Content-Type": "application/x-www-form-urlencoded",
                             **HTTP_HEADERS})
                base.throttle(portal["code"])
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT,
                                            context=base.ssl_ctx()) as resp:
                    html = resp.read().decode("utf-8", "ignore")
            except Exception:
                pass
            if not html:
                continue
            got = generic_like_rows(html, portal)
            if got:
                rows.extend(got)
    return rows


def generic_like_rows(html: str, portal: dict) -> list[dict]:
    from . import generic
    rows = []
    seen = set()
    for row in base.tables(html):
        b = generic._row_to_bid(row, portal, portal["base"])
        if b and (b["title"] or ""):
            k = (b["bid_number"], b["title"][:60])
            if k not in seen:
                seen.add(k)
                rows.append(b)
    return rows


def scrape(portal: dict, keywords: list[str], pages: int = 3) -> list[dict]:
    rows = search_form(portal, keywords, pages=pages)
    if rows:
        return rows
    from . import generic
    return generic.scrape_listings(portal, keywords, pages=pages)


def scrape_portal(portal: dict, keywords: list[str], pages: int = 3) -> list[dict]:
    return scrape(portal, keywords, pages=pages)
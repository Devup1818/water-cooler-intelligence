"""CPPP (Central Public Procurement Portal) best-effort scraper.

The tendersearch form is CAPTCHA-gated, so fully-automated keyword search is
NOT reliable. This module:
  1. Tries the Drupal AJAX search; if the CAPTCHA blocks it, it fails gracefully.
  2. Provides a public paginated page parser fallback for the "Active Tenders"
     listing (no keyword filter, but usable for market sampling by org).

You can later scale to state portals (each is a different Drupal verb) by
adding a StateScraper subclass - see README.
"""
from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from config import HTTP_HEADERS, REQUEST_TIMEOUT

TENDER_SEARCH_FORM = "https://eprocure.gov.in/cppp/tendersearch"
TENDER_SEARCH_ACTION = "https://eprocure.gov.in/cppp/tendersearch/cpppdata"
ACTIVE_TENDERS = "https://eprocure.gov.in/eprocure/app?page=FrontEndLatestActiveTenders&service=page"


def _ctx() -> ssl.SSLContext | None:
    try:
        return ssl.create_default_context()
    except Exception:
        return None


def _fetch(url: str, **kw):
    kw.setdefault("timeout", REQUEST_TIMEOUT)
    kw.setdefault("headers", HTTP_HEADERS)
    import urllib.request as u
    return u.urlopen(urllib.request.Request(url, headers=kw.pop("headers")), **kw)


# ---------------------------------------------------------------------------
# Drupal form approach (best effort - will be rejected when CAPTCHA is on)
# ---------------------------------------------------------------------------
def search_form_cppp(keywords: list[str], pages: int = 3) -> list[dict]:
    """POST the Drupal `tendersearch-form`. Expected to 403/redirect on CAPTCHA."""
    out: list[dict] = []
    first = _fetch(TENDER_SEARCH_FORM).read().decode("utf-8", "ignore")
    form_build = re.search(r'name="form_build_id" value="([^"]+)"', first)
    token = re.search(r'name="form_token" value="([^"]+)"', first)
    sess = re.search(r'name="captcha_sid" value="(\d+)"', first)
    key = re.search(r'name="captcha_token" value="([^"]+)"', first)
    if not (form_build and token):
        return out

    for kw in keywords:
        data = {
            "form_id": "tendersearch_form",
            "form_build_id": form_build.group(1),
            "form_token": token.group(1),
            "keyword": kw,
            "op": "Search",
        }
        if sess and key:
            data.update({"captcha_sid": sess.group(1), "captcha_token": key.group(1), "captcha_response": ""})
        body = urllib.parse.urlencode(data).encode()
        try:
            resp = _fetch(TENDER_SEARCH_ACTION, data=body)
            html = resp.read().decode("utf-8", "ignore")
            rows = _parse_cppp_table(html)
            if rows:
                out.extend(rows)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            break  # captcha / block - stop
        time.sleep(1.2)
    return out


# ---------------------------------------------------------------------------
# Public listing page fallback (no keyword, but no captcha either)
# ---------------------------------------------------------------------------
def scrape_active_tenders(max_pages: int = 2) -> list[dict]:
    out: list[dict] = []
    for page in range(1, max_pages + 1):
        url = ACTIVE_TENDERS
        try:
            html = _fetch(url).read().decode("utf-8", "ignore")
        except Exception:
            break
        rows = _parse_cppp_table(html)
        out.extend(rows)
        time.sleep(1.0)
    return out


# ---------------------------------------------------------------------------
# Shared table parser for CPPP/html listing pages
# ---------------------------------------------------------------------------
class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_rows = 0
        self.in_cell = False
        self.row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.in_rows += 1
            self.row = []
        elif tag in ("td", "th"):
            self.in_cell = True
            self._cell = []
        elif tag == "br" and self.in_cell:
            self._cell.append(" ")

    def handle_data(self, data):
        if self.in_cell:
            self._cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_cell:
            self.row.append(" ".join("".join(self._cell).split()))
            self.in_cell = False
        elif tag == "tr" and self.row:
            self.rows.append(self.row)

    def _strip_tags(self, s: str) -> str:
        return re.sub(r"<[^>]+>", " ", s)


def _parse_cppp_table(html: str) -> list[dict]:
    p = _TableParser()
    try:
        p.feed(html)
    except Exception:
        return []
    out: list[dict] = []
    for row in p.rows:
        if len(row) < 4:
            continue
        joined = " ".join(row)
        title_ref = row[-2] if len(row) >= 5 else row[-1]
        created = re.search(r"([0-9]{2}-[A-Za-z]{3}-[0-9]{4}|[0-9]{2}-[0-9]{2}-[0-9]{4})", joined)
        out.append({
            "source": "cppp",
            "title": joined[:300],
            "bid_number": re.sub(r"/\s*", "/", title_ref)[:120] if title_ref else None,
            "publish_date": created.group(0) if created else None,
            "_raw": joined[:800],
        })
    return out


def keyword_filter(rows: list[dict], keywords: list[str]) -> list[dict]:
    kws = [k.lower() for k in keywords]
    hits = []
    for r in rows:
        t = (r.get("title") or "").lower()
        if any(k in t for k in kws):
            hits.append(r)
    return hits
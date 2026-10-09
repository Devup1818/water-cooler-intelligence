"""Shared machinery for third-party (non-GeM) tender portals.

Design notes
------------
State e-procure sites rarely expose a clean JSON API the way GeM bidplus does.
Most are Drupal-forks (same engine as CPPP), a few are ASP.NET (nprocure),
and the health corps are plain corporate sites. This module provides:

  * polite, throttled fetching (urllib/ssl-off for corp proxy like GeM)
  * a generic table extractor
  * an anchor-based "tender link" finder so we can mine a listing page even
    when we do not know its exact table structure
  * a local keyword+bucket filter used as the fallback when the site's own
    search is CAPTCHA-gated.

Every engine adaptor (`drupal`, `nprocure`, `generic`, `health`) is expected
to return flat dicts matching the `bids` table columns; the CLI enriches them
(capacity/relevance/state/segment) via the normal pipeline.
"""
from __future__ import annotations

import datetime
import hashlib
import re
import ssl
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser

from config import HTTP_HEADERS, REQUEST_TIMEOUT


# ---------------------------------------------------------------------------
# throttle + fetch
# ---------------------------------------------------------------------------
_last_hit: dict[str, float] = {}


def throttle(portal_code: str, per_second: float = 0.8) -> None:
    now = time.time()
    gap = _last_hit.get(portal_code)
    if gap:
        wait = (1.0 / per_second) - (now - gap)
        if wait > 0:
            time.sleep(wait)
    _last_hit[portal_code] = time.time()


def ssl_ctx() -> ssl.SSLContext | None:
    """Unverified context: corporate MITM proxies break cert validation."""
    try:
        return ssl._create_unverified_context()
    except Exception:
        try:
            return ssl.create_default_context()
        except Exception:
            return None


def fetch(url: str, portal_code: str = "portal", timeout: int = REQUEST_TIMEOUT,
          max_meta_hops: int = 4) -> str | None:
    """Fetch HTML, following HTTP + META-refresh (GePNIC-style) redirects."""
    cur = url
    for _ in range(max_meta_hops + 2):
        throttle(portal_code)
        req = urllib.request.Request(cur, headers=HTTP_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as resp:
                html = resp.read().decode("utf-8", "ignore")
        except Exception:
            return None
        m = re.search(r'<meta[^>]+http-equiv=["\']?refresh["\']?\s+content=["\']0;\s*URL=([^"\']+)',
                      html, re.I)
        if not m:
            # also handle JS meta variant with semicolon spacing
            m = re.search(r'URL\s*=\s*([^\'"\s;]+)', html, re.I)
        if m:
            nxt = urllib.parse.urljoin(cur, m.group(1).strip())
            if nxt == cur:
                return html
            cur = nxt
            continue
        return html
    return None


# ---------------------------------------------------------------------------
# table extraction (shared HTMLParser from cppp)
# ---------------------------------------------------------------------------
class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.in_cell = False
        self.row: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.depth += 1
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


def tables(html: str) -> list[list[str]]:
    p = TableParser()
    try:
        p.feed(html)
    except Exception:
        return []
    return p.rows


# ---------------------------------------------------------------------------
# anchor-based discoverer (works on any listing page)
# ---------------------------------------------------------------------------
class _AnchorParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base = base_url
        self.links: list[tuple[str, str]] = []  # (href, text)

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        d = dict(attrs)
        href = d.get("href", "")
        if not href or href.startswith(("javascript", "#", "mailto")):
            return
        full = urllib.parse.urljoin(self.base, href) if self.base else href
        self.links.append((full, ""))
        self._pending = len(self.links) - 1

    def handle_data(self, data):
        if getattr(self, "_pending", None) is not None and self.links:
            t = self.links[self._pending][1]
            self.links[self._pending] = (self.links[self._pending][0], t + data)

    def handle_endtag(self, tag):
        if tag == "a":
            self._pending = None


_TENDER_HINT = re.compile(r"tender|dareid|viewbid|bid(?!plus)|detail|procurement", re.I)


def find_tender_links(html: str, url: str) -> list[tuple[str, str]]:
    p = _AnchorParser(url)
    try:
        p.feed(html)
    except Exception:
        return []
    out = []
    for href, text in p.links:
        t = " ".join(text.split())
        if not t or len(t) < 12:
            continue
        if _TENDER_HINT.search(href) and _TENDER_HINT.search(t):
            out.append((href, t))
    return out


def guess_listing_urls(portal: dict) -> list[str]:
    base_url = portal["base"].rstrip("/")
    if portal.get("paths"):
        candidates = portal["paths"]
    else:
        # GePNIC NIC e-procure apps serve the recent-tenders marquee on these
        # app pages (CPPP = /eprocure/app, states = /nicgep/app). Prefer the
        # context path that matches the host (eprocure.gov.in -> /eprocure).
        if "eprocure" in base_url.lower():
            candidates = [
                "/eprocure/app?page=FrontEndLatestActiveTenders&service=page",
                "/nicgep/app?page=FrontEndLatestActiveTenders&service=page",
            ]
        else:
            candidates = [
                "/nicgep/app?page=FrontEndLatestActiveTenders&service=page",
                "/eprocure/app?page=FrontEndLatestActiveTenders&service=page",
            ]
        candidates += [
            "/nicgep/app?page=FrontEndListTendersbyDate&service=page",
            "/",
            "/tenders", "/procurement", "/eprocure", "/tendersearch",
        ]
    seen: list[str] = []
    for c in candidates:
        u = c if c.startswith("http") else base_url + c
        if u not in seen:
            seen.append(u)
    if portal.get("search"):
        seen.insert(0, portal["search"])
    return seen


def noid_id(title: str, url: str) -> str:
    raw = f"{title}:{url}"
    return "NID" + hashlib.sha1(raw.encode()).hexdigest()[:9].upper()


def date_of(text: str) -> str | None:
    m = re.search(r"([0-9]{1,2})[/-]([0-9]{1,2})[/-](20\d\d)(?:\s+([0-9]{1,2}):([0-9]{2}))?", text)
    if not m:
        m = re.search(r"([0-9]{1,2})\s*[-/]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*[-/]\s*(20\d\d)(?:\s+([0-9]{1,2}):([0-9]{2})\s*[AP]M?)?", text, re.I)
    if not m:
        return None
    return m.group(0).replace(".", "/")
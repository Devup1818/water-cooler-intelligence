"""Generic listing-page scraper: works on any portal whose public pages show
recent tenders in a table or as anchor links. Rows are keyword-filtered
locally, so it is the universal fallback when a portal's own search is gated.
"""
from __future__ import annotations

import re
import urllib.parse

from . import base

_REF = re.compile(r"([A-Za-z0-9]+(?:[/\-_.][A-Za-z0-9]+){1,10})")


def _ref_value(s: str) -> str | None:
    m = _REF.search(s or "")
    if not m:
        return None
    ref = re.sub(r"\s+dated\s*.*$", "", m.group(1))
    ref = ref.strip("/ ._-")
    if len(ref) < 4:
        return None
    return ref[:60]

_FOOTER = re.compile(
    r"(^(version\s*:|copyright|screen reader|\s*powered by|best viewed|"
    r"contents owned|forgot password|new user|register|important links|"
    r"contact us|sitemap|help\s*[:d])"
    r"|eProcurement System Government of|MIS Reports|Tenders by Location|"
    r"Tenders by Organisation|Tenders by Classification|Tenders by Closing Date|"
    r"Active Tenders|Screen Reader|Fee Collection|Payment related issues|"
    r"Bidders who are using|Tenders in Archive|Tenders Status|Cancelled/Retendered|"
    r"Results of Tenders|Bid Awards|e-Published Date|Organisation Chain|"
    r"Tender Details|View More Details|Online Bidder Enrollment|"
    r"Hassle Free Bid|Bidders Manual Kit|Prebid Replies|Nodal Officer|"
    r"^Corrigendum|©|\s*\(c\)\s*20\d\d"
    r"|«|<<|kind attention|instruction to bidders|guide lines|\bguideline\b|"
    r"regarding publishing|application fees|internet banking|\bsb mops\b|"
    r"pre.?bid|tender cum auction|tn tenders act|(?:^|\s)notice no\.?\s|"
    r"e[- ]tender notice|announcement\b)", re.I)


def _is_footer(t: str) -> bool:
    return bool(_FOOTER.search(t or ""))


def _clean_title(t: str) -> str:
    t = t.strip()
    t = re.sub(r"^\s*\d+\.\s*", "", t)      # leading "1. "
    t = re.sub(r"\s+", " ", t)
    return t[:400]


def _row_to_bid(row: list[str], portal: dict, url: str) -> dict | None:
    joined = " ".join(str(c) for c in row)
    if not joined.strip():
        return None
    # skip header rows
    if re.search(r"tender title|reference no|closing date", joined, re.I) and len(row) <= 6:
        return None
    # GePNIC layout: [Title, Ref No, Closing, Bid Opening]
    end_date = None
    bid_number = None
    if len(row) >= 4 and base.date_of(row[2]) and base.date_of(row[2]) != base.date_of(row[3] or ""):
        bid_number = _ref_value(row[1])
        if not bid_number:
            return None  # announcement/notice row, not a tender
        end_date = row[2]
        title = _clean_title(row[0])
        if not title or _is_footer(title) or title.lower().startswith("corrigendum"):
            return None
        return {
            "source": portal.get("engine", "generic"),
            "portal_code": portal["code"],
            "bid_number": bid_number,
            "title": title or joined[:400],
            "status": "open",
            "end_date": end_date,
            "publish_date": None,
            "source_url": url,
            "org_name": _org_of(portal, joined),
            "_raw": joined[:800],
        }

    ref = _ref_value(joined)
    bid_number = bid_number or ref
    title = ""
    cells = sorted((str(c) for c in row if len(str(c)) >= 8), key=len, reverse=True)
    if cells:
        title = _clean_title(cells[0])
    elif bid_number:
        title = joined[:220]
    if _is_footer(title):
        return None
    if not title:
        return None
    # fallback rows must look like a real bid: an id/reference AND a date
    if not ref or not base.date_of(joined):
        return None

    if not end_date:
        m = re.search(
            r"(?:last date|closing|bid end|due date|End Date|Submission)\s*"
            r"[:\-]?\s*([0-9]{1,2}[/\-][0-9]{1,2}[/\-]20\d\d(?:\s+[0-9]{1,2}:[0-9]{2})?)",
            joined, re.I)
        end_date = m.group(1) if m else base.date_of(joined)
    publish_date = base.date_of(joined)
    if end_date == publish_date:
        publish_date = None
    return {
        "source": portal.get("engine", "generic"),
        "portal_code": portal["code"],
        "bid_number": bid_number or base.noid_id(title, url),
        "title": title[:400] or joined[:400],
        "status": "open",
        "end_date": end_date,
        "publish_date": publish_date,
        "source_url": url,
        "org_name": _org_of(portal, joined),
        "_raw": joined[:800],
    }


def _org_of(portal: dict, text: str) -> str | None:
    m = re.search(r"(?:organisation|organization|buyer|dept)\s*[:\-]\s*([A-Za-z][A-Za-z &()/.-]{3,60})", text, re.I)
    if m:
        return m.group(1).strip()
    return None


def scrape_listings(portal: dict, keywords: list[str], pages: int = 3) -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    listing_urls = [u for u in base.guess_listing_urls(portal)
                    if u != portal.get("search")][:pages]
    for url in listing_urls:
        html = base.fetch(url, portal["code"])
        if not html:
            continue
        # tables first
        got_table_rows = False
        for row in base.tables(html):
            b = _row_to_bid(row, portal, url)
            if b and (b["title"] or ""):
                key = (b["bid_number"], b["title"][:60])
                if key not in seen:
                    seen.add(key)
                    out.append(b)
                    got_table_rows = True
        # anchor fallback only for row-less pages (health corps / odd layouts)
        if got_table_rows:
            continue
        for href, text in base.find_tender_links(html, url):
            t = _clean_title(text)
            if _is_footer(t) or not t:
                continue
            key = ("anchor", t[:60], href)
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "source": portal.get("engine", "generic"),
                "portal_code": portal["code"],
                "bid_number": base.noid_id(t, href),
                "title": t,
                "status": "open",
                "source_url": href,
                "_raw": f"{t} | {href}",
            })
    return base_filter(out, keywords)


def base_filter(rows: list[dict], keywords: list[str]) -> list[dict]:
    if not keywords:
        return rows
    kws = [k.lower() for k in keywords]
    hits = []
    for r in rows:
        t = (r.get("title") or "").lower()
        if any(k in t for k in kws):
            hits.append(r)
    return hits
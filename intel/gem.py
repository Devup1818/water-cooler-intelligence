"""GeM bidplus scraper.

Discovers public tender/bid listings for water-cooler keywords via the
`all-bids-data` AJAX endpoint (POST + per-session CSRF token), then can pull
the full bid-document PDF for each interesting bid so structured fields
(specs, EMD, ePBG, quantity, consignees, capacity) can be parsed.

Endpoints (re-verified live):
    page:   https://bidplus.gem.gov.in/all-bids
    data:   https://bidplus.gem.gov.in/all-bids-data   (CSRF-gated session)
    pdf:    https://bidplus.gem.gov.in/showbidDocument/{id}
"""
from __future__ import annotations

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from http.cookiejar import CookieJar
from pathlib import Path

from config import (AUTHORIZED_THROUGHPUT, DB_PATH, GEM_KEYWORDS, HTTP_HEADERS,
                    REQUEST_TIMEOUT)

BIDS_PAGE = "https://bidplus.gem.gov.in/all-bids"
BIDS_DATA = "https://bidplus.gem.gov.in/all-bids-data"
BID_DOC = "https://bidplus.gem.gov.in/showbidDocument/{bid_id}"

_STATUS_MAP = {1: "published", 2: "ended", 3: "cancelled"}
_TYPE_MAP = {
    1: "product", 2: "service", 3: "product custom", 4: "boq", 5: "rate contract",
    6: "global", 7: "limited", 8: "single", 9: "bid to RA", 10: "RA to bid",
}


def _ssl_ctx() -> ssl.SSLContext:
    """Local corporate MITM proxy -> disable verification (curl already works)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _opener() -> urllib.request.OpenerDirector:
    cj = CookieJar()
    op = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(context=_ssl_ctx()),
    )
    for k, v in HTTP_HEADERS.items():
        op.addheaders.append((k, v))
    op.addheaders += [
        ("Referer", BIDS_PAGE),
        ("X-Requested-With", "XMLHttpRequest"),
        ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
    ]
    return op


class GemSession:
    """Holds a cookie session + CSRF token, the pair GeM requires."""

    def __init__(self, opener: urllib.request.OpenerDirector | None = None):
        self.opener = opener or _opener()
        self.csrf: str | None = None
        self.last_request_ms = 0.0

    def _throttle(self) -> None:
        gap = 1.0 / AUTHORIZED_THROUGHPUT
        wait = gap - (time.time() - self.last_request_ms)
        if wait > 0:
            time.sleep(wait)

    def refresh_token(self) -> None:
        self._throttle()
        try:
            resp = self.opener.open(BIDS_PAGE, timeout=REQUEST_TIMEOUT)
            html = resp.read().decode("utf-8", "ignore")
            m = re.search(r"csrf_bd_gem_nk\.?\s*[:=]\s*['\"]([a-f0-9]{10,})['\"]", html)
            if not m:
                m = re.search(r"csrf_bd_gem_nk\s*['\"]?\s*:\s*['\"]([a-f0-9]{10,})['\"]", html)
            if not m:
                raise RuntimeError("CSRF token not found in bidplus page")
            self.csrf = m.group(1)
            self.last_request_ms = time.time()
        except urllib.error.HTTPError as e:
            if e.code == 403:
                raise RuntimeError("GeM blocked this request (403). Pause and retry later.") from e
            raise

    def search(self, keyword: str, bid_status_type: str = "ongoing_bids",
               by_type: str = "all", pages: int = 999, max_hits: int | None = None):
        """Yield raw docs for all pages of one keyword search.

        bid_status_type: 'ongoing_bids' | 'cancelled_bids'
        by_type:         'all' | 'product' | 'service'
        """
        if not self.csrf:
            self.refresh_token()
        page = 1
        hits = 0
        while True:
            if pages is not None and page > pages:
                break
            payload = {
                "page": page,
                "param": {"searchBid": keyword, "searchType": "fullText"},
                "filter": {
                    "bidStatusType": bid_status_type,
                    "byType": by_type,
                    "highBidValue": "",
                    "byEndDate": {"from": "", "to": ""},
                    "sort": "Bid-End-Date-Oldest",
                },
            }
            body = urllib.parse.urlencode({
                "payload": json.dumps(payload),
                "csrf_bd_gem_nk": self.csrf,
            }).encode()
            req = urllib.request.Request(BIDS_DATA, data=body)
            self._throttle()
            resp = self.opener.open(req, timeout=REQUEST_TIMEOUT)
            data = json.loads(resp.read().decode("utf-8", "ignore"))
            self.last_request_ms = time.time()
            inner = data.get("response", {}).get("response", {})
            num_found = inner.get("numFound", 0)
            docs = inner.get("docs", [])
            if not docs:
                break
            for doc in docs:
                hits += 1
                if max_hits and hits > max_hits:
                    return
                yield doc
            start = inner.get("start", 0) + len(docs)
            if start >= num_found:
                break
            page += 1
            if page > 500:
                break  # safety


def doc_to_bid(keyword: str, doc: dict, bid_status_type: str) -> dict:
    """Map a SOLR bidplus doc -> our generic bid row (pre-normalisation)."""
    bid_id = str(doc.get("id", ""))
    number = (doc.get("b_bid_number") or [""])[0]
    cat = (doc.get("b_category_name") or [""])[0]
    full_cat = (doc.get("bd_category_name") or [""])[0]
    title_full = (full_cat and (cat + " " + full_cat)) or cat

    start = _first(doc, "final_start_date_sort")
    end = _first(doc, "final_end_date_sort")
    b_status = (doc.get("b_status") or [None])[0]
    b_type = (doc.get("b_bid_type") or [None])[0]
    ministry = (doc.get("ba_official_details_minName") or [""])[0]
    dept = (doc.get("ba_official_details_deptName") or [""])[0]
    org = (doc.get("ba_official_details_buyer") or [""])[0]

    return {
        "source": "gem",
        "bid_number": number,
        "title": title_full,
        "category": cat,
        "org_name": org,
        "ministry": ministry,
        "dept": dept,
        "buyer_contact": None,
        "est_value": None,
        "quantity": (doc.get("b_total_quantity") or [None])[0],
        "bid_type": _TYPE_MAP.get(b_type, str(b_type)),
        "status": _status_of(b_status, bid_status_type),
        "start_date": _iso(start),
        "end_date": _iso(end),
        "source_url": f"https://bidplus.gem.gov.in/showbidDocument/{bid_id}" if bid_id else None,
        "raw": json.dumps(doc, default=str),
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_keyword": keyword,
        "_id": bid_id,
    }


def _first(doc: dict, key: str):
    v = doc.get(key)
    return v[0] if isinstance(v, list) and v else v


def _iso(v: str | None) -> str | None:
    if not v:
        return None
    return v.replace("Z", "")[:19] if isinstance(v, str) else None


def _status_of(b_status, bid_status_type: str) -> str:
    if bid_status_type == "cancelled_bids":
        return "cancelled"
    return _STATUS_MAP.get(b_status, "unknown")


# ---------------------------------------------------------------------------
# Bid document (PDF) fetch + pdf text extraction
# ---------------------------------------------------------------------------

def fetch_bid_document(session: GemSession, bid_id: str, number: str,
                       out_dir: str = "data/pdfs") -> dict | None:
    """Download the bid-document PDF. Returns metadata dict (None on failure)."""
    url = BID_DOC.format(bid_id=bid_id)
    req = urllib.request.Request(url)
    session._throttle()
    try:
        resp = session.opener.open(req, timeout=REQUEST_TIMEOUT)
        raw = resp.read()
        session.last_request_ms = time.time()
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        return {"error": f"{type(e).__name__}: {getattr(e, 'code', e)}", "bid_number": number}
    if not raw.startswith(b"%PDF"):
        return {"error": "not a pdf", "bid_number": number}
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", number)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{safe}.pdf")
    Path(path).write_bytes(raw)
    body = _extract_pdf_text(path)
    return {"bid_number": number, "pdf_path": path, "body_text": body}


def _extract_pdf_text(path: str) -> str:
    try:
        import pypdf
        PdfReader = pypdf.PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            return ""
    try:
        reader = PdfReader(path)
        parts = []
        for p in reader.pages[:10]:
            parts.append(p.extract_text() or "")
        return "\n".join(parts)
    except Exception:
        return ""


def parse_bid_document_body(text: str) -> dict:
    """Pull structured fields out of a GeM bid-document text dump.

    GeM bid docs are bilingual (Hindi + English) with repeated token lines, so
    we use the stable English "/ Label" lines and take the next readable line.
    """
    if not text:
        return {}
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    out: dict = {}

    def grab(label_re: str, mode: str = "text", max_skip: int = 6) -> str | float | None:
        for i, line in enumerate(lines):
            if re.search(label_re, line, re.I):
                j = i + 1
                skipped = 0
                while j < len(lines) and skipped <= max_skip:
                    cand = lines[j]
                    skipped += 1
                    if mode == "text":
                        # skip Hindi-only token lines (short, no ASCII letters)
                        if len(cand) > 3 and re.search(r"[A-Za-z]", cand):
                            return cand
                    elif mode == "num":
                        if re.fullmatch(r"[\d,]+(?:\.\d+)?", cand):
                            return _to_number(cand)
                    elif mode == "int":
                        if re.fullmatch(r"[\d,]+", cand):
                            return int(re.sub(r"[^\d]", "", cand))
                    j += 1
                return None
        return None

    out["bid_number"] = grab(r"Bid\s+Number\s*[:#]", mode="text") or None
    org = grab(r"/Organisation\s*Name", mode="text")
    office = grab(r"/Office\s*Name", mode="text")
    out["org_name"] = org or None
    out["office"] = office or None
    qty = grab(r"/Total\s*Quantity", mode="num")
    if qty:
        out["quantity"] = qty
    est = grab(r"/?\s*Estimated\s*Bid\s*Value", mode="num")
    if est:
        out["est_value"] = est
    emd = grab(r"/EMD\s*Amount", mode="num")
    if emd:
        out["emd"] = emd
    cat = grab(r"/Item\s*Category", mode="text")
    if cat:
        out["category"] = cat
    sold_as = grab(r"Selling\s*As", mode="text") or grab(r"/Seller\s*Type", mode="text")
    if sold_as:
        out["selling_as"] = sold_as
    eval_m = grab(r"/Evaluation\s*Method", mode="text")
    if eval_m:
        out["evaluation"] = eval_m
    consignees = grab(r"/Consignees?\s*(?:and|/)", mode="text")
    if consignees:
        out["consignee_qty"] = consignees

    # Buyers email / contact (useful for outreach)
    email = None
    m = re.search(r"Buyer\s+Email\s*id\s*:\s*([\w.\-]+@[\w.\-]+)", text, re.I)
    if m:
        email = m.group(1)
    out["buyer_email"] = email

    # --- item spec block --------------------------------------------------
    rate = grab(r"Cooling\s*Capacity\s*Rating", mode="num")
    if rate:
        out["cooling_capacity_lph"] = rate
    storage = grab(r"Storage\s*Capacity\s*for", mode="num")
    if storage:
        out["storage_capacity_l"] = storage
    watts = grab(r"Maximum\s*Power\s*Consumption", mode="num")
    if watts:
        out["max_power_w"] = watts
    voltage = grab(r"Rated\s*Voltage", mode="text")
    if voltage:
        out["voltage"] = voltage

    # warranty lines (embedded further down)
    m = re.search(r"Warranty\s*:\s*(\d+)\s*month", text, re.I)
    if m:
        out["warranty_months"] = int(m.group(1))

    cap_txt = ""
    cap_class = out.get("cooling_capacity_lph")
    if cap_class:
        cap = int(cap_class)
        cap_txt = f"{cap} LPH"
        out["capacity_class"] = cap
        out["capacity_text"] = cap_txt
    else:
        from normalize import extract_capacity
        full = " ".join(lines)
        cc, ct = extract_capacity(full)
        if cc:
            out["capacity_class"] = cc
            out["capacity_text"] = ct
    return out


def _to_number(s: str) -> float:
    return float(re.sub(r"[^\d.]", "", s))
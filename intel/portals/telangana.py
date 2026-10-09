"""Telangana eProcurement (Vupadhi) engine - JS session app.

The home page auto-submits a session form and then server-renders a "Live
Tenders" card list (Tender ID, Enquiry/Notice Number, description, bid closing
date). Navigating to deep list pages terminates the session, so we only read
the home-page live-tender cards via headless Chrome. Rolling window of recent
live tenders - accumulate across weekly runs.
"""
from __future__ import annotations

import re
import time

from . import generic

_HOME = "https://tender.telangana.gov.in/"
_YEAR = 2026


def _driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    opts = Options()
    for a in ("--headless=new", "--no-sandbox", "--disable-gpu",
              "--ignore-certificate-errors", "--disable-dev-shm-usage",
              "--window-size=1400,3000"):
        opts.add_argument(a)
    return webdriver.Chrome(options=opts, service=Service())


def _closing_date(month_day_time: str) -> str | None:
    m = re.match(r"([A-Za-z]+)\s+(\d{1,2})\s+([0-9]{1,2}:[0-9]{2}\s*[APM]{2})",
                 month_day_time or "")
    if not m:
        return None
    months = {n.lower(): i for i, n in enumerate(
        ["January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"], 1)}
    mon = months.get(m.group(1).lower())
    if not mon:
        return None
    day = int(m.group(2))
    year = _YEAR
    now = time.localtime()
    if mon < now.tm_mon or (mon == now.tm_mon and day < now.tm_mday):
        year += 1
    return f"{day:02d}/{mon:02d}/{year} {m.group(3).upper()}"


def _living_rows(driver) -> list[dict]:
    driver.set_page_load_timeout(90)
    driver.get(_HOME)
    time.sleep(7)
    mark = driver.execute_script("return document.body.innerText;")
    start = mark.find("Live Tenders")
    end = mark.find("Welcome to Telangana State eProcurement Portal")
    if start < 0 or end < start:
        return []
    section = mark[start:end if end > start else start + 20000]
    rows = []
    for card in section.split("Bid Closing Date")[1:]:
        tl = [l.strip() for l in card.split("\n")]
        nonempty = [l for l in tl if l]
        if not nonempty:
            continue
        closing = _closing_date(" ".join(nonempty[:3]))
        tid_m = re.search(r"Tender ID:\s*([0-9]+)", card)
        if not tid_m:
            continue
        tid = tid_m.group(1)
        notice = None
        nm = re.search(r"Tender Notice Number:\s*([^\n]+)", card)
        if nm:
            notice = nm.group(1).strip()
        title = re.sub(r"\bTender ID:\s*[0-9]+\s*", " ", card)
        title = re.sub(r"Tender Notice Number:\s*[^\n]+\n?", " ", title)
        title = re.sub(r"\bEnquiry/IFB/\s*", " ", title)
        title = re.sub(r"^[A-Za-z]+\s+\d{1,2}\s+\d{1,2}:\d{2}\s*[APM]{2}", " ",
                       title, flags=re.MULTILINE)
        title = re.sub(r"\s*in\s+Division\s*No\s*:.*", " ", title, flags=re.S | re.I)
        title = generic._clean_title(title)
        org = None
        mo = re.search(r"in Division No:\s*([^.,\n]+)", card)
        if mo:
            org = mo.group(1).strip()
        if not title:
            continue
        rows.append({
            "bid_number": tid,
            "title": title[:400],
            "status": "open",
            "end_date": closing,
            "org_name": org or None,
            "source_url": _HOME,
            "_raw": card.strip()[:800],
        })
    return rows


def scrape_portal(portal: dict, keywords: list[str], pages: int = 3) -> list[dict]:
    try:
        d = _driver()
    except Exception:
        return []
    try:
        try:
            rows = _living_rows(d)
        except Exception:
            return []
    finally:
        try:
            d.quit()
        except Exception:
            pass
    return generic.base_filter(rows, keywords)
"""Bihar eproc2 (BSEDC/BELTRON) engine - Angular SPA.

The public "Open area Tender List" at
`/EPSV2Web/openarea/tenderListingPage.action` is only reliably rendered by a
JS-capable browser, so this engine drives headless Chrome via Selenium.
Home page itself is a login-gated Angular SPA; the open-area listing page is
public and server-renders the current active tenders.

Falls back to [] silently if Selenium/Chrome is unavailable.
"""
from __future__ import annotations

from . import generic

_LISTING_PATH = "/EPSV2Web/openarea/tenderListingPage.action"

# (0 SL, 1 Tender No, 2 Title, 3 NIT No dated, 4 Department, 5 Closing iso, 6 Remaining, 7)
_TENDER_HEADER = "SL No."


def _driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    opts = Options()
    for a in ("--headless=new", "--no-sandbox", "--disable-gpu",
              "--ignore-certificate-errors", "--disable-dev-shm-usage",
              "--window-size=1400,2600"):
        opts.add_argument(a)
    return webdriver.Chrome(options=opts, service=Service())


def _listing_rows(driver) -> list[dict]:
    driver.set_page_load_timeout(90)
    driver.get("https://eproc2.bihar.gov.in" + _LISTING_PATH)
    import time
    time.sleep(7)
    out = driver.execute_script(
        "var t=[];var tbl=document.querySelectorAll('table')[1];"
        "for(var i=1;i<tbl.rows.length;i++){var c=[];"
        "for(var j=0;j<tbl.rows[i].cells.length;j++)"
        "c.push(tbl.rows[i].cells[j].innerText.replace(/\\n/g,' ').trim());"
        "t.push(c);} return t;")
    rows = []
    for cells in out or []:
        if len(cells) < 5:
            continue
        try:
            int(cells[0])
        except Exception:
            continue
        tender_no = (cells[1] or "").strip()
        title = generic._clean_title(cells[2])
        if not title or generic._is_footer(title):
            continue
        rows.append({
            "bid_number": tender_no or cells[3][:60],
            "title": title[:400],
            "status": "open",
            "end_date": (cells[5] or "").strip(),
            "org_name": (cells[4] or "").strip() or None,
            "source_url": "https://eproc2.bihar.gov.in" + _LISTING_PATH,
            "_raw": " | ".join(c for c in cells),
        })
    return rows


def scrape_portal(portal: dict, keywords: list[str], pages: int = 3) -> list[dict]:
    try:
        d = _driver()
    except Exception:
        return []
    try:
        try:
            rows = _listing_rows(d)
        except Exception:
            return []
    finally:
        try:
            d.quit()
        except Exception:
            pass
    return generic.base_filter(rows, keywords)
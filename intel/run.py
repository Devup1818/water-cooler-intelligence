"""Water Cooler Govt Tender Intelligence - CLI.

Usage:
  python run.py init                # create SQLite schema
  python run.py scrape --kw "water cooler" --pages 3 [--only test]
  python run.py scrape-cppp         # best-effort CPPP (usually captcha-blocked)
  python run.py docs --limit 5      # fetch bid-document PDFs for captured bids
  python run.py import --csv data/awards.csv
  python run.py seed                # load your two known contracts as sample awards
  python run.py report              # generate Markdown + Excel report
  python run.py dashboard           # local web UI over all captured tenders
  python run.py all --pages 3       # scrape -> import -> docs -> report
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import db as dbm
import analytics
import report as report_mod
import dashboard
from normalize import classify_seller, extract_capacity, extract_segment, extract_state, is_msme, is_relevant


# ---------------------------------------------------------------------------
# scrape
# ---------------------------------------------------------------------------
def cmd_scrape(args) -> None:
    import gem
    conn = dbm.init()
    session = gem.GemSession()
    keywords = args.kw
    if not keywords:
        try:
            from config import DEFAULT_GEM_KEYWORDS
            keywords = DEFAULT_GEM_KEYWORDS
        except ImportError:
            keywords = ["Drinking Water Coolers", "Water Cooler V4", "Water Cooler V3",
                        "Coolers ISI Marked", "Bulk Water Dispensers", "Water Dispenser",
                        "Water Cooler cum Purifier"]
    status = args.status
    total = 0
    started = dbm.now_iso()
    for kw in keywords:
        print(f"[gem] searching '{kw}' status={status} ...")
        before = total
        try:
            for doc in session.search(kw, bid_status_type=status, pages=args.pages):
                bid = gem.doc_to_bid(kw, doc, status)
                bid = enrich_bid(bid)
                dbm.upsert_bid(conn, bid)
                total += 1
        except RuntimeError as e:
            print(f"[gem] stopping: {e}")
            break
        except Exception as e:
            print(f"[gem] error on '{kw}': {e}")
        conn.commit()
        print(f"[gem] '{kw}' -> {total - before} rows")
        time.sleep(1)
    conn.commit()
    dbm.log_run(conn, "scrape_gem", f"rows={total} kw={keywords} status={status}", started)
    print(f"[gem] done, {total} bids upserted.")


def enrich_bid(bid: dict) -> dict:
    text = " ".join(str(bid.get(k) or "") for k in ("title", "category", "org_name",
                                                    "ministry", "dept")).lower()
    cap, cap_txt = extract_capacity(text)
    if cap is None:
        cap, cap_txt = extract_capacity(bid.get("category") or "")
    bid["capacity_class"] = cap
    bid["capacity_text"] = cap_txt
    bid["relevant"] = 1 if is_relevant(text) else 0
    bid["state"] = extract_state(text)
    bid["segment"] = extract_segment(bid.get("org_name") or "", bid.get("ministry") or "")
    return bid


def cmd_scrape_cppp(args) -> None:
    import cppp
    conn = dbm.init()
    started = dbm.now_iso()
    rows = cppp.search_form_cppp(["water cooler"], pages=3)
    if not rows:
        rows = cppp.scrape_active_tenders(max_pages=2)
        rows = cppp.keyword_filter(rows, ["water cooler", "watercooler", "water dispenser"])
    n = 0
    for r in rows[:args.limit]:
        dbm.upsert_bid(conn, enrich_bid({**r, "status": "archived", "scraped_at": dbm.now_iso()}))
        n += 1
    conn.commit()
    dbm.log_run(conn, "scrape_cppp", f"rows={n}", started)
    print(f"[cppp] done, {n} rows.")


def cmd_scrape_portal(args) -> None:
    """Run the multi-portal sweep (state/central/health portals)."""
    from config import PORTAL_KEYWORDS
    from portals import all_portals, portal as find_portal
    import portals as portals_mod

    if getattr(args, "list", False):
        for p in all_portals():
            print(f"{p['code']:8} {p['engine']:9} {p.get('type'):7} "
                  f"{str(p.get('state')):16} {p['name']}  "
                  f"[verified={p.get('verified')}]")
        return

    conn = dbm.init()
    started = dbm.now_iso()

    if args.portal:
        codes = [c.strip() for c in args.portal.split(",") if c.strip()]
        plist = [p for p in all_portals() if p["code"] in codes]
    elif args.state:
        plist = [p for p in all_portals() if p.get("state", "").lower() == args.state.lower()
                 or (p.get("state") == "ALL" and p.get("type") == "central")]
    elif args.type:
        plist = [p for p in all_portals() if p.get("type") == args.type]
    else:
        plist = all_portals()

    if not plist:
        print("[portals] no portals matched (see --list)")
        return

    # default: capture EVERY tender row (full market universe); only apply
    # local keyword filtering when explicitly requested via --kw.
    kws = args.kw or (PORTAL_KEYWORDS if args.filter else [])
    total = 0
    relevant = 0
    for p in plist:
        print(f"[portals] {p['code']} ({p['name']}) ...")
        before = total
        try:
            rows = portals_mod.scrape_portal(p, kws, pages=args.pages)
            for r in rows:
                r["status"] = "published"
                e = enrich_bid({**r, "scraped_at": dbm.now_iso()})
                dbm.upsert_bid(conn, e)
                relevant += int(e.get("relevant") == 1)
                total += 1
        except Exception as e:
            print(f"[portals] {p['code']} failed: {e}")
        conn.commit()
        got = total - before
        print(f"[portals] {p['code']} -> {got} rows")
        time.sleep(1)
    conn.commit()
    dbm.log_run(conn, "scrape_portals", f"rows={total} relevant={relevant} portals={len(plist)} kw={kws}")
    print(f"[portals] done, {total} rows ({relevant} water-cooler-relevant) from {len(plist)} portals.")


def cmd_docs(args) -> None:
    import gem
    conn = dbm.init()
    rows = conn.execute("""
        SELECT raw FROM bids
        WHERE source='gem' AND relevant=1 AND bid_number IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM bid_docs d WHERE d.bid_number = bids.bid_number)
        ORDER BY quantity DESC, end_date DESC
        LIMIT ?
    """, (args.limit,)).fetchall()
    if not rows:
        rows = conn.execute("SELECT raw FROM bids WHERE source='gem' LIMIT ?", (args.limit,)).fetchall()
    session = gem.GemSession()
    done, errors = 0, 0
    for row in rows:
        if isinstance(row, sqlite3.Row):
            raw = json.loads(row["raw"])
        else:
            raw = json.loads(row[0] if isinstance(row, tuple) else row)
        bid_id = raw.get("_id") or str(raw.get("id"))
        number = (raw.get("b_bid_number") or [""])[0]
        if not bid_id:
            continue
        res = gem.fetch_bid_document(session, bid_id, number)
        if res.get("body_text"):
            fields = gem.parse_bid_document_body(res["body_text"])
            dbm.upsert_bid_doc(conn, {
                "bid_number": number, "pdf_path": res["pdf_path"],
                "body_text": res["body_text"][:200000],
                "fields": json.dumps(fields), "fetched_at": dbm.now_iso(),
            })
            upd = {}
            if fields.get("capacity_class"):
                upd["capacity_class"] = fields["capacity_class"]
                upd["capacity_text"] = fields.get("capacity_text")
            if fields.get("est_value"):
                upd["est_value"] = fields["est_value"]
            if fields.get("org_name"):
                upd["org_name"] = fields["org_name"]
            if fields.get("quantity"):
                upd["quantity"] = fields["quantity"]
            if fields.get("category"):
                upd["category"] = fields["category"]
            if upd:
                sets = ", ".join(f"{k}=?" for k in upd)
                conn.execute(f"UPDATE bids SET {sets} WHERE bid_number=?", (*upd.values(), number))
            done += 1
        else:
            errors += 1
        conn.commit()
        time.sleep(1)
    print(f"[docs] fetched {done} docs, {errors} failed.")


# ---------------------------------------------------------------------------
# import award csv
# ---------------------------------------------------------------------------
def cmd_import(args) -> None:
    conn = dbm.init()
    path = Path(args.csv)
    n = 0
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not (row.get("seller_name") or "").strip():
                continue
            seller_type = (row.get("seller_type") or "").strip() or classify_seller(row["seller_name"])
            award = {
                "source": (row.get("source") or "manual").strip() or "manual",
                "tender_id": (row.get("tender_id") or "").strip() or None,
                "award_date": (row.get("award_date") or "").strip() or None,
                "buyer_org": (row.get("buyer_org") or "").strip() or None,
                "buyer_state": (row.get("buyer_state") or "").strip() or None,
                "segment": (row.get("segment") or "").strip() or None,
                "seller_name": row["seller_name"].strip(),
                "seller_id": (row.get("seller_id") or "").strip() or None,
                "seller_type": seller_type,
                "capacity_class": _num(row.get("capacity_class")) or None,
                "qty": _num(row.get("qty")),
                "unit_price": _num(row.get("unit_price")),
                "total_value": _num(row.get("total_value")),
                "currency": (row.get("currency") or "INR").strip(),
                "remarks": (row.get("remarks") or "").strip() or None,
                "source_url": (row.get("source_url") or "").strip() or None,
                "entered_at": dbm.now_iso(),
            }
            if award["capacity_class"]:
                award["total_value"] = award["total_value"] or (
                    award["unit_price"] * award["qty"] if award["unit_price"] and award["qty"] else None)
            dbm.insert_award(conn, award)
            if award["seller_name"]:
                dbm.upsert_seller(conn, {
                    "seller_id": f"manual:{sanitize_id(award['seller_name'])}",
                    "seller_name": award["seller_name"], "seller_type": seller_type,
                    "role_source": "manual", "msme": 0, "contact": None,
                    "state": award["buyer_state"], "updated_at": dbm.now_iso(),
                })
            n += 1
    conn.commit()
    dbm.log_run(conn, "import_awards", f"rows={n} file={path.name}")
    print(f"[import] {n} awards inserted from {path.name}")


def _num(v):
    if v is None or str(v).strip() == "":
        return None
    return float(str(v).replace(",", "").replace("\u20b9", "").strip())


def sanitize_id(s: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9]+", "_", s.lower())[:60]


# ---------------------------------------------------------------------------
# seed sample awards from the two real contracts
# ---------------------------------------------------------------------------
def cmd_seed(args) -> None:
    conn = dbm.init()
    sample = [
        {"source": "gem", "tender_id": "GEM/2026/B/7094486", "award_date": "2026-03-18",
         "buyer_org": "North Western Railway", "buyer_state": "Rajasthan", "segment": "Railways",
         "seller_name": "Cool Home (India) - Fresco Casa", "seller_type": "OEM", "capacity_class": 150,
         "qty": 120, "unit_price": 35835, "total_value": 4300200, "remarks": "Real contract GEMC-511687751472352"},
        {"source": "gem", "tender_id": "GEM/2026/B/7299831", "award_date": "2026-04-15",
         "buyer_org": "Northern Railway (Moradabad)", "buyer_state": "Uttar Pradesh", "segment": "Railways",
         "seller_name": "Cool Home (India) - Fresco Casa", "seller_type": "OEM", "capacity_class": 150,
         "qty": 29, "unit_price": 35200, "total_value": 1020800, "remarks": "Rejected batch GEMC-511687763924679"},
        {"source": "manual", "award_date": "2026-08-05", "buyer_org": "Sample State PSU",
         "buyer_state": "Madhya Pradesh", "segment": "Power", "seller_name": "Sample Competitor Industries",
         "seller_type": "OEM", "capacity_class": 120, "qty": 40, "unit_price": 42000, "total_value": 1680000,
         "remarks": "Example row - replace with real data"},
    ]
    for a in sample:
        dbm.insert_award(conn, {**a, "entered_at": dbm.now_iso()})
        dbm.upsert_seller(conn, {
            "seller_id": "manual:" + sanitize_id(a["seller_name"]), "seller_name": a["seller_name"],
            "seller_type": a["seller_type"], "role_source": "manual", "msme": 0,
            "contact": None, "state": a["buyer_state"], "updated_at": dbm.now_iso(),
        })
    conn.commit()
    print("[seed] sample awards inserted.")


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def cmd_report(args) -> None:
    conn = dbm.init()
    started = dbm.now_iso()
    out = report_mod.build(conn)
    dbm.log_run(conn, "report", f"md={out['markdown']} xlsx={out['excel']}", started)
    print(f"[report] {out['markdown']}")
    print(f"[report] {out['excel']}")
    print(analytics.summary_text(conn))


def _run_all(args):
    cmd_scrape(args)
    if args.portals:
        cmd_scrape_portal(args)
    cmd_scrape_cppp(args)
    cmd_docs(args)
    cmd_report(args)


def main(argv=None):
    p = argparse.ArgumentParser(description="Water Cooler Govt Tender Intelligence")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scrape")
    s.add_argument("--kw", action="append", help="keyword (repeatable; default water cooler)")
    s.add_argument("--pages", type=int, default=5)
    s.add_argument("--status", default="ongoing_bids",
                   choices=["ongoing_bids", "cancelled_bids"])
    s.set_defaults(fn=cmd_scrape)

    c = sub.add_parser("scrape-cppp")
    c.add_argument("--limit", type=int, default=200)
    c.set_defaults(fn=cmd_scrape_cppp)

    pp = sub.add_parser("scrape-portal")
    pp.add_argument("--portal", help="comma-separated portal codes (e.g. up,mh)")
    pp.add_argument("--state", help="run state portals for one state only")
    pp.add_argument("--type", choices=["central", "state", "health"])
    pp.add_argument("--kw", action="append", help="keyword (repeatable; also enables local filtering)")
    pp.add_argument("--filter", action="store_true",
                    help="apply PORTAL_KEYWORDS filtering before storing (default: keep all rows)")
    pp.add_argument("--pages", type=int, default=3)
    pp.add_argument("--list", action="store_true",
                    help="print portal registry and exit")
    pp.set_defaults(fn=cmd_scrape_portal)

    d = sub.add_parser("docs")
    d.add_argument("--limit", type=int, default=5)
    d.set_defaults(fn=cmd_docs)

    i = sub.add_parser("import")
    i.add_argument("--csv", default="data/awards.csv")
    i.set_defaults(fn=cmd_import)

    sub.add_parser("seed").set_defaults(fn=cmd_seed)
    sub.add_parser("report").set_defaults(fn=cmd_report)

    dsh = sub.add_parser("dashboard", help="serve local web dashboard (default port 8787)")
    dsh.add_argument("--port", type=int, default=8787)
    dsh.set_defaults(fn=dashboard.cmd_dashboard)

    a = sub.add_parser("all")
    a.add_argument("--pages", type=int, default=5)
    a.add_argument("--status", default="ongoing_bids")
    a.add_argument("--portals", action="store_true",
                   help="also run the state/central/health portal sweep")
    a.set_defaults(fn=lambda argv: _run_all(argv))

    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main(sys.argv[1:])
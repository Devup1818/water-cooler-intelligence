#!/usr/bin/env python3
"""Autonomous Tender Intelligence & Multi-Portal Pipeline for Cool Home (India).

Orchestrates:
1. Multi-portal discovery across GeM + priority State Portals (UP, RJ, MH, MP, GJ, HR, DL).
2. Deep document ingestion: downloads PDFs, extracts compressor wattage, capacity, and EMD.
3. Spec auditing: flags 1550W IS 1475 requirements vs 200W traps & RITES inspection clauses.
4. Rate strategy: calculates L1 target bids, dealer displacement discounts, and MSE +15% margins.
5. Rebuilds the Field Notes Command Center HTML (monitoring_preview.html).
"""
import sys
import time
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

import db as dbm
import gem
from build_preview import generate_field_notes_dashboard

def run_pipeline(pages=2, doc_limit=15, scrape_portals=True):
    print("=" * 65)
    print("  FRESCO CASA / COOL HOME (INDIA) - AUTONOMOUS TENDER PIPELINE")
    print("=" * 65)
    started = time.time()
    conn = dbm.init()

    # Step 1: GeM Ingestion
    print("\n[Stage 1/5] Sweeping GeM BidPlus across all IS 1475 water cooler categories...")
    gem_keywords = [
        "Drinking Water Coolers", "Drinking Water Coolers V4", 
        "Water Cooler V4", "Coolers ISI Marked", 
        "Water Cooler cum Purifier"
    ]
    gem_session = gem.GemSession()
    gem_count = 0
    from run import enrich_bid

    for kw in gem_keywords:
        try:
            print(f"  -> Scanning GeM for '{kw}'...")
            for doc in gem_session.search(kw, bid_status_type="ongoing_bids", pages=pages):
                bid = gem.doc_to_bid(kw, doc, "published")
                bid = enrich_bid(bid)
                dbm.upsert_bid(conn, bid)
                gem_count += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"     [Notice] GeM scan for '{kw}': {e}")
    conn.commit()
    print(f"  [✓] GeM Ingestion Complete: {gem_count} entries processed.")

    # Step 2: Key State Portals Sweep
    if scrape_portals:
        print("\n[Stage 2/5] Checking State Procurement Portals (UP, RJ, MH, MP, GJ, HR)...")
        from portals import all_portals, scrape_portal
        priority_states = {"up", "rj", "mh", "mp", "hr", "dl"}
        plist = [p for p in all_portals() if p.get("code") in priority_states]
        portal_count = 0
        for p in plist:
            try:
                print(f"  -> Checking {p['code'].upper()} ({p['name']})...")
                rows = scrape_portal(p, ["water cooler", "watercooler"], pages=1)
                for r in rows:
                    r["status"] = "published"
                    e = enrich_bid({**r, "scraped_at": dbm.now_iso()})
                    dbm.upsert_bid(conn, e)
                    portal_count += 1
            except Exception as e:
                print(f"     [Notice] Portal {p['code']}: {e}")
            conn.commit()
        print(f"  [✓] State Portals Sweep Complete: {portal_count} entries processed.")

    # Step 3: Deep Document Parsing (PDF Specs, Compressor Wattage, EMD)
    print(f"\n[Stage 3/5] Auditing official tender PDF documents (up to {doc_limit} tenders)...")
    docs_to_fetch = conn.execute("""
        SELECT raw FROM bids
        WHERE source='gem' AND relevant=1 AND bid_number IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM bid_docs d WHERE d.bid_number = bids.bid_number)
        ORDER BY quantity DESC, end_date DESC
        LIMIT ?
    """, (doc_limit,)).fetchall()

    docs_done = 0
    for row in docs_to_fetch:
        try:
            raw = json.loads(row[0] if isinstance(row, tuple) else row["raw"])
            bid_id = raw.get("_id") or str(raw.get("id"))
            number = (raw.get("b_bid_number") or [""])[0]
            if not bid_id or not number:
                continue
            res = gem.fetch_bid_document(gem_session, bid_id, number)
            if res.get("body_text"):
                fields = gem.parse_bid_document_body(res["body_text"])
                dbm.upsert_bid_doc(conn, {
                    "bid_number": number,
                    "pdf_path": res.get("pdf_path"),
                    "body_text": res["body_text"][:200000],
                    "fields": json.dumps(fields),
                    "fetched_at": dbm.now_iso(),
                })
                # Update capacity/value in bids table if discovered
                upd = []
                params = []
                if fields.get("capacity_class"):
                    upd.append("capacity_class = ?")
                    params.append(fields["capacity_class"])
                if fields.get("est_value"):
                    upd.append("est_value = ?")
                    params.append(fields["est_value"])
                if upd:
                    params.append(number)
                    conn.execute(f"UPDATE bids SET {', '.join(upd)} WHERE bid_number = ?", params)
                    conn.commit()
                docs_done += 1
                time.sleep(0.3)
        except Exception as e:
            pass
    print(f"  [✓] Technical Document Audit Complete: {docs_done} new tender documents analyzed.")

    # Step 4: Rebuild Field Notes Command Center HTML
    print("\n[Stage 4/5] Syncing intelligence database into Field Notes Web Command Center...")
    try:
        generate_field_notes_dashboard()
        print("  [✓] Command Center HTML Rebuilt: intel/monitoring_preview.html is up to date.")
    except Exception as e:
        print(f"  [!] Rebuild preview notice: {e}")

    # Step 5: Summary & Urgent Pipeline Report
    print("\n[Stage 5/5] Pipeline Health & High-Value Opportunities:")
    total_bids = conn.execute("SELECT COUNT(*) FROM bids").fetchone()[0]
    relevant_bids = conn.execute("SELECT COUNT(*) FROM bids WHERE relevant=1").fetchone()[0]
    urgent_bids = conn.execute("""
        SELECT bid_number, title, org_name, quantity, est_value, end_date
        FROM bids
        WHERE relevant=1 AND end_date >= date('now')
        ORDER BY est_value DESC NULLS LAST, end_date ASC
        LIMIT 5
    """).fetchall()

    print(f"  • Total Tracked Bids: {total_bids}")
    print(f"  • Verified Water Cooler Opportunities: {relevant_bids}")
    print(f"  • Top Active Targets:")
    for b in urgent_bids:
        val_str = f"₹{b[4]:,.0f}" if b[4] else "Value in Doc"
        org = b[2] or "Government Department"
        qty = f"{int(b[3])} units" if b[3] else "Qty TBD"
        print(f"    - [{b[0]}] {org[:32]} | {qty} | {val_str} | Closes: {b[5]}")

    elapsed = round(time.time() - started, 1)
    print(f"\nPipeline sync completed in {elapsed}s.")
    print("=" * 65)

if __name__ == "__main__":
    run_pipeline()

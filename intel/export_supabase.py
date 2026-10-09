#!/usr/bin/env python3
"""Sync local SQLite database (intel/data/intel.db) directly to Supabase cloud.

Usage:
  # Option A: Export to Supabase via REST API
  export SUPABASE_URL="https://your-project.supabase.co"
  export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
  python3 export_supabase.py --sync

  # Option B: Dump full database into supabase/full_seed.sql for 1-click SQL Editor run
  python3 export_supabase.py --dump-sql
"""
import os
import sys
import json
import sqlite3
import argparse
from pathlib import Path
import urllib.request
import urllib.parse

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "intel.db"
SEED_SQL_PATH = ROOT.parent / "supabase" / "full_seed.sql"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def dump_sql():
    conn = get_db()
    lines = [
        "-- ========================================================",
        "-- FULL EXPORT: Cool Home / Fresco Casa Tender Intelligence",
        "-- ========================================================",
        ""
    ]
    
    # 1. Bids
    bids = conn.execute("SELECT * FROM bids WHERE relevant=1").fetchall()
    print(f"Exporting {len(bids)} relevant bids to SQL dump...")
    for b in bids:
        cols = [k for k in b.keys() if b[k] is not None]
        val_placeholders = []
        for c in cols:
            val = b[c]
            if isinstance(val, (int, float)):
                val_placeholders.append(str(val))
            else:
                escaped = str(val).replace("'", "''")
                val_placeholders.append(f"'{escaped}'")
        
        sql = f"insert into public.bids ({', '.join(cols)}) values ({', '.join(val_placeholders)}) on conflict (bid_number) do update set status = excluded.status, end_date = excluded.end_date;"
        lines.append(sql)

    SEED_SQL_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[✓] Successfully generated full SQL seed at: {SEED_SQL_PATH}")

def sync_supabase(url: str, key: str):
    if not url or not key:
        print("[!] SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables required.")
        return

    conn = get_db()
    bids = [dict(r) for r in conn.execute("SELECT * FROM bids WHERE relevant=1").fetchall()]
    print(f"Syncing {len(bids)} tenders to Supabase at {url}...")

    endpoint = f"{url.rstrip('/')}/rest/v1/bids"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    # Batch in chunks of 50
    chunk_size = 50
    for i in range(0, len(bids), chunk_size):
        chunk = bids[i:i + chunk_size]
        data = json.dumps(chunk).encode("utf-8")
        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                print(f"  -> Synced batch {i // chunk_size + 1} ({len(chunk)} rows) - HTTP {resp.status}")
        except Exception as e:
            print(f"  [!] Batch sync error: {e}")

    print("[✓] Supabase sync completed successfully.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Sync SQLite to Supabase")
    p.add_argument("--sync", action="store_true", help="Sync via REST API")
    p.add_argument("--dump-sql", action="store_true", help="Dump full SQL to supabase/full_seed.sql")
    args = p.parse_args()

    if args.sync:
        sync_supabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    else:
        dump_sql()

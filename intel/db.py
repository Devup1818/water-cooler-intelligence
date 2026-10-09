"""SQLite storage layer for the Water Cooler intelligence pipeline.

Tables:
  bids          - scraped GeM / CPPP tenders (one row per tender/bid)
  bid_docs      - fetched GeM bid-document PDFs (raw bytes + parsed body text)
  sellers       - normalised seller/winner directory (OEM vs dealer vs trader)
  awards        - the award log (winner, rate, qty) - primary source = manual CSV
  runs          - scrapes/imports/reports history
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS bids (
    source          TEXT NOT NULL,             -- 'gem' | 'drupal' | 'nprocure' | 'generic' ...
    portal_code     TEXT,                      -- which portal/state the row came from
    bid_number      TEXT NOT NULL,             -- e.g. GEM/2026/B/7094486 or tender ref
    title           TEXT,
    category        TEXT,
    org_name        TEXT,
    ministry        TEXT,
    dept            TEXT,
    buyer_contact   TEXT,
    est_value       REAL,
    quantity        REAL,
    capacity_class  INTEGER,                   -- normalised
    capacity_text   TEXT,                      -- raw match
    relevant        INTEGER DEFAULT 1,         -- 1 = water-cooler collocation found
    state           TEXT,
    segment         TEXT,
    bid_type        TEXT,                      -- product / service / boq ...
    status          TEXT,                      -- ongoing / cancelled / awarded / archived
    start_date      TEXT,
    end_date        TEXT,
    source_url      TEXT,
    raw             TEXT,                      -- JSON blob of source doc
    scraped_at      TEXT,
    PRIMARY KEY (source, bid_number)
);
CREATE INDEX IF NOT EXISTS idx_bids_capacity  ON bids(capacity_class);
CREATE INDEX IF NOT EXISTS idx_bids_status    ON bids(status);
CREATE INDEX IF NOT EXISTS idx_bids_org       ON bids(org_name);
CREATE INDEX IF NOT EXISTS idx_bids_state     ON bids(state);

CREATE TABLE IF NOT EXISTS bid_docs (
    bid_number   TEXT PRIMARY KEY,
    pdf_path     TEXT,
    body_text    TEXT,
    fields       TEXT,                         -- parsed key fields JSON
    fetched_at   TEXT
);

CREATE TABLE IF NOT EXISTS sellers (
    seller_id         TEXT PRIMARY KEY,
    seller_name       TEXT,
    seller_type       TEXT,                    -- OEM / Authorized Dealer / Trader / Distributor
    role_source       TEXT,                    -- 'name' | 'geam' | 'manual'
    msme              INTEGER DEFAULT 0,
    contact           TEXT,
    state             TEXT,
    updated_at        TEXT
);

CREATE TABLE IF NOT EXISTS awards (
    award_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    source          TEXT DEFAULT 'manual',
    tender_id       TEXT,                      -- links to bids.bid_number when known
    award_date      TEXT,
    buyer_org       TEXT,
    buyer_state     TEXT,
    segment         TEXT,
    seller_name     TEXT NOT NULL,
    seller_id       TEXT,
    seller_type     TEXT,
    capacity_class  INTEGER,
    qty             REAL,
    unit_price      REAL,
    total_value     REAL,
    currency        TEXT DEFAULT 'INR',
    remarks         TEXT,
    source_url      TEXT,
    entered_at      TEXT
);
CREATE INDEX IF NOT EXISTS idx_awards_seller ON awards(seller_name);
CREATE INDEX IF NOT EXISTS idx_awards_date   ON awards(award_date);

CREATE TABLE IF NOT EXISTS runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at  TEXT,
    finished_at TEXT,
    kind        TEXT,                          -- scrape_gem / scrape_cppp / import_awards / report
    detail      TEXT
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(db_path: str = DB_PATH) -> sqlite3.Connection:
    if os.path.dirname(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = connect(db_path)
    conn.executescript(SCHEMA)
    # migrate older DBs: add portal_code, populate for legacy rows
    cols = [r[1] for r in conn.execute("PRAGMA table_info(bids)").fetchall()]
    if "portal_code" not in cols:
        conn.execute("ALTER TABLE bids ADD COLUMN portal_code TEXT")
        conn.execute("UPDATE bids SET portal_code='gem'  WHERE source='gem'")
        conn.execute("UPDATE bids SET portal_code='cppp' WHERE source='cppp' OR portal_code IS NULL")
    conn.commit()
    return conn


def upsert_bid(conn: sqlite3.Connection, bid: dict) -> None:
    cols = [
        "source", "portal_code", "bid_number", "title", "category", "org_name", "ministry",
        "dept", "buyer_contact", "est_value", "quantity", "capacity_class",
        "capacity_text", "relevant", "state", "segment", "bid_type", "status",
        "start_date", "end_date", "source_url", "raw", "scraped_at",
    ]
    sql = f"""
        INSERT INTO bids ({', '.join(cols)})
        VALUES ({', '.join(':' + c for c in cols)})
        ON CONFLICT(source, bid_number) DO UPDATE SET
            title=excluded.title,
            category=excluded.category,
            org_name=excluded.org_name,
            ministry=excluded.ministry,
            dept=excluded.dept,
            quantity=excluded.quantity,
            capacity_class=excluded.capacity_class,
            capacity_text=excluded.capacity_text,
            relevant=excluded.relevant,
            segment=excluded.segment,
            state=excluded.state,
            bid_type=excluded.bid_type,
            status=excluded.status,
            end_date=COALESCE(NULLIF(excluded.end_date,''), bids.end_date),
            est_value=COALESCE(excluded.est_value, bids.est_value),
            raw=excluded.raw,
            scraped_at=excluded.scraped_at
    """
    conn.execute(sql, {k: bid.get(k) for k in cols})


def upsert_bid_doc(conn: sqlite3.Connection, doc: dict) -> None:
    conn.execute(
        """INSERT INTO bid_docs (bid_number, pdf_path, body_text, fields, fetched_at)
           VALUES (:bid_number, :pdf_path, :body_text, :fields, :fetched_at)
           ON CONFLICT(bid_number) DO UPDATE SET
             pdf_path=excluded.pdf_path, body_text=excluded.body_text,
             fields=excluded.fields, fetched_at=excluded.fetched_at""",
        doc,
    )


def upsert_seller(conn: sqlite3.Connection, seller: dict) -> None:
    conn.execute(
        """INSERT INTO sellers (seller_id, seller_name, seller_type, role_source,
                msme, contact, state, updated_at)
           VALUES (:seller_id, :seller_name, :seller_type, :role_source,
                   :msme, :contact, :state, :updated_at)
           ON CONFLICT(seller_id) DO UPDATE SET
             seller_name=excluded.seller_name,
             seller_type=CASE WHEN sellers.role_source='manual' THEN sellers.seller_type
                              ELSE COALESCE(excluded.seller_type, sellers.seller_type) END,
             role_source=CASE WHEN sellers.role_source='manual' THEN 'manual'
                              ELSE COALESCE(excluded.role_source, sellers.role_source) END,
             contact=COALESCE(excluded.contact, sellers.contact),
             state=excluded.state,
             updated_at=excluded.updated_at""",
        seller,
    )


def insert_award(conn: sqlite3.Connection, award: dict) -> None:
    cols = ["source", "tender_id", "award_date", "buyer_org", "buyer_state", "segment",
            "seller_name", "seller_id", "seller_type", "capacity_class", "qty",
            "unit_price", "total_value", "currency", "remarks", "source_url", "entered_at"]
    conn.execute(
        f"INSERT INTO awards ({', '.join(cols)}) VALUES ({', '.join(':' + c for c in cols)})",
        {k: award.get(k) for k in cols},
    )


def log_run(conn: sqlite3.Connection, kind: str, detail: str = "", started: str | None = None) -> None:
    conn.execute(
        "INSERT INTO runs (started_at, finished_at, kind, detail) VALUES (?, ?, ?, ?)",
        (started or now_iso(), now_iso(), kind, detail[:4000]),
    )
    conn.commit()
"""Market analytics over the bids + awards tables.

Outputs (dict of tabular results) consumed by report.py:
  market_size      - publish-volume and est-value by month / state / segment
  opportunity      - currently-open bids, sorted (your hunting list)
  capacity_mix     - how many tenders per capacity class
  buyer_profile    - top buyers by # tenders and est value
  winner_map       - who wins (from award log): by seller, by seller_type
  rate_bench       - unit-price stats per capacity class from the award log
  competitors      - seller share of awards
  pipeline_value   - total est. value of captured bids (market proxy)
"""
from __future__ import annotations

import sqlite3
from collections import defaultdict

from config import RATE_BANDS
from normalize import format_inr


def _q(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    return conn.execute(sql, params).fetchall()


def market_size(conn: sqlite3.Connection) -> dict:
    def cnt(where: str) -> int:
        return conn.execute(f"SELECT COUNT(*) c FROM bids WHERE {where}").fetchone()["c"]

    relevant = cnt("relevant=1")
    open_cnt = cnt("status='published' AND relevant=1")
    total_cnt = cnt("1=1")
    with_value = conn.execute(
        "SELECT SUM(est_value) s, COUNT(*) c FROM bids WHERE est_value IS NOT NULL AND relevant=1"
    ).fetchone()
    by_month = conn.execute("""
        SELECT substr(COALESCE(start_date, end_date),1,7) ym, COUNT(*) c
        FROM bids WHERE relevant=1 GROUP BY 1 ORDER BY 1""").fetchall()
    by_capacity = conn.execute("""
        SELECT COALESCE(capacity_class, 0) cap, COUNT(*) c FROM bids
        WHERE relevant=1 GROUP BY 1 ORDER BY 1""").fetchall()
    return {
        "relevant": relevant,
        "open": open_cnt,
        "total": total_cnt,
        "est_value_sum": with_value["s"] if with_value else None,
        "est_value_rows": with_value["c"] if with_value else 0,
        "by_month": list(by_month),
        "by_capacity": list(by_capacity),
    }


def opportunity(conn: sqlite3.Connection, limit: int = 100) -> list[sqlite3.Row]:
    return _q(conn, """
        SELECT bid_number, title, org_name, ministry, quantity, capacity_class,
               end_date, est_value, source_url, portal_code
        FROM bids
        WHERE status IN ('published','open','ongoing') AND relevant=1
        ORDER BY end_date ASC
        LIMIT ?""", (limit,))


def buyer_profile(conn: sqlite3.Connection, limit: int = 15) -> list[sqlite3.Row]:
    return _q(conn, """
        SELECT COALESCE(NULLIF(org_name,''), NULLIF(ministry,''), 'Unknown') buyer,
               COALESCE(segment, 'Other') segment,
               COUNT(*) tenders,
               SUM(est_value) est_value,
               SUM(quantity) qty
        FROM bids
        WHERE relevant=1
        GROUP BY buyer, segment
        ORDER BY est_value DESC NULLS LAST, tenders DESC
        LIMIT ?""", (limit,))


def capacity_mix(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return _q(conn, """
        SELECT capacity_class, COUNT(*) tenders, SUM(quantity) qty
        FROM bids WHERE capacity_class IS NOT NULL AND relevant=1
        GROUP BY capacity_class ORDER BY capacity_class""")


def winner_map(conn: sqlite3.Connection) -> dict:
    ex = """COALESCE(remarks,'') NOT LIKE '%example%' AND COALESCE(remarks,'') NOT LIKE '%sample%'"""
    awards = conn.execute(f"SELECT COUNT(*) c FROM awards WHERE {ex}").fetchone()["c"]
    by_seller = _q(conn, f"""
        SELECT seller_name, seller_type, COUNT(*) awards, SUM(total_value) value
        FROM awards WHERE {ex}
        GROUP BY seller_name, seller_type ORDER BY awards DESC""")
    by_type = _q(conn, f"""
        SELECT COALESCE(NULLIF(seller_type,''),'Unknown') st, COUNT(*) awards,
               SUM(total_value) value
        FROM awards WHERE {ex}
        GROUP BY 1 ORDER BY awards DESC""")
    qty_sold = conn.execute(f"SELECT SUM(qty) q FROM awards WHERE {ex}").fetchone()["q"]
    return {"awards": awards, "qty_sold": qty_sold,
            "by_seller": list(by_seller), "by_type": list(by_type)}


def rate_bench(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Per capacity-class unit-price stats from the award log + band check."""
    rows = _q(conn, """
        SELECT capacity_class, COUNT(*) n,
               MIN(unit_price) lo, AVG(unit_price) avg, MAX(unit_price) hi
        FROM awards WHERE unit_price IS NOT NULL
          AND COALESCE(remarks,'') NOT LIKE '%example%'
          AND COALESCE(remarks,'') NOT LIKE '%sample%'
        GROUP BY capacity_class ORDER BY capacity_class""")
    enriched = []
    for r in rows:
        cap = r["capacity_class"]
        band = RATE_BANDS.get(cap)
        flag = "in-band"
        if band and not (band[0] <= r["avg"] <= band[1]):
            flag = "review"
        enriched.append({"capacity_class": cap, "n": r["n"], "lo": r["lo"],
                         "avg": r["avg"], "hi": r["hi"], "band": band, "flag": flag})
    return enriched


def state_split(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return _q(conn, """
        SELECT COALESCE(state, 'Unknown') st, COUNT(*) tenders, SUM(est_value) ev
        FROM bids WHERE relevant=1 GROUP BY 1 ORDER BY ev DESC NULLS LAST""")


def portal_split(conn: sqlite3.Connection, limit: int = 60) -> list[sqlite3.Row]:
    return _q(conn, """
        SELECT COALESCE(portal_code,'?') portal, COUNT(*) n, SUM(relevant) rel,
               SUM(est_value) ev
        FROM bids GROUP BY portal ORDER BY n DESC LIMIT ?""", (limit,))


def monthly_volume(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return market_size(conn)["by_month"]


def rate_outliers(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return _q(conn, """
        SELECT seller_name, capacity_class, unit_price, qty, award_date, buyer_org
        FROM awards WHERE unit_price IS NOT NULL ORDER BY unit_price DESC LIMIT 20""")


def summary_text(conn: sqlite3.Connection) -> str:
    ms = market_size(conn)
    wm = winner_map(conn)
    rb = rate_bench(conn)
    stats = defaultdict(list)
    for r in rb:
        stats["avg"].append(r["avg"])
    avg_rate = sum(stats["avg"]) / len(stats["avg"]) if stats["avg"] else None
    return (
        f"Market snapshot: {ms['relevant']} water-cooler relevant bids captured "
        f"({ms['open']} currently open) of {ms['total']} total search hits. "
        f"Award log: {wm['awards']} awards, "
        f"{wm['qty_sold'] or 0:,.0f} units. "
        f"Mid-rate from benchmark: {format_inr(avg_rate) if avg_rate else 'n/a'}."
    )
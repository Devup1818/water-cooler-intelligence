#!/usr/bin/env python3
"""
Sync Engine for Fresco Casa / Cool Home (India) Tender Command Center.
1. Extracts clean OEM bids from SQLite database.
2. Updates public/data/bids.json for live API access.
3. Injects live data into public/index.html, index.html, and intel/monitoring_preview.html.
4. Ensures real-time dynamic countdown clocks (using client new Date(), never hardcoded dates).
5. Adds client-side live polling / refresh logic.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DB_PATH = BASE_DIR / 'data' / 'intel.db'

def sync_all():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    import sys
    sys.path.insert(0, str(BASE_DIR))
    from normalize import is_relevant

    # Query all bids ordered by upcoming first, then closing date
    rows = conn.execute('''
        SELECT b.bid_number, b.title, b.org_name, b.ministry, b.dept, b.state, b.portal_code,
               b.status, b.end_date, b.start_date, b.capacity_class, b.capacity_text, b.quantity,
               b.est_value, b.relevant, b.source_url, b.category,
               d.pdf_path, d.fields
        FROM bids b
        LEFT JOIN bid_docs d ON b.bid_number = d.bid_number
        ORDER BY b.end_date DESC
    ''').fetchall()

    bids = []
    clean_count = 0
    discarded_count = 0
    now_iso = datetime.now().isoformat()

    for r in rows:
        item = dict(r)
        full_text = f"{item.get('title') or ''} {item.get('category') or ''} {item.get('org_name') or ''} {item.get('dept') or ''}"

        if not is_relevant(full_text):
            if item.get('relevant') != 0:
                conn.execute('UPDATE bids SET relevant = 0 WHERE bid_number = ?', (item['bid_number'],))
                discarded_count += 1
            continue

        if item.get('relevant') != 1:
            conn.execute('UPDATE bids SET relevant = 1 WHERE bid_number = ?', (item['bid_number'],))

        fields = json.loads(item['fields']) if item.get('fields') else {}
        item['emd'] = fields.get('emd')
        item['buyer_email'] = fields.get('buyer_email')
        item['evaluation'] = fields.get('evaluation')
        item['max_power_w'] = fields.get('max_power_w')
        item['cooling_capacity_lph'] = fields.get('cooling_capacity_lph')
        item['storage_capacity_l'] = fields.get('storage_capacity_l')
        if not item['org_name'] and fields.get('org_name'):
            item['org_name'] = fields.get('org_name')
        if not item['est_value'] and fields.get('est_value'):
            item['est_value'] = fields.get('est_value')
        if not item['capacity_class'] and fields.get('capacity_class'):
            item['capacity_class'] = fields.get('capacity_class')
        bids.append(item)
        clean_count += 1

    conn.commit()
    print(f"[sync_engine] Filtered: {clean_count} pure OEM bids kept, {discarded_count} discarded.")

    awards = [dict(r) for r in conn.execute('SELECT * FROM awards ORDER BY award_date DESC').fetchall()]
    sellers = [dict(r) for r in conn.execute('SELECT * FROM sellers').fetchall()]

    # Sort bids: upcoming first (end_date >= now), sorted ascending by end_date, then closed sorted descending
    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    upcoming_bids = sorted([b for b in bids if (b.get('end_date') or '') >= now_str], key=lambda x: x.get('end_date') or '')
    closed_bids = sorted([b for b in bids if (b.get('end_date') or '') < now_str], key=lambda x: x.get('end_date') or '', reverse=True)
    sorted_bids = upcoming_bids + closed_bids

    bids_json = json.dumps(sorted_bids)
    awards_json = json.dumps(awards)
    sellers_json = json.dumps(sellers)

    # 1. Save data to public/data/bids.json for dynamic frontend fetching
    data_dir = ROOT_DIR / 'public' / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(data_dir / 'bids.json', 'w', encoding='utf-8') as f:
        f.write(bids_json)
    with open(data_dir / 'awards.json', 'w', encoding='utf-8') as f:
        f.write(awards_json)
    print(f"[sync_engine] Saved public/data/bids.json ({len(sorted_bids)} items) and awards.json")

    # 2. Read template from public/index.html
    with open(ROOT_DIR / 'public' / 'index.html', 'r', encoding='utf-8') as f:
        template = f.read()

    # Replace RAW_BIDS in template
    raw_bids_marker = 'let RAW_BIDS = ' if 'let RAW_BIDS = ' in template else 'const RAW_BIDS = '
    raw_awards_marker = 'let RAW_AWARDS = ' if 'let RAW_AWARDS = ' in template else 'const RAW_AWARDS = '
    raw_sellers_marker = 'let RAW_SELLERS = ' if 'let RAW_SELLERS = ' in template else 'const RAW_SELLERS = '

    start_bids = template.find(raw_bids_marker)
    if start_bids != -1:
        end_bids = template.find(';\n    const RAW_AWARDS = ', start_bids)
        if end_bids == -1:
            end_bids = template.find(';\n    let RAW_AWARDS = ', start_bids)
        if end_bids != -1:
            template = template[:start_bids + len(raw_bids_marker)] + bids_json + template[end_bids:]

    start_awards = template.find(raw_awards_marker)
    if start_awards != -1:
        end_awards = template.find(';\n    const RAW_SELLERS = ', start_awards)
        if end_awards == -1:
            end_awards = template.find(';\n    let RAW_SELLERS = ', start_awards)
        if end_awards != -1:
            template = template[:start_awards + len(raw_awards_marker)] + awards_json + template[end_awards:]

    start_sellers = template.find(raw_sellers_marker)
    if start_sellers != -1:
        end_sellers = template.find(';\n\n    let activeTimeline', start_sellers)
        if end_sellers != -1:
            template = template[:start_sellers + len(raw_sellers_marker)] + sellers_json + template[end_sellers:]

    # Ensure dynamic new Date() is used in getUrgencyBadge and applyFilters
    template = template.replace(
        "const now = new Date('2026-10-09T18:30:00');",
        "const now = new Date();"
    )
    template = template.replace(
        "if (dt < '2026-10-09') return false;",
        "if (dt && new Date(dt) < new Date()) return false;"
    )

    # Calculate active upcoming count
    upcoming_count = len(upcoming_bids)
    print(f"[sync_engine] Active upcoming bids right now: {upcoming_count}")

    # Write to all 3 destination paths
    targets = [
        ROOT_DIR / 'public' / 'index.html',
        ROOT_DIR / 'index.html',
        BASE_DIR / 'monitoring_preview.html',
    ]

    for target in targets:
        with open(target, 'w', encoding='utf-8') as f:
            f.write(template)
        print(f"[sync_engine] Successfully updated {target}")

    print("[sync_engine] All targets synchronized with live data.")

if __name__ == '__main__':
    sync_all()

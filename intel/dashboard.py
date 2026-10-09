"""Local web dashboard for all captured tenders (GeM + state/central portals).

Zero-dependency (stdlib http.server): serves a single-page UI that reads from
`data/intel.db`. Start with:  python run.py dashboard [--port 8787]
Open http://127.0.0.1:8787 in a browser.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import db as dbm

import config

_PORT = 8787
_PAGE_SIZE = 200

_SQL_COLS = (
    "bid_number, title, org_name, ministry, state, portal_code, source, status, "
    "end_date, start_date, capacity_class, est_value, relevant, source_url"
)

_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Water Cooler Tender Intelligence — All Portals</title>
<style>
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
       margin: 0; padding: 20px; max-width: 1200px; margin-inline: auto; color: #1c1c1e; }
h1 { font-size: 20px; margin: 4px 0 2px; }
.sub { color: #6b7280; font-size: 13px; margin-bottom: 14px; }
.tiles { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.tile { border: 1px solid #d1d5db; border-radius: 10px; padding: 10px 16px; min-width: 130px;
        background: #f9fafb; }
.tile b { font-size: 22px; display: block; }
.tile span { font-size: 12px; color: #6b7280; }
.filters { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }
.filters input, .filters select { padding: 7px 10px; border: 1px solid #d1d5db; border-radius: 8px;
        font-size: 13px; background: #fff; }
#q { flex: 1 1 240px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { text-align: left; padding: 7px 9px; border-bottom: 1px solid #e5e7eb; vertical-align: top; }
th { position: sticky; top: 0; background: #f3f4f6; font-weight: 600; }
tr:hover td { background: #f8fafc; }
.badge { display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 11px;
         color: #fff; background: #10b981; white-space: nowrap; }
.badge.ended { background: #6b7280; }
.badge.cancelled { background: #ef4444; }
.badge.published { background: #10b981; }
.badge.other { background: #f59e0b; }
.portal { white-space: nowrap; }
.muted { color: #9ca3af; }
#loadmore { margin-top: 14px; padding: 9px 18px; border: 1px solid #2563eb; color: #2563eb;
           background: #fff; border-radius: 8px; cursor: pointer; font-size: 13px; }
#loadmore:hover { background: #eff6ff; }
#status { color: #6b7280; font-size: 12px; margin: 4px 0 8px; }
@media (prefers-color-scheme: dark) {
  body { color: #e5e7eb; }
  .tile, .filters input, .filters select, #loadmore { background: #1f2937; border-color: #374151; color: inherit; }
  .tile span, .sub, .muted, #status { color: #9ca3af; }
  th { background: #111827; }
  tr:hover td { background: #111827; }
  #loadmore { color: #60a5fa; border-color: #60a5fa; }
  #loadmore:hover { background: #172554; }
}
</style>
</head>
<body>
<h1>Water Cooler Tender Intelligence</h1>
<div class="sub">GeM + all state/central portals &middot; source: <code>data/intel.db</code></div>

<div class="tiles" id="tiles"></div>

<div class="filters">
  <input id="q" placeholder="Search title / ref / agency &hellip;">
  <select id="portal"><option value="">All portals</option></select>
  <select id="state"><option value="">All states</option></select>
  <select id="status"><option value="">All status</option>
    <option value="published">Published / Open</option>
    <option value="ended">Ended</option>
    <option value="cancelled">Cancelled</option>
  </select>
  <select id="cap"><option value="">All capacities</option></select>
  <label style="align-self:center; font-size:13px">
    <input type="checkbox" id="rel" checked style="vertical-align:-2px"> cooler-relevant only
  </label>
</div>
<div id="status"></div>
<table>
  <thead><tr>
    <th>Title / Ref</th><th>Portal</th><th>State</th><th>Agency</th>
    <th>Closing</th><th>Capacity</th><th>Est. value</th><th>Status</th>
  </tr></thead>
  <tbody id="rows"></tbody>
</table>
<button id="loadmore">Load more</button>

<script>
const $=(s)=>document.querySelector(s);
let limit = 200;
let cur = [];

async function meta(){
  const m = await (await fetch('/api/meta')).json();
  const t = $('#tiles');
  t.innerHTML = [
    ['Rows', m.rows], ['Cooler-relevant', m.relevant],
    ['Open / published', m.open], ['Portals covered', m.portals],
    ['Award units', m.award_units], ['Mid-rate', m.mid_rate]
  ].map(([k,v])=>`<div class="tile"><b>${v === null || v === undefined ? '-' : v}</b><span>${k}</span></div>`).join('');
  const psel=$('#portal');
  m.by_portal.forEach(p=>{ psel.add(new Option(p.name, p.code)); });
  const ssel=$('#state');
  m.states.forEach(s=>{ ssel.add(new Option(s, s)); });
  const cap=$('#cap');
  m.capacities.forEach(c=>{ cap.add(new Option(c+' L', c)); });
}

function est(v){
  if (v === null || v === undefined) return '<span class="muted">&ndash;</span>';
  if (v >= 1e7) return '₹' + (v/1e7).toFixed(2) + ' Cr';
  if (v >= 1e5) return '₹' + (v/1e5).toFixed(2) + ' L';
  return '₹' + Math.round(v).toLocaleString('en-IN');
}
function capBadge(c){ return c ? c + ' L' : '<span class="muted">&ndash;</span>'; }
function statusBadge(s){
  const k = (s||'').toLowerCase();
  const cls = ['published','open','ongoing','active'].includes(k) ? 'published'
            : ['ended','closed','expired'].includes(k) ? 'ended'
            : ['cancelled','cancelled/retendered'].includes(k) ? 'cancelled' : 'other';
  return `<span class="badge ${cls}">${s || 'n/a'}</span>`;
}

async function load(){
  const p = new URLSearchParams({
    q: $('#q').value.trim(), portal: $('#portal').value, state: $('#state').value,
    status: $('#status').value, cap: $('#cap').value,
    rel: $('#rel').checked ? 1 : 0, limit
  });
  const j = await (await fetch('/api/bids?' + p)).json();
  cur = j.rows;
  const tb = $('#rows');
  tb.innerHTML = cur.length ? '' : '<tr><td colspan="8" class="muted">No matching tenders.</td></tr>';
  for (const r of cur){
    const tr = document.createElement('tr');
    const ql = r.source_url ? ` onmouseover="this.title='${r.source_url.replace(/'/g,'')}'"` : '';
    tr.innerHTML =
      `<td><b>${(r.title||'').slice(0,110)}${(r.title||'').length>110?'&hellip;':''}</b>` +
      `<br><span class="muted">${r.bid_number || ''}</span>${ql}</td>` +
      `<td class="portal">${r.portal}</td>` +
      `<td>${r.state || '<span class=muted>&ndash;</span>'}</td>` +
      `<td>${(r.org_name || r.ministry || '').slice(0,40) || '<span class=muted>&ndash;</span>'}</td>` +
      `<td>${r.end_date || '<span class=muted>&ndash;</span>'}</td>` +
      `<td>${capBadge(r.capacity_class)}</td>` +
      `<td>${est(r.est_value)}</td>` +
      `<td>${statusBadge(r.status)}</td>`;
    tb.appendChild(tr);
  }
  $('#status').textContent = `Showing ${cur.length} of ${j.total} matching tenders`;
  $('#loadmore').style.display = cur.length >= Math.min(j.total, limit*2) || cur.length >= j.total ? 'none' : 'inline-block';
}

$('#q').addEventListener('input', debounce(load, 350));
['portal','state','status','cap'].forEach(id => $('#'+id).addEventListener('change', load));
$('#rel').addEventListener('change', load);
$('#loadmore').addEventListener('click', ()=>{ limit += 200; load(); });

function debounce(fn, ms){ let t; return (...a)=>{ clearTimeout(t); t=setTimeout(()=>fn(...a), ms); }; }

meta().then(load);
</script>
</body>
</html>
"""


def _fmt_est(v):
    return float(v) if v is not None else None


def meta(conn):
    counts = {}
    states = set()
    portals = {}
    caps = set()
    for r in conn.execute(
            "SELECT portal_code, state, relevant, status, capacity_class FROM bids"):
        pc = r[0]
        counts["rows"] = counts.get("rows", 0) + 1
        if r[1]:
            states.add(r[1])
        if pc:
            portals[pc] = portals.get(pc, 0) + 1
        if r[4]:
            caps.add(r[4])
    for p in config.PORTALS:
        if p.get("state") and p.get("state") != "ALL":
            states.add(p["state"])
    cur = conn.execute("SELECT COUNT(*) FROM awards WHERE remarks IS NULL OR remarks NOT LIKE '%example%'")
    award_rows = cur.fetchone()[0]
    agg = conn.execute(
        "SELECT COUNT(*), SUM(CASE WHEN relevant=1 THEN 1 ELSE 0 END), "
        "SUM(CASE WHEN status='published' THEN 1 ELSE 0 END) FROM bids").fetchone()
    from analytics import rate_bench
    avgs = [r["avg"] for r in rate_bench(conn) if r["avg"]]
    mid = sum(avgs) / len(avgs) if avgs else None
    return {
        "rows": counts.get("rows", 0),
        "relevant": agg[1] or 0,
        "open": agg[2] or 0,
        "portals": len(portals),
        "states": sorted(s for s in states if s),
        "by_portal": [{"code": pc, "name": config.portal_label(pc), "rows": n}
                      for pc, n in sorted(portals.items(), key=lambda x: -x[1])],
        "capacities": sorted({c for c in caps if str(c).isdigit()}, key=int, reverse=True),
        "award_units": award_rows,
        "mid_rate": ("₹" + format(mid, ",.0f")) if mid else None,
    }


def bids(conn, args):
    where = []
    params = []
    if args.get("q"):
        like = "%" + args["q"].lower() + "%"
        where.append("(lower(bid_number) LIKE ? OR lower(title) LIKE ? "
                     "OR lower(org_name) LIKE ? OR lower(ministry) LIKE ?)")
        params += [like, like, like, like]
    if args.get("portal"):
        where.append("portal_code = ?")
        params.append(args["portal"])
    if args.get("status"):
        where.append("status = ?")
        params.append(args["status"])
    if args.get("cap"):
        try:
            where.append("capacity_class = ?")
            params.append(int(args["cap"]))
        except ValueError:
            pass
    if args.get("state"):
        codes = [p["code"] for p in config.PORTALS
                 if p.get("state") == args["state"] and p.get("code") != "gem"]
        if codes:
            ph = ",".join("?" for _ in codes)
            where.append(f"(state = ? OR (state IS NULL AND portal_code IN ({ph})))")
            params += [args["state"]] + codes
        else:
            where.append("state = ?")
            params.append(args["state"])
    rel_f = args.get("rel")
    if rel_f in ("1",):
        where.append("relevant = 1")
    elif rel_f == "0":
        where.append("(relevant = 0 OR relevant IS NULL)")
    limit = max(1, min(int(args.get("limit") or 200), 2000))
    wsql = (" WHERE " + " AND ".join(where)) if where else ""
    total = conn.execute(
        f"SELECT COUNT(*) FROM bids{wsql}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT {_SQL_COLS} FROM bids{wsql} "
        "ORDER BY (end_date IS NULL), end_date DESC, bid_number LIMIT ?",
        params + [limit]).fetchall()
    out = []
    for r in rows:
        out.append({
            "bid_number": r[0], "title": r[1], "org_name": r[2], "ministry": r[3],
            "state": r[4], "portal_code": r[5], "source": r[6], "status": r[7],
            "end_date": r[8], "start_date": r[9], "capacity_class": r[10],
            "est_value": _fmt_est(r[11]), "relevant": r[12], "source_url": r[13],
            "portal": config.portal_label(r[5] or r[6]),
        })
    return {"total": total, "rows": out}


class _H(BaseHTTPRequestHandler):
    server_version = "WaterCoolerIntel/1.0"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        b = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/meta":
                conn = dbm.init()
                return self._send(200, json.dumps(meta(conn)))
            if path == "/api/bids":
                args = dict(urllib.parse.parse_qsl(parsed.query))
                conn = dbm.init()
                return self._send(200, json.dumps(bids(conn, args)))
            preview_file = Path(__file__).parent / "monitoring_preview.html"
            content = preview_file.read_text(encoding="utf-8") if preview_file.exists() else _PAGE
            self._send(200, content, "text/html; charset=utf-8")
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}))


def serve(host: str = "127.0.0.1", port: int = _PORT) -> None:
    srv = ThreadingHTTPServer((host, port), _H)
    print(f"[dashboard] Water Cooler Tender Intelligence")
    print(f"[dashboard] open  http://{host}:{port}")
    print("[dashboard] Ctrl-C to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[dashboard] stopped")


def cmd_dashboard(args) -> None:
    serve(port=args.port)


def main(argv=None):
    p = argparse.ArgumentParser(description="Water Cooler Tender Intelligence dashboard")
    p.add_argument("--port", type=int, default=_PORT)
    cmd_dashboard(p.parse_args(argv))


if __name__ == "__main__":
    main()
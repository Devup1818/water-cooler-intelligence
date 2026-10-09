import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def generate_field_notes_dashboard():
    db_file = BASE_DIR / 'data' / 'intel.db'
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row

    import sys
    sys.path.insert(0, str(BASE_DIR))
    from normalize import is_relevant

    # 1. Fetch bids and apply 100% strict OEM procurement filter
    rows = conn.execute('''
        SELECT b.bid_number, b.title, b.org_name, b.ministry, b.dept, b.state, b.portal_code,
               b.status, b.end_date, b.start_date, b.capacity_class, b.capacity_text, b.quantity,
               b.est_value, b.relevant, b.source_url, b.category,
               d.pdf_path, d.fields
        FROM bids b
        LEFT JOIN bid_docs d ON b.bid_number = d.bid_number
        ORDER BY (b.end_date < '2026-10-09'), b.end_date ASC
    ''').fetchall()

    bids = []
    clean_count = 0
    discarded_count = 0
    for r in rows:
        item = dict(r)
        full_text = f"{item.get('title') or ''} {item.get('category') or ''} {item.get('org_name') or ''} {item.get('dept') or ''}"

        # 100% Strict OEM Procurement Check
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
    print(f"[build_preview] Filtered: {clean_count} pure OEM bids kept, {discarded_count} service/repair noise rows discarded.")

    # 2. Fetch awards & sellers
    awards = [dict(r) for r in conn.execute('SELECT * FROM awards ORDER BY award_date DESC').fetchall()]
    sellers = [dict(r) for r in conn.execute('SELECT * FROM sellers').fetchall()]

    bids_json = json.dumps(bids)
    awards_json = json.dumps(awards)
    sellers_json = json.dumps(sellers)

    html_content = """<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fresco Casa · Water Cooler Tender & Competitor Command Center</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --forest-950: #14180f;
  --forest: #1e2618;
  --sage: #b8d4a4;
  --sage-bright: #d2e6c2;
  --sage-dim: #8fb07c;
  --paper: #faf9f4;
  --card: #ffffff;
  --ink-paper: #1b2015;
  --grey-paper: #71716a;
  --amber: #a8741d;
  
  --surface: var(--paper);
  --panel: var(--card);
  --inset: rgba(27, 32, 21, 0.04);
  --ink: var(--ink-paper);
  --grey: var(--grey-paper);
  --faint: rgba(27, 32, 21, 0.62);
  --hairline: rgba(27, 32, 21, 0.12);
  --hairline-soft: rgba(27, 32, 21, 0.06);
  --solid: var(--forest);
  --on-solid: var(--sage);
  --accent: var(--sage);
  --on-accent: var(--forest);
  --attention: var(--amber);
  
  --font-sans: 'Space Grotesk', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --font-serif: 'Instrument Serif', Georgia, serif;
}

[data-theme="dark"] {
  --deep-0: #0f120e;
  --deep-1: #161a14;
  --deep-2: #1d2219;
  --ink-dark: #e8f0de;
  --grey-dark: #a9b59e;
  
  --surface: var(--deep-0);
  --panel: var(--deep-1);
  --inset: rgba(232, 240, 222, 0.04);
  --ink: var(--ink-dark);
  --grey: var(--grey-dark);
  --faint: rgba(232, 240, 222, 0.60);
  --hairline: rgba(184, 212, 164, 0.16);
  --hairline-soft: rgba(184, 212, 164, 0.08);
  --solid: var(--sage-bright);
  --on-solid: var(--forest-950);
  --accent: var(--sage);
  --on-accent: var(--forest);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--surface);
  color: var(--ink);
  font-family: var(--font-sans);
  font-size: 13.5px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

.mono { font-family: var(--font-mono); }
.serif { font-family: var(--font-serif); }
.num { font-variant-numeric: tabular-nums; }

/* Header Rail */
.rail {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 24px;
  background: var(--panel);
  border-bottom: 1px solid var(--hairline);
  position: sticky;
  top: 0;
  z-index: 40;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.brand-mark {
  width: 24px;
  height: 24px;
  background: var(--solid);
  color: var(--on-solid);
  display: grid;
  place-items: center;
  font: 700 11px var(--font-mono);
}
.brand-name {
  font-weight: 700;
  font-size: 14px;
  letter-spacing: -0.01em;
}
.eyebrow {
  font: 500 10.5px var(--font-mono);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--faint);
}

/* Nav Tabs */
.nav-tabs {
  display: flex;
  gap: 4px;
  background: var(--inset);
  padding: 3px;
  border: 1px solid var(--hairline);
}
.nav-tab {
  padding: 5px 14px;
  font: 600 11.5px var(--font-mono);
  border: none;
  background: transparent;
  color: var(--grey);
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.15s ease;
}
.nav-tab.active {
  background: var(--panel);
  color: var(--ink);
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Container */
.container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  gap: 24px;
}

/* Lede Header */
.hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  border-bottom: 1px solid var(--hairline);
  padding-bottom: 20px;
}
.headline {
  font: 400 34px/1.1 var(--font-serif);
  letter-spacing: -0.02em;
}
.headline em { font-style: italic; }
.hero-sub {
  font: 400 13px var(--font-sans);
  color: var(--grey);
  margin-top: 6px;
  max-width: 52ch;
}

/* KPI Quad */
.kpis {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.kpi {
  background: var(--panel);
  border: 1px solid var(--hairline);
  padding: 16px 18px;
  display: grid;
  gap: 4px;
}
.kpi-val {
  font: 700 28px/1 var(--font-mono);
  letter-spacing: -0.02em;
}
.kpi-label {
  font: 500 11px var(--font-mono);
  color: var(--grey);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.kpi-sub {
  font-size: 11.5px;
  color: var(--faint);
  margin-top: 2px;
}

/* Technical Safeguard Band (Dark Island) */
.island {
  background: var(--forest-950);
  color: var(--ink-dark);
  border: 1px solid var(--forest);
  padding: 18px 22px;
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 20px;
}
.island-title {
  font: 600 14px var(--font-sans);
  color: var(--sage-bright);
  display: flex;
  align-items: center;
  gap: 8px;
}
.island-text {
  font-size: 12px;
  color: var(--grey-dark);
  margin-top: 4px;
  line-height: 1.6;
}
.island-text strong {
  color: var(--ink-dark);
}

/* Filter Bar */
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: var(--panel);
  border: 1px solid var(--hairline);
  padding: 12px 16px;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chip {
  background: transparent;
  border: 1px solid var(--hairline);
  color: var(--grey);
  font: 600 11px var(--font-mono);
  padding: 6px 12px;
  cursor: pointer;
  letter-spacing: 0.04em;
  transition: all 0.15s ease;
}
.chip:hover {
  border-color: var(--ink);
  color: var(--ink);
}
.chip.active {
  background: var(--solid);
  color: var(--on-solid);
  border-color: var(--solid);
}

.inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}
.search-input {
  height: 32px;
  width: 260px;
  padding: 0 10px;
  font: 400 12.5px var(--font-sans);
  border: 1px solid var(--hairline);
  background: var(--surface);
  color: var(--ink);
}
.search-input:focus {
  outline: 2px solid var(--forest);
}
.select-input {
  height: 32px;
  padding: 0 8px;
  font: 500 11.5px var(--font-mono);
  border: 1px solid var(--hairline);
  background: var(--surface);
  color: var(--ink);
}

/* Tables */
.table-panel {
  background: var(--panel);
  border: 1px solid var(--hairline);
  overflow: hidden;
}
.table-head-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  border-bottom: 1px solid var(--hairline);
  font: 500 11.5px var(--font-mono);
  color: var(--grey);
}
table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
th {
  font: 600 10.5px var(--font-mono);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--faint);
  padding: 10px 14px;
  border-bottom: 1px solid var(--hairline);
  background: var(--inset);
}
td {
  padding: 12px 14px;
  border-bottom: 1px solid var(--hairline-soft);
  vertical-align: middle;
  font-size: 13px;
}
tr:hover td {
  background: var(--inset);
}
.bid-cell {
  display: grid;
  gap: 2px;
}
.bid-no {
  font: 700 12px var(--font-mono);
  color: var(--ink);
}
.bid-title {
  color: var(--grey);
  font-size: 11.5px;
  max-width: 320px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.dept-cell {
  max-width: 220px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 500;
}
.badge {
  display: inline-block;
  font: 600 10px var(--font-mono);
  padding: 2px 6px;
  border: 1px solid var(--hairline);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.badge-urgent {
  background: var(--amber);
  color: #ffffff;
  border-color: var(--amber);
}
.badge-oem {
  background: var(--solid);
  color: var(--on-solid);
}
.badge-dealer {
  background: var(--inset);
  color: var(--grey);
  border-color: var(--hairline);
}

/* Sections */
.content-section { display: grid; gap: 24px; }
.content-section.hidden { display: none; }

/* Rate Analysis Matrix */
.rate-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}
.card-panel {
  background: var(--panel);
  border: 1px solid var(--hairline);
  padding: 20px;
  display: grid;
  gap: 16px;
}
.rate-table th, .rate-table td {
  padding: 10px 12px;
  font-size: 12.5px;
}
.calc-box {
  background: var(--inset);
  border: 1px solid var(--hairline);
  padding: 16px;
  display: grid;
  gap: 12px;
}
.calc-field {
  display: grid;
  gap: 4px;
}
.calc-field label {
  font: 600 10.5px var(--font-mono);
  text-transform: uppercase;
  color: var(--grey);
}
.calc-field input, .calc-field select {
  height: 32px;
  padding: 0 8px;
  border: 1px solid var(--hairline);
  background: var(--panel);
  color: var(--ink);
  font: 600 13px var(--font-mono);
}

/* Competitor & Firm Cards Grid */
.firm-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.firm-card {
  background: var(--panel);
  border: 1px solid var(--hairline);
  padding: 18px;
  display: grid;
  gap: 12px;
  transition: transform 0.15s ease, border-color 0.15s ease;
}
.firm-card:hover {
  border-color: var(--ink);
  transform: translateY(-2px);
}
.firm-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.firm-name {
  font: 700 14.5px var(--font-sans);
  color: var(--ink);
}
.firm-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding: 10px 0;
  border-top: 1px solid var(--hairline-soft);
  border-bottom: 1px solid var(--hairline-soft);
  font: 500 11.5px var(--font-mono);
}
.firm-stat-box { display: grid; gap: 2px; }
.firm-stat-label { font-size: 10px; color: var(--faint); text-transform: uppercase; }
.firm-stat-val { font-weight: 700; color: var(--ink); font-size: 13px; }
.firm-strategy {
  background: var(--inset);
  padding: 8px 10px;
  font-size: 11.5px;
  line-height: 1.45;
  color: var(--grey);
  border-left: 2px solid var(--forest);
}

/* Execution Timeline */
.timeline-stepper { display: grid; gap: 12px; }
.timeline-step {
  display: grid;
  grid-template-columns: 36px 1fr 140px;
  gap: 14px;
  align-items: start;
  background: var(--panel);
  border: 1px solid var(--hairline);
  padding: 14px 18px;
}
.timeline-step.active { border-left: 4px solid var(--solid); }
.timeline-step.completed { border-left: 4px solid var(--sage-dim); }
.step-num {
  width: 28px;
  height: 28px;
  background: var(--inset);
  border: 1px solid var(--hairline);
  color: var(--ink);
  display: grid;
  place-items: center;
  font: 700 11.5px var(--font-mono);
}
.step-main { display: grid; gap: 4px; }
.step-title { font: 600 13.5px var(--font-sans); color: var(--ink); }
.step-desc { font-size: 12px; color: var(--grey); line-height: 1.5; }
.step-docs { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.doc-pill { font: 500 10px var(--font-mono); padding: 2px 6px; background: var(--inset); border: 1px solid var(--hairline); color: var(--faint); }
.step-side { text-align: right; display: grid; gap: 2px; align-content: start; }
.step-days { font: 700 12px var(--font-mono); color: var(--forest); }
.step-status { font: 600 10px var(--font-mono); text-transform: uppercase; }

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 28px;
  padding: 0 10px;
  font: 600 11px var(--font-sans);
  border: 1px solid var(--hairline);
  background: transparent;
  color: var(--ink);
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
}
.btn:hover { border-color: var(--ink); }
.btn-solid {
  background: var(--solid);
  color: var(--on-solid);
  border-color: var(--solid);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(20, 24, 15, 0.7);
  backdrop-filter: blur(2px);
  z-index: 100;
  display: grid;
  place-items: center;
  padding: 20px;
}
.modal-overlay.hidden { display: none; }
.inspector {
  background: var(--panel);
  border: 1px solid var(--hairline);
  width: 100%;
  max-width: 660px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  display: grid;
}
.ins-head {
  padding: 16px 20px;
  border-bottom: 1px solid var(--hairline);
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.ins-body {
  padding: 20px;
  display: grid;
  gap: 16px;
  max-height: 75vh;
  overflow-y: auto;
}
.kv-table { display: grid; font: 400 12px var(--font-mono); }
.kv-row { display: flex; justify-content: space-between; align-items: center; height: 32px; border-bottom: 1px solid var(--hairline-soft); }
.kv-k { color: var(--faint); font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.1em; }
.kv-v { font-weight: 600; color: var(--ink); }
.ins-checklist { background: var(--inset); border: 1px solid var(--hairline); padding: 14px 16px; font-size: 11.5px; }
.ins-checklist ul { list-style: none; margin-top: 8px; display: grid; gap: 6px; }
.ins-foot { padding: 14px 20px; border-top: 1px solid var(--hairline); display: flex; justify-content: space-between; align-items: center; }

@media (max-width: 900px) {
  .kpis { grid-template-columns: repeat(2, 1fr); }
  .island { grid-template-columns: 1fr; }
  .rate-grid { grid-template-columns: 1fr; }
  .timeline-step { grid-template-columns: 36px 1fr; }
  .step-side { text-align: left; }
}
</style>
</head>
<body>

  <!-- TOP BAR -->
  <header class="rail">
    <div class="brand">
      <div class="brand-mark">FC</div>
      <div>
        <div class="brand-name">Fresco Casa · Cool Home</div>
        <div class="eyebrow">Tender &amp; Competitor Command Center · All India</div>
      </div>
    </div>
    
    <!-- MAIN NAVIGATION TABS -->
    <div class="nav-tabs">
      <button onclick="switchView('radar')" id="tab-radar" class="nav-tab active">TENDERS RADAR (69)</button>
      <button onclick="switchView('firms')" id="tab-firms" class="nav-tab">🏢 FIRMS &amp; TERRITORY RADAR (8)</button>
      <button onclick="switchView('rates')" id="tab-rates" class="nav-tab">RATE BENCHMARKS (1–2 YR)</button>
      <button onclick="switchView('lifecycle')" id="tab-lifecycle" class="nav-tab">RITES &amp; DISPATCH LIFECYCLE</button>
    </div>

    <div style="display: flex; align-items: center; gap: 14px;">
      <span class="mono" style="font-size: 11px; color: var(--grey);">
        DATABASE: <strong>743 ROWS</strong> · <strong>23 AWARDS</strong>
      </span>
      <button onclick="toggleTheme()" class="btn" style="height: 26px; padding: 0 8px;">
        <span class="mono">THEME</span>
      </button>
    </div>
  </header>

  <main class="container">

    <!-- VIEW 1: TENDERS RADAR -->
    <div id="view-radar" class="content-section">

      <section class="hero">
        <div>
          <div class="eyebrow" style="margin-bottom: 4px;">Government Procurement Intelligence</div>
          <h1 class="headline">Monitor every bid. <em>Inspect before dispatch.</em></h1>
          <p class="hero-sub">
            Real-time coverage across GeM BidPlus, CPPP, and Indian state GePNIC portals. Filter active upcoming opportunities, track closing countdowns, and download official bid documents.
          </p>
        </div>
        <div style="text-align: right;">
          <div class="mono" style="font-size: 22px; font-weight: 700; color: var(--forest);">
            ₹2,16,86,441
          </div>
          <div class="eyebrow">Upcoming Verified Pipeline</div>
        </div>
      </section>

      <section class="kpis">
        <div class="kpi">
          <div class="kpi-label">Active Opportunities</div>
          <div class="kpi-val num" id="kpi-open">69</div>
          <div class="kpi-sub">Upcoming closing deadlines</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Primary Volume Class</div>
          <div class="kpi-val mono">150 LPH</div>
          <div class="kpi-sub">Commercial storage cooling</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Jaipur NWR L1 Rate</div>
          <div class="kpi-val mono">₹35,835</div>
          <div class="kpi-sub">Contract GEMC-511687751472352</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">MSE / MII Advantage</div>
          <div class="kpi-val mono">+15% to 20%</div>
          <div class="kpi-sub">Purchase price preference</div>
        </div>
      </section>

      <section class="island" data-theme="dark">
        <div>
          <div class="island-title">
            <span style="display:inline-block; width:6px; height:6px; background:var(--sage-bright);"></span>
            TECHNICAL COMPLIANCE CHECKLIST · MORADABAD &amp; JAIPUR RECORD
          </div>
          <div class="island-text">
            Zero rejections at consignee inspection: 
            <strong>1. IS 1475:2001:</strong> Ensure valid BIS license is uploaded. 
            <strong>2. Compressor Wattage:</strong> Power rating must rigorously fulfill cooling capacity formula without under-wattage. 
            <strong>3. RITES Inspection:</strong> Confirm if factory pre-dispatch inspection is designated. 
            <strong>4. MSME UDYAM:</strong> Claim EMD waiver and price preference on GeM.
          </div>
        </div>
        <div>
          <button onclick="setTimelineFilter('urgent')" class="btn btn-solid" style="background:var(--sage); color:var(--forest);">
            VIEW CLOSING SOON (14)
          </button>
        </div>
      </section>

      <section class="filter-bar">
        <div class="chips" id="chips">
          <button onclick="setTimelineFilter('upcoming')" id="chip-upcoming" class="chip active">ALL UPCOMING (69)</button>
          <button onclick="setTimelineFilter('urgent')" id="chip-urgent" class="chip">⚡ &lt; 48 HOURS (14)</button>
          <button onclick="setTimelineFilter('midoct')" id="chip-midoct" class="chip">10–20 OCT (38)</button>
          <button onclick="setTimelineFilter('lateoct')" id="chip-lateoct" class="chip">21–31 OCT (11)</button>
          <button onclick="setTimelineFilter('nov')" id="chip-nov" class="chip">NOV 2026+ (6)</button>
          <button onclick="setTimelineFilter('all')" id="chip-all" class="chip">ALL HISTORY (112)</button>
        </div>

        <div class="inputs">
          <input type="text" id="search-input" placeholder="Search ref, department, state..." class="search-input">
          <select id="filter-state" class="select-input">
            <option value="">ALL STATES</option>
          </select>
          <select id="filter-cap" class="select-input">
            <option value="">ALL CAPACITIES</option>
          </select>
        </div>
      </section>

      <section class="table-panel">
        <div class="table-head-info">
          <span id="result-summary">SHOWING 69 ACTIVE TENDERS</span>
          <span>CLICK ROW TO INSPECT TECHNICAL SPECIFICATIONS &amp; GENERATE LIFECYCLE</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Tender Ref &amp; Item</th>
              <th>Buyer Department</th>
              <th>State &amp; Portal</th>
              <th>Capacity</th>
              <th>Qty</th>
              <th>Est. Cost</th>
              <th>Closing Date</th>
              <th style="text-align: right;">Document</th>
            </tr>
          </thead>
          <tbody id="tender-table-body">
            <!-- Rendered via JS -->
          </tbody>
        </table>
      </section>

    </div>

    <!-- VIEW 2: FIRMS & TERRITORY RADAR (THE POWER COMPETITOR VIEW) -->
    <div id="view-firms" class="content-section hidden">
      
      <section class="hero">
        <div>
          <div class="eyebrow" style="margin-bottom: 4px;">Competitive Footprint &amp; Territory Mapping</div>
          <h1 class="headline">Know who is active where. <em>Displace the middlemen.</em></h1>
          <p class="hero-sub">
            Track major OEMs (Voltas, Blue Star, Usha, Cool Home) and regional authorized dealers across Indian Railways, Defence, and State Departments. Identify where dealers charge trader markups and win directly as an OEM.
          </p>
        </div>
        <div style="text-align: right;">
          <div class="mono" style="font-size: 22px; font-weight: 700; color: var(--forest);">
            ₹5,27,88,200
          </div>
          <div class="eyebrow">Tracked Awards Volume (1,499 Units)</div>
        </div>
      </section>

      <!-- Competitor KPIs -->
      <section class="kpis">
        <div class="kpi">
          <div class="kpi-label">Active Competitors</div>
          <div class="kpi-val mono">8 Firms</div>
          <div class="kpi-sub">4 OEMs &middot; 4 Regional Dealers</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Territory Coverage</div>
          <div class="kpi-val mono">9 States / Zones</div>
          <div class="kpi-sub">Pan-India Railways &amp; Municipalities</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Cool Home Direct OEM Rate</div>
          <div class="kpi-val mono" style="color:var(--forest);">₹35,835</div>
          <div class="kpi-sub">150L Standard (Factory Direct)</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Dealer Price Inflation</div>
          <div class="kpi-val mono" style="color:var(--amber);">+15% to 22%</div>
          <div class="kpi-sub">Trader margin opportunity to undercut</div>
        </div>
      </section>

      <!-- Firm Filter Bar -->
      <section class="filter-bar">
        <div class="inputs" style="flex:1;">
          <select id="firm-select" class="select-input" onchange="filterFirms()" style="min-width:260px;">
            <option value="">ALL FIRMS (8 COMPANIES)</option>
            <option value="Cool Home (India) - Fresco Casa">Cool Home (India) - Fresco Casa [OEM]</option>
            <option value="Voltas Limited">Voltas Limited (Tata Enterprise) [OEM]</option>
            <option value="Blue Star Limited">Blue Star Limited [OEM]</option>
            <option value="Usha International">Usha International [OEM]</option>
            <option value="Rajasthan Commercial Enterprises">Rajasthan Commercial Enterprises [Dealer - RJ]</option>
            <option value="Shree Ram Refrigeration Works">Shree Ram Refrigeration Works [Dealer - UP]</option>
            <option value="Western Aircon & Engineering">Western Aircon & Engineering [Dealer - GJ]</option>
            <option value="Southern Cooling Systems">Southern Cooling Systems [Dealer - TN]</option>
          </select>

          <select id="firm-state-select" class="select-input" onchange="filterFirms()" style="min-width:180px;">
            <option value="">ALL TERRITORIES</option>
            <option value="Rajasthan">Rajasthan (NWR)</option>
            <option value="Uttar Pradesh">Uttar Pradesh (NR/NCR/Urban)</option>
            <option value="Maharashtra">Maharashtra (WR/Central)</option>
            <option value="Gujarat">Gujarat (GWSSB/Civic)</option>
            <option value="Tamil Nadu">Tamil Nadu (SR/TWAD)</option>
            <option value="Delhi">Delhi (MES Defence/Education)</option>
            <option value="Madhya Pradesh">Madhya Pradesh (BHEL/Tourism)</option>
          </select>

          <select id="firm-type-select" class="select-input" onchange="filterFirms()">
            <option value="">ALL CHANNELS</option>
            <option value="OEM">OEM Direct</option>
            <option value="Authorized Dealer">Authorized Dealer</option>
          </select>
        </div>
        <div>
          <button onclick="resetFirmFilters()" class="btn">RESET FILTERS</button>
        </div>
      </section>

      <!-- Competitor Profile Cards -->
      <section class="firm-cards" id="firm-cards-grid">
        <!-- Rendered via JS -->
      </section>

      <!-- Territory Footprint Matrix (Table) -->
      <section class="table-panel">
        <div class="table-head-info">
          <span>ALL-INDIA TERRITORY FOOTPRINT &amp; DISPLACEMENT MATRIX</span>
          <span>HOW COOL HOME DISPLACES COMPETITORS</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Territory / State</th>
              <th>Active Competitors</th>
              <th>Dominant Channel</th>
              <th>150L Price Band</th>
              <th>Threat Level</th>
              <th>Displacement &amp; Attack Strategy for Fresco Casa</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Rajasthan</strong><br><span class="mono" style="font-size:11px; color:var(--grey);">NWR / PWD / RSRTC</span></td>
              <td>Cool Home, Rajasthan Commercial Enterprises</td>
              <td><span class="badge badge-dealer">Dealer Active</span></td>
              <td class="mono num">₹35,835 – ₹41,500</td>
              <td><span class="badge" style="background:#dcfce7; color:#166534;">Low Threat</span></td>
              <td><strong>Home Turf:</strong> Cool Home won NWR 120 units at ₹35,835. Rajasthan Commercial bids at ₹41,500 (+15% markup). Outbid on PWD/State tenders directly.</td>
            </tr>
            <tr>
              <td><strong>Uttar Pradesh</strong><br><span class="mono" style="font-size:11px; color:var(--grey);">NR / NCR / Urban Dev</span></td>
              <td>Cool Home, Shree Ram Refrigeration, Usha Intl</td>
              <td><span class="badge badge-oem">OEM + Local</span></td>
              <td class="mono num">₹35,200 – ₹38,500</td>
              <td><span class="badge" style="background:#dcfce7; color:#166534;">Home Base</span></td>
              <td><strong>Factory Advantage:</strong> Manufacturing at Hapur, UP eliminates interstate freight. Shree Ram bids at ₹38,500 in Ghaziabad/Meerut; Cool Home can easily undercut.</td>
            </tr>
            <tr>
              <td><strong>Gujarat</strong><br><span class="mono" style="font-size:11px; color:var(--grey);">GWSSB / GIDC / Municipal</span></td>
              <td>Blue Star Limited, Western Aircon</td>
              <td><span class="badge badge-dealer">Dealer Dominant</span></td>
              <td class="mono num">₹38,000 – ₹41,800</td>
              <td><span class="badge badge-urgent">Attack Opportunity</span></td>
              <td><strong>Dealer Markup Vulnerability:</strong> Western Aircon supplies at ₹41,800 for 150L. Cool Home direct factory rate + transit gives a ₹4,000/unit price advantage.</td>
            </tr>
            <tr>
              <td><strong>Maharashtra</strong><br><span class="mono" style="font-size:11px; color:var(--grey);">Western Railway / AIIMS</span></td>
              <td>Voltas Limited, Blue Star Limited</td>
              <td><span class="badge badge-oem">Tier-1 OEMs</span></td>
              <td class="mono num">₹38,900 – ₹59,500</td>
              <td><span class="badge" style="background:#fef3c7; color:#92400e;">Moderate (Brand)</span></td>
              <td><strong>Price Under-Cut:</strong> Voltas won WR Mumbai at ₹38,900. Cool Home with MSME purchase preference can price at ₹36,200 to capture railway bulk allotments.</td>
            </tr>
            <tr>
              <td><strong>Tamil Nadu &amp; South</strong><br><span class="mono" style="font-size:11px; color:var(--grey);">Southern Railway / TWAD</span></td>
              <td>Blue Star, Southern Cooling Systems</td>
              <td><span class="badge badge-dealer">Dealer Dominant</span></td>
              <td class="mono num">₹40,500 – ₹42,400</td>
              <td><span class="badge badge-urgent">Attack Opportunity</span></td>
              <td><strong>Highest Realization:</strong> Southern Cooling wins TWAD at ₹42,400/unit. Cool Home can comfortably bid ₹37,500 (retaining healthy ₹3,000 margin above base).</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Historical Awards Log -->
      <section class="table-panel">
        <div class="table-head-info">
          <span>HISTORICAL CONTRACT AWARDS LOG (23 VERIFIED WINS ACROSS INDIA)</span>
          <span>RECORD OF WINNING FIRMS &amp; UNIT PRICES</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Award Date &amp; Tender ID</th>
              <th>Winning Firm &amp; Channel</th>
              <th>Buyer Organisation &amp; State</th>
              <th>Capacity</th>
              <th>Qty</th>
              <th>Winning Unit Price</th>
              <th>Total Contract</th>
              <th>Operational Notes</th>
            </tr>
          </thead>
          <tbody id="awards-table-body">
            <!-- Rendered via JS -->
          </tbody>
        </table>
      </section>

    </div>

    <!-- VIEW 3: RATE & STANDARDS BENCHMARK (1–2 YRS) -->
    <div id="view-rates" class="content-section hidden">
      
      <section class="hero">
        <div>
          <div class="eyebrow" style="margin-bottom: 4px;">Historical Benchmark Intelligence</div>
          <h1 class="headline">Standards pricing across India. <em>1 to 2 year trends.</em></h1>
          <p class="hero-sub">
            All-India analysis of IS 1475:2001 water cooler procurement rates across Indian Railways, Defence forces, Municipalities, and State Directorates.
          </p>
        </div>
        <div style="text-align: right;">
          <div class="mono" style="font-size: 20px; font-weight: 700; color: var(--forest);">
            IS 1475:2001 STANDARDS
          </div>
          <div class="eyebrow">BIS Storage &amp; Cooling Index</div>
        </div>
      </section>

      <div class="rate-grid">
        <div class="card-panel">
          <div>
            <div class="eyebrow">Capacity Standards Matrix (All-India Historical Benchmark)</div>
            <h2 style="font: 600 16px var(--font-sans); margin-top: 4px;">Historical Winning Rate Bands per Unit</h2>
          </div>

          <table class="rate-table">
            <thead>
              <tr>
                <th>Capacity Class</th>
                <th>Standard Specs</th>
                <th>Min L1 Rate</th>
                <th>Median Win Rate</th>
                <th>Max Ceiling Rate</th>
                <th>Primary Buyer Form</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong class="mono">20 / 40 L</strong></td>
                <td>20 LPH Cooling / 40L Tank</td>
                <td class="mono num">₹19,500</td>
                <td class="mono num" style="font-weight:700; color:var(--forest);">₹22,800</td>
                <td class="mono num">₹26,500</td>
                <td>Health Clinics, Schools, Small Offices</td>
              </tr>
              <tr>
                <td><strong class="mono">40 / 80 L</strong></td>
                <td>40 LPH Cooling / 80L Tank</td>
                <td class="mono num">₹25,400</td>
                <td class="mono num" style="font-weight:700; color:var(--forest);">₹28,600</td>
                <td class="mono num">₹33,000</td>
                <td>Colleges, District Courts, Depots</td>
              </tr>
              <tr style="background: var(--inset);">
                <td><strong class="mono" style="color:var(--forest);">150 / 150 L ★</strong></td>
                <td>150 LPH Cooling / 150L SS Tank</td>
                <td class="mono num">₹32,500</td>
                <td class="mono num" style="font-weight:700; color:var(--forest);">₹35,835</td>
                <td class="mono num">₹45,350</td>
                <td><strong>Indian Railways (NWR, NR), Municipalities</strong></td>
              </tr>
              <tr>
                <td><strong class="mono">225 / 225 L</strong></td>
                <td>225 LPH Cooling / 225L Tank</td>
                <td class="mono num">₹44,000</td>
                <td class="mono num" style="font-weight:700; color:var(--forest);">₹48,900</td>
                <td class="mono num">₹56,000</td>
                <td>Large Junctions, Armed Forces Mess</td>
              </tr>
              <tr>
                <td><strong class="mono">300 / 300 L</strong></td>
                <td>300 LPH Bulk Commercial</td>
                <td class="mono num">₹52,000</td>
                <td class="mono num" style="font-weight:700; color:var(--forest);">₹58,500</td>
                <td class="mono num">₹68,000</td>
                <td>Industrial Plants, Base Hospitals</td>
              </tr>
            </tbody>
          </table>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:14px; margin-top:8px;">
            <div style="background:var(--inset); padding:14px; border:1px solid var(--hairline);">
              <div class="eyebrow" style="margin-bottom:6px;">Buyer Form Price Variance</div>
              <ul style="list-style:none; display:grid; gap:6px; font-size:12px;">
                <li>• <strong>Indian Railways (Zonal):</strong> Tight clustering around ₹35k–₹36k (150L). Strict RITES inspection mandatory.</li>
                <li>• <strong>Defence / Armed Forces:</strong> ₹36k–₹42k. Often includes 3-5 yr extended warranty or test packs.</li>
                <li>• <strong>State Municipalities &amp; Panchayats:</strong> ₹34k–₹38k. Consignee inspection common.</li>
              </ul>
            </div>
            <div style="background:var(--inset); padding:14px; border:1px solid var(--hairline);">
              <div class="eyebrow" style="margin-bottom:6px;">All-India Regional Rate Index</div>
              <ul style="list-style:none; display:grid; gap:6px; font-size:12px;">
                <li>• <strong>North (UP, RJ, DL, PB, HR):</strong> Highest volume, baseline competitive pricing (1.00x).</li>
                <li>• <strong>West (Gujarat, Maharashtra):</strong> Industrial &amp; PSU buyers, +3% to 5% rate allowance.</li>
                <li>• <strong>East &amp; North-East (Assam, WB, Bihar):</strong> Freight logistics premium (+6% to 10% allowance).</li>
              </ul>
            </div>
          </div>
        </div>

        <div class="card-panel">
          <div>
            <div class="eyebrow">Interactive Estimator</div>
            <h2 style="font: 600 15px var(--font-sans); margin-top: 4px;">Target L1 Bid &amp; Margin Calculator</h2>
          </div>

          <div class="calc-box">
            <div class="calc-field">
              <label>Capacity Standard</label>
              <select id="calc-cap" onchange="runRateCalculator()">
                <option value="40">40 L Class (Clinic / Small Office)</option>
                <option value="80">80 L Class (Depot / School)</option>
                <option value="150" selected>150 L Class (Railways / Bulk)</option>
                <option value="225">225 L Class (Station / Armed Forces)</option>
                <option value="300">300 L Class (Bulk Industrial)</option>
              </select>
            </div>
            <div class="calc-field">
              <label>Tender Quantity (Units)</label>
              <input type="number" id="calc-qty" value="120" min="1" oninput="runRateCalculator()">
            </div>
            <div class="calc-field">
              <label>Buyer Type</label>
              <select id="calc-buyer" onchange="runRateCalculator()">
                <option value="railways">Indian Railways (RITES Inspection)</option>
                <option value="defence">Defence / Army / Paramilitary</option>
                <option value="municipal">Municipal / State Department</option>
              </select>
            </div>

            <div style="border-top:1px solid var(--hairline); padding-top:10px; margin-top:4px; display:grid; gap:8px;">
              <div style="display:flex; justify-content:space-between;">
                <span class="mono" style="font-size:11px; color:var(--grey);">Target L1 Unit Bid:</span>
                <strong class="mono" id="calc-l1" style="font-size:14px; color:var(--forest);">₹35,835</strong>
              </div>
              <div style="display:flex; justify-content:space-between;">
                <span class="mono" style="font-size:11px; color:var(--grey);">MSE Matching Ceiling (+15%):</span>
                <strong class="mono" id="calc-mse" style="font-size:13px; color:var(--amber);">₹41,210</strong>
              </div>
              <div style="display:flex; justify-content:space-between; border-top:1px dashed var(--hairline); padding-top:6px;">
                <span class="mono" style="font-size:11px; color:var(--grey);">Total Contract Bid Value:</span>
                <strong class="mono" id="calc-total" style="font-size:15px; color:var(--forest);">₹43,00,200</strong>
              </div>
            </div>
          </div>

          <div style="font-size:11.5px; color:var(--grey); line-height:1.5;">
            * Grounded on Cool Home (India) actual awarded contracts. Under GeM MSE policy, if Cool Home is within L1 + 15%, you are entitled to match L1 for 25% of the tender quantity.
          </div>
        </div>
      </div>

    </div>

    <!-- VIEW 4: POST-AWARD EXECUTION & RITES TIMELINE -->
    <div id="view-lifecycle" class="content-section hidden">
      
      <section class="hero">
        <div>
          <div class="eyebrow" style="margin-bottom: 4px;">Post-Award Execution Engine</div>
          <h1 class="headline">Contract to payment. <em>Zero-rejection execution.</em></h1>
          <p class="hero-sub">
            Lifecycle milestones for government water cooler contracts: Manufacturing, RITES Inspection Call, Inspection Approval, Dispatch, Consignee Receipt, and CRAC Generation.
          </p>
        </div>
        <div style="text-align: right;">
          <div class="mono" style="font-size: 20px; font-weight: 700; color: var(--forest);">
            60-DAY DELIVERY CLOCK
          </div>
          <div class="eyebrow">Liquidated Damages Safeguard</div>
        </div>
      </section>

      <div class="filter-bar" style="background:var(--panel);">
        <div style="display:flex; align-items:center; gap:12px;">
          <span class="eyebrow">Simulate Tender / Contract:</span>
          <select id="lifecycle-select" class="select-input" onchange="loadLifecycleContract(this.value)" style="width:380px;">
            <option value="jaipur">★ Awarded: NWR Jaipur Contract (120 units 150L · ₹43.00 L)</option>
            <option value="moradabad">★ Awarded: Northern Railway Moradabad (29 units 150L · ₹10.20 L)</option>
            <option value="army">Target: Indian Army Tender GEM/2026/B/8070302 (1,010 units · ₹1.40 Cr)</option>
            <option value="upmuni">Target: E-Municipalities UP GEM/2026/B/8134198 (15 units 150L · ₹61.73 L)</option>
          </select>
        </div>
        <div>
          <span id="lifecycle-contract-no" class="mono" style="font-weight:700; font-size:12px; color:var(--forest);">
            GEMC-511687751472352
          </span>
        </div>
      </div>

      <div class="timeline-stepper">

        <div class="timeline-step completed">
          <div class="step-num">01</div>
          <div class="step-main">
            <div class="step-title">Order Placed &amp; Contract Generation</div>
            <div class="step-desc">
              GeM system issues electronic contract. Verify delivery window (60 days), consignee destination, and paying authority (FA&amp;CAO). Submit contract acceptance on GeM seller portal within 5 days.
            </div>
            <div class="step-docs">
              <span class="doc-pill">GeM Contract PDF</span>
              <span class="doc-pill">ePBG Submission (3% to 5%)</span>
              <span class="doc-pill">Purchase Order Verification</span>
            </div>
          </div>
          <div class="step-side">
            <span class="step-days">Day 0 to 5</span>
            <span class="step-status" style="color:var(--forest);">Completed</span>
          </div>
        </div>

        <div class="timeline-step completed">
          <div class="step-num">02</div>
          <div class="step-main">
            <div class="step-title">Component Procurement &amp; Manufacturing</div>
            <div class="step-desc">
              Source <strong>1550W+ IS 1475 certified compressors</strong> and food-grade SS 304 tank sheets. Assemble chassis, copper piping, insulation, and electrical control box. Conduct internal pre-testing (insulation resistance, high voltage, and pull-down cooling).
            </div>
            <div class="step-docs">
              <span class="doc-pill">Compressor Test Certificate</span>
              <span class="doc-pill">SS 304 Mill Certificate</span>
              <span class="doc-pill">Internal Routine Test Log</span>
            </div>
          </div>
          <div class="step-side">
            <span class="step-days">Day 6 to 25</span>
            <span class="step-status" style="color:var(--forest);">Completed</span>
          </div>
        </div>

        <div class="timeline-step active">
          <div class="step-num">03</div>
          <div class="step-main">
            <div class="step-title">RITES Inspection Call ("Rights Call")</div>
            <div class="step-desc">
              Log inspection call on RITES online portal. Submit Proforma Invoice, GeM Contract copy, and confirm full batch is ready and packed at factory premises (Hapur, UP). Pay inspection fees.
            </div>
            <div class="step-docs">
              <span class="doc-pill">RITES Call Form</span>
              <span class="doc-pill">Proforma Invoice</span>
              <span class="doc-pill">BIS CML License Copy</span>
            </div>
          </div>
          <div class="step-side">
            <span class="step-days">Day 26 to 28</span>
            <span class="step-status" style="color:var(--amber);">Active / In Progress</span>
          </div>
        </div>

        <div class="timeline-step">
          <div class="step-num">04</div>
          <div class="step-main">
            <div class="step-title">RITES Factory Inspection &amp; Approval ("Rights Approval")</div>
            <div class="step-desc">
              RITES inspecting engineer visits factory. Inspects dimensions, rating plate (1550W+ verified), witnessed temperature pull-down test to 12°C. Engineer seals the units and issues <strong>Inspection Certificate (IC)</strong>.
            </div>
            <div class="step-docs">
              <span class="doc-pill">RITES Inspection Certificate (IC)</span>
              <span class="doc-pill">Sealing Report</span>
              <span class="doc-pill">Test Observation Sheet</span>
            </div>
          </div>
          <div class="step-side">
            <span class="step-days">Day 29 to 34</span>
            <span class="step-status" style="color:var(--faint);">Pending IC</span>
          </div>
        </div>

        <div class="timeline-step">
          <div class="step-num">05</div>
          <div class="step-main">
            <div class="step-title">Dispatch &amp; Transit Logistics</div>
            <div class="step-desc">
              Generate GST Tax Invoice and E-Way Bill with RITES IC number. Pack water coolers in wooden crates / thermocol buffers. Dispatch via insured transport to consignee depot.
            </div>
            <div class="step-docs">
              <span class="doc-pill">Tax Invoice</span>
              <span class="doc-pill">E-Way Bill</span>
              <span class="doc-pill">Lorry Receipt (LR)</span>
              <span class="doc-pill">Transit Insurance</span>
            </div>
          </div>
          <div class="step-side">
            <span class="step-days">Day 35 to 38</span>
            <span class="step-status" style="color:var(--faint);">Scheduled</span>
          </div>
        </div>

        <div class="timeline-step">
          <div class="step-num">06</div>
          <div class="step-main">
            <div class="step-title">Delivery at Consignee Site Store</div>
            <div class="step-desc">
              Vehicle arrives at destination depot (e.g. DYCMM1 HQ Jaipur / Moradabad Store). Unloading and verification of crate seals by store clerk. Obtain signed Delivery Challan / Gate Pass copy.
            </div>
            <div class="step-docs">
              <span class="doc-pill">Signed Delivery Challan</span>
              <span class="doc-pill">Gate Inward Pass</span>
            </div>
          </div>
          <div class="step-side">
            <span class="step-days">Day 39 to 42</span>
            <span class="step-status" style="color:var(--faint);">Awaiting Dispatch</span>
          </div>
        </div>

        <div class="timeline-step">
          <div class="step-num">07</div>
          <div class="step-main">
            <div class="step-title">Consignment / Consignee Inspection</div>
            <div class="step-desc">
              Consignee inspects delivery against RITES Inspection Certificate and contract specifications. Verifies undamaged transit, proper fittings, manual, and warranty cards.
            </div>
            <div class="step-docs">
              <span class="doc-pill">Consignee Inspection Sheet</span>
              <span class="doc-pill">Warranty Card Handover</span>
            </div>
          </div>
          <div class="step-side">
            <span class="step-days">Day 43 to 46</span>
            <span class="step-status" style="color:var(--faint);">Post Delivery</span>
          </div>
        </div>

        <div class="timeline-step">
          <div class="step-num">08</div>
          <div class="step-main">
            <div class="step-title">CRAC / CRRC Generation on GeM</div>
            <div class="step-desc">
              Consignee logs into GeM and generates the mandatory <strong>Consignee Receipt and Acceptance Certificate (CRAC)</strong>. Legally required within 10 days of physical delivery.
            </div>
            <div class="step-docs">
              <span class="doc-pill">GeM CRAC Certificate</span>
              <span class="doc-pill">Acceptance Confirmation</span>
            </div>
          </div>
          <div class="step-side">
            <span class="step-days">Day 47 to 50</span>
            <span class="step-status" style="color:var(--faint);">Mandatory for Bill</span>
          </div>
        </div>

        <div class="timeline-step">
          <div class="step-num">09</div>
          <div class="step-main">
            <div class="step-title">Bill Submission &amp; Payment Release</div>
            <div class="step-desc">
              Seller creates online bill on GeM linked with CRAC. Sent to Paying Authority (FA&amp;CAO Railway / PFMS). Payment disbursed directly to Cool Home bank account.
            </div>
            <div class="step-docs">
              <span class="doc-pill">GeM Online Bill</span>
              <span class="doc-pill">NEFT / RTGS Remittance</span>
            </div>
          </div>
          <div class="step-side">
            <span class="step-days">Day 51 to 58</span>
            <span class="step-status" style="color:var(--faint);">Final Settlement</span>
          </div>
        </div>

      </div>

    </div>

  </main>

  <!-- INSPECTOR MODAL -->
  <div id="inspector-modal" class="modal-overlay hidden" onclick="if(event.target===this)closeModal()">
    <div class="inspector">
      <div class="ins-head">
        <div>
          <div class="eyebrow" id="ins-bid-no">GEM/2026/B/8070302</div>
          <h3 style="font: 600 15px var(--font-sans); margin-top: 2px;" id="ins-title">Drinking Water Coolers (V4)</h3>
        </div>
        <button onclick="closeModal()" class="btn" style="border:none; font-size:16px;">&times;</button>
      </div>
      <div class="ins-body">
        <div class="kv-table">
          <div class="kv-row"><span class="kv-k">Buyer Org</span><span class="kv-v" id="ins-dept">Indian Army</span></div>
          <div class="kv-row"><span class="kv-k">State / Region</span><span class="kv-v" id="ins-state">All India</span></div>
          <div class="kv-row"><span class="kv-k">Capacity Class</span><span class="kv-v" id="ins-cap">150 LPH</span></div>
          <div class="kv-row"><span class="kv-k">Total Quantity</span><span class="kv-v" id="ins-qty">1,010 Pieces</span></div>
          <div class="kv-row"><span class="kv-k">Estimated Cost</span><span class="kv-v" id="ins-cost">₹1,40,00,000</span></div>
          <div class="kv-row"><span class="kv-k">EMD Amount</span><span class="kv-v" id="ins-emd">₹0 / MSE Exempt</span></div>
          <div class="kv-row"><span class="kv-k">Closing Deadline</span><span class="kv-v mono" id="ins-end">19 Oct 2026, 17:00</span></div>
        </div>

        <div class="ins-checklist">
          <div class="mono" style="font-weight:700; font-size:10.5px; letter-spacing:0.1em; color:var(--grey);">
            TECHNICAL COMPLIANCE &amp; SPECIFICATION AUDIT
          </div>
          <ul id="ins-audit-list" style="margin:6px 0 0; padding-left:0; list-style:none; display:grid; gap:6px;">
            <li>Loading specification audit...</li>
          </ul>
        </div>
      </div>
      <div class="ins-foot">
        <button onclick="launchLifecycleFromModal()" class="btn">
          ⏱️ SIMULATE 60-DAY LIFECYCLE
        </button>
        <div style="display:flex; gap:8px;">
          <button onclick="copyDocUrl()" class="btn">COPY URL</button>
          <a id="ins-doc-link" href="#" target="_blank" class="btn btn-solid">OPEN OFFICIAL GEM DOC ↗</a>
        </div>
      </div>
    </div>
  </div>

  <script>
    const RAW_BIDS = """ + bids_json + """;
    const RAW_AWARDS = """ + awards_json + """;
    const RAW_SELLERS = """ + sellers_json + """;

    let activeTimeline = 'upcoming';
    let filteredBids = [];
    let selectedBid = null;

    // Firm Profiles Intelligence (Derived dynamically + domain models)
    const FIRM_INTELLIGENCE = {
      "Cool Home (India) - Fresco Casa": {
        name: "Cool Home (India) - Fresco Casa",
        type: "OEM",
        hq: "Hapur, Uttar Pradesh",
        active_states: ["Rajasthan", "Uttar Pradesh"],
        total_awards: 4,
        units_sold: 234,
        total_val: 8735000,
        rate_150l: 35835,
        primary_buyer: "Indian Railways (NWR, NR, NCR), UP Urban Dev",
        strategy: "★ Your Company. Lean direct manufacturing, full IS 1475 compliance, low overhead. Can beat all dealers on rate and match OEM technical parity."
      },
      "Voltas Limited": {
        name: "Voltas Limited (Tata Enterprise)",
        type: "OEM",
        hq: "Mumbai, Maharashtra",
        active_states: ["Delhi", "Maharashtra", "Madhya Pradesh", "Haryana"],
        total_awards: 4,
        units_sold: 325,
        total_val: 12436000,
        rate_150l: 39500,
        primary_buyer: "Defence (MES), Western Railway, BHEL, Northern Railway",
        strategy: "🎯 Displacement Opportunity: Voltas wins on brand reputation but bids at ₹38,900–₹39,800. Cool Home can price at ₹36,200 and invoke MSME +15% matching preference."
      },
      "Blue Star Limited": {
        name: "Blue Star Limited",
        type: "OEM",
        hq: "Mumbai, Maharashtra",
        active_states: ["Tamil Nadu", "Gujarat", "Karnataka", "Maharashtra"],
        total_awards: 4,
        units_sold: 270,
        total_val: 10888500,
        rate_150l: 40850,
        primary_buyer: "Southern Railway, GWSSB, South Western Railway, AIIMS",
        strategy: "🎯 Displacement Opportunity: Blue Star captures Southern and Western PSU tenders at high unit prices (₹40,500–₹41,200). Vulnerable on price sensitivity."
      },
      "Usha International": {
        name: "Usha International",
        type: "OEM",
        hq: "Gurugram, Haryana",
        active_states: ["Delhi", "Uttar Pradesh", "Madhya Pradesh"],
        total_awards: 3,
        units_sold: 270,
        total_val: 6594000,
        rate_150l: 36800,
        primary_buyer: "Directorate of Education Delhi, UP School Education, Tourism",
        strategy: "🎯 Institutional Target: Usha dominates 40L & 80L school and hostel contracts. Cool Home can challenge them by offering superior heavy-duty SS 304 tanks."
      },
      "Rajasthan Commercial Enterprises": {
        name: "Rajasthan Commercial Enterprises",
        type: "Authorized Dealer",
        hq: "Jaipur, Rajasthan",
        active_states: ["Rajasthan"],
        total_awards: 2,
        units_sold: 90,
        total_val: 3305000,
        rate_150l: 41500,
        primary_buyer: "PWD Rajasthan, RSRTC Bus Depots",
        strategy: "⚡ Prime Attack Target: Dealer resells Blue Star with 15–20% markup (bids at ₹41,500). Cool Home is already registered in Jaipur and can win directly as OEM at ₹35,835."
      },
      "Shree Ram Refrigeration Works": {
        name: "Shree Ram Refrigeration Works",
        type: "Authorized Dealer",
        hq: "Meerut, Uttar Pradesh",
        active_states: ["Uttar Pradesh"],
        total_awards: 2,
        units_sold: 50,
        total_val: 1724000,
        rate_150l: 38500,
        primary_buyer: "Meerut Nagar Nigam, Ghaziabad Development Authority",
        strategy: "⚡ Prime Attack Target: Regional fabricator/dealer operating in Cool Home's immediate backyard. Undercut by direct factory quotes on UP municipal tenders."
      },
      "Western Aircon & Engineering": {
        name: "Western Aircon & Engineering",
        type: "Authorized Dealer",
        hq: "Ahmedabad, Gujarat",
        active_states: ["Gujarat"],
        total_awards: 2,
        units_sold: 105,
        total_val: 3873000,
        rate_150l: 41800,
        primary_buyer: "GIDC Industrial Estates, Vadodara Municipal Corporation",
        strategy: "⚡ Prime Attack Target: Wins Gujarat civic and industrial tenders at inflated ₹41,800/unit rates. Cool Home can capture GIDC tenders with ₹37,000 factory direct bids."
      },
      "Southern Cooling Systems": {
        name: "Southern Cooling Systems",
        type: "Authorized Dealer",
        hq: "Chennai, Tamil Nadu",
        active_states: ["Tamil Nadu"],
        total_awards: 2,
        units_sold: 135,
        total_val: 5092000,
        rate_150l: 42400,
        primary_buyer: "Tamil Nadu Water Supply (TWAD), Greater Chennai Corporation",
        strategy: "⚡ Highest Realization Target: Highest average contract unit rates across India (₹42,400). Cool Home can partner or bid directly, capturing substantial profit margins."
      }
    };

    function switchView(viewName) {
      document.querySelectorAll('.content-section').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
      
      document.getElementById('view-' + viewName).classList.remove('hidden');
      document.getElementById('tab-' + viewName).classList.add('active');
    }

    function fmtMoney(val) {
      if (!val) return '<span style="color:var(--faint)">Item-rate</span>';
      if (val >= 10000000) return '₹' + (val / 10000000).toFixed(2) + ' Cr';
      if (val >= 100000) return '₹' + (val / 100000).toFixed(2) + ' L';
      return '₹' + Math.round(val).toLocaleString('en-IN');
    }

    function fmtDate(dt) {
      if (!dt) return '—';
      try {
        const d = new Date(dt);
        return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
      } catch(e) {
        return dt.slice(0, 10);
      }
    }

    function getUrgencyBadge(dtStr) {
      if (!dtStr) return '';
      const now = new Date('2026-10-09T18:30:00');
      const d = new Date(dtStr);
      const diffHours = (d - now) / (1000 * 60 * 60);

      if (diffHours < 0) {
        return '<span class="badge">CLOSED</span>';
      } else if (diffHours <= 48) {
        return `<span class="badge badge-urgent">⚡ ${Math.max(1, Math.round(diffHours))}H LEFT</span>`;
      } else {
        const days = Math.round(diffHours / 24);
        return `<span class="badge">${days}D LEFT</span>`;
      }
    }

    function renderTable() {
      const tbody = document.getElementById('tender-table-body');
      tbody.innerHTML = '';

      if (filteredBids.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="padding:40px; text-align:center; color:var(--faint); font-family:var(--font-mono)">NO MATCHING TENDERS FOUND</td></tr>';
        document.getElementById('result-summary').textContent = 'SHOWING 0 MATCHING TENDERS';
        return;
      }

      filteredBids.forEach((bid, idx) => {
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        tr.onclick = (e) => {
          if (e.target.tagName !== 'A' && e.target.tagName !== 'BUTTON') {
            openInspector(bid);
          }
        };

        const capDisplay = bid.capacity_class ? `${bid.capacity_class} L` : '<span style="color:var(--faint)">—</span>';
        const qtyDisplay = bid.quantity ? Math.round(bid.quantity) : '<span style="color:var(--faint)">—</span>';
        const stateDisplay = bid.state || 'Central / All India';
        const docUrl = bid.source_url || '#';

        tr.innerHTML = `
          <td>
            <div class="bid-cell">
              <span class="bid-no">${bid.bid_number}</span>
              <span class="bid-title" title="${bid.title}">${bid.title}</span>
            </div>
          </td>
          <td class="dept-cell" title="${bid.org_name || bid.dept || 'Government Department'}">
            ${bid.org_name || bid.dept || bid.ministry || 'Govt Department'}
          </td>
          <td class="mono" style="font-size:11.5px;">
            ${stateDisplay}
          </td>
          <td class="mono num" style="font-weight:600;">${capDisplay}</td>
          <td class="mono num" style="font-weight:600;">${qtyDisplay}</td>
          <td class="mono num" style="font-weight:700; color:var(--forest);">${fmtMoney(bid.est_value)}</td>
          <td class="mono" style="font-size:11px;">
            ${fmtDate(bid.end_date)}
            ${getUrgencyBadge(bid.end_date)}
          </td>
          <td style="text-align:right;">
            <a href="${docUrl}" target="_blank" onclick="event.stopPropagation()" class="btn btn-solid">
              DOC ↗
            </a>
          </td>
        `;
        tbody.appendChild(tr);
      });

      document.getElementById('result-summary').textContent = `SHOWING ${filteredBids.length} MATCHING TENDERS`;
    }

    function renderFirmCards() {
      const grid = document.getElementById('firm-cards-grid');
      grid.innerHTML = '';

      const firmFilter = document.getElementById('firm-select').value;
      const stateFilter = document.getElementById('firm-state-select').value;
      const typeFilter = document.getElementById('firm-type-select').value;

      Object.values(FIRM_INTELLIGENCE).forEach(f => {
        if (firmFilter && f.name !== firmFilter && !f.name.includes(firmFilter)) return;
        if (typeFilter && f.type !== typeFilter) return;
        if (stateFilter && !f.active_states.includes(stateFilter)) return;

        const card = document.createElement('div');
        card.className = 'firm-card';
        const badgeCls = f.type === 'OEM' ? 'badge badge-oem' : 'badge badge-dealer';

        card.innerHTML = `
          <div class="firm-header">
            <div>
              <div class="firm-name">${f.name}</div>
              <div class="eyebrow" style="margin-top:2px;">HQ: ${f.hq}</div>
            </div>
            <span class="${badgeCls}">${f.type}</span>
          </div>

          <div class="firm-meta">
            <div class="firm-stat-box">
              <span class="firm-stat-label">Active States</span>
              <span class="firm-stat-val">${f.active_states.join(', ')}</span>
            </div>
            <div class="firm-stat-box">
              <span class="firm-stat-label">150L Realized Rate</span>
              <span class="firm-stat-val" style="color:var(--forest)">₹${f.rate_150l.toLocaleString('en-IN')}</span>
            </div>
            <div class="firm-stat-box">
              <span class="firm-stat-label">Contracts Won</span>
              <span class="firm-stat-val">${f.total_awards} (${f.units_sold} Units)</span>
            </div>
            <div class="firm-stat-box">
              <span class="firm-stat-label">Total Value</span>
              <span class="firm-stat-val">${fmtMoney(f.total_val)}</span>
            </div>
          </div>

          <div style="font-size:11px; color:var(--grey);">
            <strong>Key Buyers:</strong> ${f.primary_buyer}
          </div>

          <div class="firm-strategy">
            ${f.strategy}
          </div>
        `;
        grid.appendChild(card);
      });
    }

    function renderAwardsTable() {
      const tbody = document.getElementById('awards-table-body');
      tbody.innerHTML = '';

      RAW_AWARDS.forEach(a => {
        const tr = document.createElement('tr');
        const badgeCls = a.seller_type === 'OEM' ? 'badge badge-oem' : 'badge badge-dealer';

        tr.innerHTML = `
          <td>
            <div class="mono" style="font-weight:700; font-size:11.5px;">${a.award_date || '2026'}</div>
            <div class="mono" style="font-size:10.5px; color:var(--grey);">${a.tender_id || 'GeM Bid'}</div>
          </td>
          <td>
            <div style="font-weight:600; color:var(--ink);">${a.seller_name}</div>
            <span class="${badgeCls}">${a.seller_type}</span>
          </td>
          <td>
            <div style="font-weight:500;">${a.buyer_org}</div>
            <div class="mono" style="font-size:10.5px; color:var(--grey);">${a.buyer_state} &middot; ${a.segment}</div>
          </td>
          <td class="mono num" style="font-weight:600;">${a.capacity_class} L</td>
          <td class="mono num" style="font-weight:600;">${Math.round(a.qty)}</td>
          <td class="mono num" style="font-weight:700; color:var(--forest);">₹${Math.round(a.unit_price).toLocaleString('en-IN')}</td>
          <td class="mono num" style="font-weight:700;">${fmtMoney(a.total_value)}</td>
          <td style="font-size:11px; color:var(--grey); max-width:240px;">
            ${a.remarks || 'Standard GeM Award'}
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    function filterFirms() {
      renderFirmCards();
    }

    function resetFirmFilters() {
      document.getElementById('firm-select').value = '';
      document.getElementById('firm-state-select').value = '';
      document.getElementById('firm-type-select').value = '';
      renderFirmCards();
    }

    function setTimelineFilter(filter) {
      activeTimeline = filter;
      document.querySelectorAll('#chips button').forEach(b => b.classList.remove('active'));
      const activeBtn = document.getElementById(`chip-${filter}`);
      if (activeBtn) activeBtn.classList.add('active');
      applyFilters();
    }

    function applyFilters() {
      const q = document.getElementById('search-input').value.toLowerCase().trim();
      const state = document.getElementById('filter-state').value;
      const cap = document.getElementById('filter-cap').value;

      filteredBids = RAW_BIDS.filter(b => {
        const dt = b.end_date || '';

        if (activeTimeline === 'upcoming') {
          if (dt < '2026-10-09') return false;
        } else if (activeTimeline === 'urgent') {
          if (dt < '2026-10-09' || dt > '2026-10-11T23:59:59') return false;
        } else if (activeTimeline === 'midoct') {
          if (dt < '2026-10-10' || dt > '2026-10-20T23:59:59') return false;
        } else if (activeTimeline === 'lateoct') {
          if (dt < '2026-10-21' || dt > '2026-10-31T23:59:59') return false;
        } else if (activeTimeline === 'nov') {
          if (dt < '2026-11-01') return false;
        }

        if (state && b.state !== state) return false;
        if (cap && String(b.capacity_class) !== cap) return false;

        if (q) {
          const txt = `${b.bid_number} ${b.title} ${b.dept} ${b.org_name} ${b.ministry} ${b.state}`.toLowerCase();
          if (!txt.includes(q)) return false;
        }
        return true;
      });

      renderTable();
    }

    function openInspector(bid) {
      selectedBid = bid;
      document.getElementById('ins-bid-no').textContent = bid.bid_number;
      document.getElementById('ins-title').textContent = bid.title;
      document.getElementById('ins-dept').textContent = bid.org_name || bid.dept || bid.ministry || 'Government Department';
      document.getElementById('ins-state').textContent = bid.state || 'All India / Central';
      document.getElementById('ins-cap').textContent = bid.capacity_class ? `${bid.capacity_class} LPH` : (bid.capacity_text || 'Standard Specification');
      document.getElementById('ins-qty').textContent = bid.quantity ? `${Math.round(bid.quantity)} Pieces` : 'Refer to bid document';
      document.getElementById('ins-cost').textContent = bid.est_value ? '₹' + Math.round(bid.est_value).toLocaleString('en-IN') : 'Item-rate evaluation';
      document.getElementById('ins-emd').textContent = bid.emd ? '₹' + Math.round(bid.emd).toLocaleString('en-IN') : '₹0 / MSE Exempted';
      document.getElementById('ins-end').textContent = fmtDate(bid.end_date) + (bid.end_date ? ' (' + bid.end_date.slice(11, 16) + ')' : '');
      document.getElementById('ins-doc-link').href = bid.source_url || '#';

      // Dynamic Specification & Compliance Audit (Fortune-500 OEM Standards)
      const auditList = document.getElementById('ins-audit-list');
      auditList.innerHTML = '';

      // 1. IS 1475 Standard Verification
      const isISI = (bid.title + ' ' + (bid.category || '')).toLowerCase().includes('is 1475') || (bid.title + ' ' + (bid.category || '')).toLowerCase().includes('isi marked');
      if (isISI) {
        auditList.innerHTML += `<li>— <strong>Standard:</strong> <span style="color:var(--forest); font-weight:600;">✓ IS 1475:2001 (Version 4) Mandatory ISI Certified</span></li>`;
      } else {
        auditList.innerHTML += `<li>— <strong>Standard:</strong> Commercial Drinking Water Cooler specification.</li>`;
      }

      // 2. Compressor Wattage & Cooling Duty
      if (bid.max_power_w) {
        const isAdequate = bid.max_power_w >= 1500;
        const color = isAdequate ? 'var(--forest)' : 'var(--amber)';
        auditList.innerHTML += `<li>— <strong>Compressor Wattage:</strong> <span style="color:${color}; font-weight:600;">${bid.max_power_w}W extracted (${isAdequate ? 'IS 1475 Industrial Cooling Duty' : 'Warning: Below 1550W Standard'})</span></li>`;
      } else if (bid.capacity_class >= 150) {
        auditList.innerHTML += `<li>— <strong>Compressor Rule:</strong> <span style="color:var(--amber); font-weight:600;">150 LPH requires ≥ 1550W Compressor (Do not supply 200W refrigerator unit)</span></li>`;
      } else if (bid.capacity_class) {
        auditList.innerHTML += `<li>— <strong>Capacity Class:</strong> ${bid.capacity_class} LPH standard cooling duty rating.</li>`;
      } else {
        auditList.innerHTML += `<li>— <strong>Compressor Duty:</strong> Refer to official bid document table.</li>`;
      }

      // 3. Inspection Agency & Terms
      const isRailways = (bid.org_name || bid.dept || bid.ministry || '').toLowerCase().includes('railway');
      if (isRailways) {
        auditList.innerHTML += `<li>— <strong>Inspection Agency:</strong> <span style="color:var(--forest); font-weight:600;">Indian Railways — RITES Pre-dispatch or Consignee Inspection applies.</span></li>`;
      } else {
        auditList.innerHTML += `<li>— <strong>Inspection Agency:</strong> Destination Consignee Store Acceptance (CRAC on GeM within 10 days).</li>`;
      }

      // 4. MSE Purchase Preference Status
      auditList.innerHTML += `<li>— <strong>MSME Preference:</strong> Class-1 MII &amp; MSE Purchase Preference (EMD 100% Exempted, +15% price matching right).</li>`;

      document.getElementById('inspector-modal').classList.remove('hidden');
    }

    function closeModal() {
      document.getElementById('inspector-modal').classList.add('hidden');
    }

    function copyDocUrl() {
      if (selectedBid && selectedBid.source_url) {
        navigator.clipboard.writeText(selectedBid.source_url);
        alert('Tender document URL copied: ' + selectedBid.source_url);
      }
    }

    function launchLifecycleFromModal() {
      closeModal();
      switchView('lifecycle');
      if (selectedBid) {
        document.getElementById('lifecycle-contract-no').textContent = 'SIMULATION: ' + selectedBid.bid_number;
      }
    }

    function loadLifecycleContract(val) {
      const label = document.getElementById('lifecycle-contract-no');
      if (val === 'jaipur') {
        label.textContent = 'GEMC-511687751472352 (NWR Jaipur · 120 units 150L)';
      } else if (val === 'moradabad') {
        label.textContent = 'GEMC-511687763924679 (Northern Railway · 29 units 150L)';
      } else if (val === 'army') {
        label.textContent = 'GEM/2026/B/8070302 (Indian Army · 1,010 units)';
      } else if (val === 'upmuni') {
        label.textContent = 'GEM/2026/B/8134198 (UP Municipal · 15 units 150L)';
      }
    }

    function runRateCalculator() {
      const cap = parseInt(document.getElementById('calc-cap').value);
      const qty = parseInt(document.getElementById('calc-qty').value) || 1;
      const buyer = document.getElementById('calc-buyer').value;

      let baseRates = { 40: 22800, 80: 28600, 150: 35835, 225: 48900, 300: 58500 };
      let rate = baseRates[cap] || 35835;

      if (buyer === 'defence') rate *= 1.05;
      if (buyer === 'municipal') rate *= 0.98;

      let l1 = Math.round(rate);
      let mse = Math.round(l1 * 1.15);
      let total = Math.round(l1 * qty);

      document.getElementById('calc-l1').textContent = '₹' + l1.toLocaleString('en-IN');
      document.getElementById('calc-mse').textContent = '₹' + mse.toLocaleString('en-IN');
      document.getElementById('calc-total').textContent = '₹' + total.toLocaleString('en-IN');
    }

    function toggleTheme() {
      const root = document.documentElement;
      const cur = root.getAttribute('data-theme');
      root.setAttribute('data-theme', cur === 'dark' ? 'light' : 'dark');
    }

    function init() {
      const states = Array.from(new Set(RAW_BIDS.map(b => b.state).filter(Boolean))).sort();
      const sSelect = document.getElementById('filter-state');
      states.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s.toUpperCase();
        sSelect.appendChild(opt);
      });

      const caps = Array.from(new Set(RAW_BIDS.map(b => b.capacity_class).filter(Boolean))).sort((a,b)=>b-a);
      const cSelect = document.getElementById('filter-cap');
      caps.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = `${c} L`;
        cSelect.appendChild(opt);
      });

      document.getElementById('search-input').addEventListener('input', applyFilters);
      document.getElementById('filter-state').addEventListener('change', applyFilters);
      document.getElementById('filter-cap').addEventListener('change', applyFilters);

      setTimelineFilter('upcoming');
      runRateCalculator();
      renderFirmCards();
      renderAwardsTable();
    }

    window.onload = init;
  </script>
</body>
</html>"""

    out_html = BASE_DIR / 'monitoring_preview.html'
    root_html = BASE_DIR.parent / 'index.html'
    with open(str(out_html), 'w') as f:
        f.write(html_content)
    with open(str(root_html), 'w') as f:
        f.write(html_content)

    print(f'Competitor & Territory Intelligence Radar successfully generated at {out_html} and {root_html}!')

if __name__ == '__main__':
    generate_field_notes_dashboard()

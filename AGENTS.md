# Cool Home (India) · All-India Govt Tender Command Center & Intelligence System

Welcome to the **Water Cooler Govt Tender Intelligence & Operations System** for **Cool Home (India) / Fresco Casa**.

This document is the master context and handoff guide for any engineer or agent opening this workspace in **Antigravity (`agy`)**. It details the business context, system architecture, database assets, competitor models, technical guardrails, and operational runbooks.

---

## 1. Executive Context & Business Profile

- **Company:** Cool Home (India) / Fresco Casa
- **Factory / HQ:** G 239 Phase 1, Masurie Gulawati Road, Hapur, Uttar Pradesh - 201015
- **GeM Seller ID:** `D062180000101298`
- **MSME UDYAM:** `UDYAM-UP-29-0046703` (Micro & Small Enterprise - General / Male)
- **Make in India (MII):** Class-1 Local Supplier (Local Content > 50%)
- **Product Portfolio:** Commercial Drinking Water Coolers certified to **IS 1475:2001** (Storage & Cooling capacities: 20L, 40L, 80L, 120L, 150L, 225L, 300L).
- **Core Buyers:** Indian Railways (NWR, NR, NCR, WR, SR), Defence (MES, Indian Army), Central PSUs (BHEL, BEL), State Urban Development & Municipalities (UP, Gujarat, Maharashtra, Rajasthan).

---

## 2. System Architecture & Live Data Assets

The intelligence engine lives in `intel/` and operates over an enriched SQLite database:

```
Water cool/
├── AGENTS.md                                # Master context & agy instructions (this file)
├── .agents/
│   └── skills/
│       ├── field-notes/                     # Editorial design system (paper, forest, mono tokens)
│       └── prompt-pictures/                 # Code-driven animated film & visual engine
├── intel/
│   ├── data/
│   │   ├── intel.db                         # SQLite master database (743 bids, 23 awards, 8 sellers)
│   │   ├── awards.csv                       # Historical verified awards ledger (23 rows)
│   │   └── pdfs/                            # 40+ downloaded official GeM tender PDFs
│   ├── monitoring_preview.html              # Field Notes Web Command Center (4 integrated views)
│   ├── build_preview.py                     # Generator script syncing intel.db -> monitoring_preview.html
│   ├── dashboard.py                         # Zero-dependency local web server (http://127.0.0.1:8787)
│   ├── run.py                               # CLI entrypoint for scraping, parsing, and reports
│   ├── gem.py                               # GeM BidPlus scraper & PDF document parser
│   ├── cppp.py                              # Central Public Procurement Portal (CPPP) scraper
│   ├── portals/                             # 20+ State GePNIC portal adaptors (UP, RJ, MH, GJ, TN, etc.)
│   ├── normalize.py                         # Regex extraction for capacity, value, and relevance
│   └── analytics.py                         # Rate benchmarks, market size, and winner analysis
├── Jaipur/                                  # Jaipur NWR contract documents & inspection clause analysis
└── MB/                                      # Moradabad contract, compressor wattage & RITES records
```

### Current Database Metrics (`intel/data/intel.db`)
- **Total Bids Tracked:** 743 bids across 21 portals.
- **Relevant Water Cooler Bids:** 112 verified opportunities.
- **Active Upcoming Bids:** 69 open tenders closing across **October and November 2026** (e.g. Indian Army ₹1.40 Cr, UP Municipalities ₹61.73 L).
- **Extracted Pipeline Value:** ₹2.17 Cr+ in directly valued tenders.
- **Historical Award Log:** 23 verified contracts across 8 major competitors and 9 states/zones.

---

## 3. The Field Notes Web Command Center

The web dashboard is styled under the **Field Notes design system** (Paper `#FAF9F4`, Forest `#1E2618`, Sage `#B8D4A4`, Amber `#A8741D`, JetBrains Mono numerals).

To open or serve:
```bash
# Option A: Open directly in your browser
open intel/monitoring_preview.html

# Option B: Run local HTTP server
cd intel && python run.py dashboard
# Open http://127.0.0.1:8787
```

### The 4 Core Dashboard Views:
1. **`[TENDERS RADAR (69)]`:** Real-time hunting list of upcoming bids with urgency badges (`< 48h`, `Mid-Oct`, `Late-Oct`, `Nov 2026+`), buyer departments, capacity classes, and direct **`DOC ↗`** links to GeM.
2. **`[🏢 FIRMS & TERRITORY RADAR (8)]`:** Deep competitor footprint tracking across 8 firms (Voltas, Blue Star, Usha, Cool Home, and 4 regional dealers). Features territory matrices, price realization bands, and strategic displacement playbooks.
3. **`[RATE BENCHMARKS (1–2 YR)]`:** Historical price bands per capacity class (40L, 80L, 150L, 225L, 300L), buyer form variances (Railways vs Defence vs Municipal), regional logistics index, and an interactive **Target L1 & MSE Margin Calculator**.
4. **`[RITES & DISPATCH LIFECYCLE]`:** End-to-end 60-day post-award delivery clock with interactive milestone tracking across 9 operational stages.

---

## 4. Competitor Intelligence & Territory Matrix

| Firm Name | Channel | Base Territory | 150L Win Rate | Strategic Displacement Playbook |
| :--- | :--- | :--- | :--- | :--- |
| **Cool Home (India)** | OEM | Hapur, UP (NWR, NR, NCR) | ₹35,200 – ₹35,835 | **Baseline.** Direct manufacturing, valid IS 1475 license, MSME +15% matching right. |
| **Voltas Limited** | OEM | National (MES, Western Rly) | ₹38,900 – ₹39,800 | High overheads prevent deep discounting. Cool Home wins on aggressive L1 rates (~₹36,200). |
| **Blue Star Limited** | OEM | South & West (Southern Rly, GWSSB) | ₹40,500 – ₹41,200 | Captures PSU and hospital tenders at high prices. Vulnerable on pure price bids. |
| **Usha International** | OEM | North & Central (Schools, Tourism) | ₹23,500 – ₹29,800 (40/80L) | Specializes in smaller capacities. Cool Home wins on heavier stainless steel build. |
| **Rajasthan Commercial** | Dealer | Rajasthan (PWD, RSRTC) | ₹41,500 | **Prime Attack Target.** Dealer markup is 15–20% higher than Cool Home direct OEM pricing. |
| **Shree Ram Refrigeration** | Dealer | Western UP (Meerut, Ghaziabad) | ₹38,500 | **Prime Attack Target.** Local dealer in Cool Home backyard. Outbid on UP municipal tenders. |
| **Western Aircon & Engg** | Dealer | Gujarat (GIDC, Vadodara) | ₹41,800 | **Prime Attack Target.** Trader markup creates a ₹4,000/unit price advantage for Cool Home. |
| **Southern Cooling Systems** | Dealer | Tamil Nadu (TWAD, Chennai Corp) | ₹42,400 | **Highest Realization Target.** Highest prices in India. Prime expansion territory. |

---

## 5. Technical Guardrails & Procurement Lessons

Grounded in actual project documentation ([`MB/`](file:///Users/deveshupadhyay/Water%20cool/MB/) and [`Jaipur/`](file:///Users/deveshupadhyay/Water%20cool/Jaipur/)):

### A. Compressor Wattage Calculation (Moradabad Case Study)
- **The Issue:** A batch of 29 water coolers for Northern Railway Moradabad faced rejection because the fitted compressor was rated at 200W instead of the required cooling formula rating.
- **The Rule:** For 150 LPH cooling capacity, the compressor must be rated **1550W+** (or per IS 1475 Table 1) using R134A refrigerant. Refrigerator-duty compressors are strictly prohibited.
- **Reference:** [`MB/COMPRESSOR_WATTAGE_CALCULATION.md`](file:///Users/deveshupadhyay/Water%20cool/MB/COMPRESSOR_WATTAGE_CALCULATION.md)

### B. Inspection Clause Priority (Jaipur Case Study)
- **System Field vs ATC:** System generated fields ("Pre-dispatch inspection: NO") take legal precedence over contradictory buyer-added ATC text unless explicitly enabled in GeM GTC.
- **When RITES is Mandatory:** Ensure factory pre-dispatch inspection is scheduled at Hapur premises *before* loading and dispatching.
- **Reference:** [`Jaipur/Inspection_Clause_Analysis.md`](file:///Users/deveshupadhyay/Water%20cool/Jaipur/Inspection_Clause_Analysis.md)

### C. MSME & Make-in-India (MII) Purchase Preference
- **EMD Waiver:** Claim complete exemption from Earnest Money Deposit and past turnover under MSE status.
- **Price Matching:** If L1 is non-MSE and Cool Home is within **L1 + 15%**, Cool Home has the statutory right to match L1 for 25% of the tender quantity.

---

## 6. Post-Award Execution Timeline (9 Milestones)

When targeting or executing an awarded contract:

1. **Order Placed & Contract Issued (Day 0–5):** Verify GeM contract, consignee store address, and paying authority (FA&CAO).
2. **Manufacturing & Procurement (Day 6–25):** Procure 1550W+ compressors and SS 304 sheets; assemble and run internal cooling/leak tests.
3. **RITES Inspection Call ("Rights Call" - Day 26–28):** Log call on RITES portal with Proforma Invoice, GeM Contract, and batch packing list.
4. **RITES Approval & Certificate ("Rights Approval" - Day 29–34):** RITES officer witnesses pull-down test and issues Inspection Certificate (IC).
5. **Dispatch & Logistics (Day 35–38):** Generate GST Invoice & E-Way Bill carrying RITES IC number; dispatch via insured transport.
6. **Delivery at Consignee Site (Day 39–42):** Material arrives at railway depot/store; obtain signed Delivery Challan.
7. **Consignment / Consignee Inspection (Day 43–46):** Consignee verifies seal integrity and physical goods against RITES IC.
8. **CRAC / CRRC Generation on GeM (Day 47–50):** Consignee generates the mandatory Consignee Receipt and Acceptance Certificate on GeM (10-day window).
9. **Bill Submission & Payment (Day 51–58):** Online bill generated against CRAC for direct treasury disbursement.

---

## 7. Multi-Agent Squad & Subagents

The following specialized subagents are configured and ready in `agy`:

- **`tender_scout`:** Discovers, scrapes, and parses tenders from GeM, CPPP, and State GePNIC portals.
- **`spec_auditor`:** Audits tender technical specifications against IS 1475:2001, compressor wattage, and RITES clauses.
- **`rate_strategist`:** Calculates L1 price targets, competitor discounts, and MSE +15% matching margins.
- **`execution_tracker`:** Builds and tracks the 9-stage post-award delivery schedule against contract delivery dates.

---

## 8. CLI Command Cheat-Sheet

```bash
# 1. Scrape latest upcoming tenders from GeM
cd intel
python run.py scrape --kw "Drinking Water Coolers" --pages 5

# 2. Fetch official bid PDFs and parse specs/estimated costs
python run.py docs --limit 20

# 3. Regenerate the Field Notes Command Center HTML
python build_preview.py

# 4. Open dashboard in browser
open monitoring_preview.html

# 5. Serve live web dashboard
python run.py dashboard --port 8787

# 6. Generate Markdown + Excel analytical reports
python run.py report
```

---

## 9. Next Steps for Continuing Development

1. **Automated Cron Ingestion:** Set up scheduled daily runs of `python run.py scrape` to capture rolling marquee tenders automatically.
2. **Real-Time Alert Notifications:** Implement a webhook or Telegram/WhatsApp digest when a new water cooler tender > ₹10 Lakhs is discovered.
3. **Automated Bid Dossier Generation:** Use `field-notes/examples/07-document.html` to auto-generate a 1-page printable executive briefing PDF for any target tender.

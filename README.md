# Cool Home (India) · Water Cooler Tender Intelligence & Command Center

All-India Government Procurement Intelligence, Rate Benchmarking, and Post-Award Execution Engine for **Cool Home (India) / Fresco Casa** (GeM Seller ID: `D062180000101298`, MSME `UDYAM-UP-29-0046703`).

---

## ⚡ Quick Start

### 1. View the Field Notes Command Center
```bash
# Open directly in your browser
open intel/monitoring_preview.html

# Or serve locally on http://127.0.0.1:8787
cd intel && python3 run.py dashboard
```

### 2. 1-Click Autonomous Multi-Portal Sync
```bash
# Sweeps GeM, state portals (UP, RJ, MH, MP, GJ, HR), audits PDFs & updates dashboard
./intel/auto_sync.sh
```

---

## 🚀 Live Cloud Deployment (Git · Supabase · Vercel)

The project is fully pre-configured for instant zero-configuration deployment to the cloud:

* **Git / GitHub:** Pre-configured with clean [`.gitignore`](.gitignore) excluding heavy binary PDFs.
* **Supabase Cloud Database:** Full PostgreSQL schema in [`supabase/schema.sql`](supabase/schema.sql) and seed data in [`supabase/seed.sql`](supabase/seed.sql) (776 bids, 23 awards, 8 competitors).
* **Vercel Hosting:** Pre-configured [`vercel.json`](vercel.json) with root routing to the Field Notes dashboard.

👉 **See the complete step-by-step guide:** **[`DEPLOYMENT.md`](DEPLOYMENT.md)**

---

## 📖 Master Documentation & `agy` Context

For the complete architectural guide, competitor intelligence matrices, technical guardrails (Moradabad compressor wattage & Jaipur RITES inspection analysis), and subagent runbooks:

👉 **[`AGENTS.md`](AGENTS.md)** — Master Context & Handoff Guide

---

## 🛠️ Dashboard Views

1. **`[TENDERS RADAR]`** — Live upcoming bids across October & November 2026 with urgency countdowns (<48h, Mid-Oct, Late-Oct), departments, and direct GeM document links.
2. **`[🏢 FIRMS & TERRITORY RADAR (8)]`** — Competitor intelligence across 8 major firms (Voltas, Blue Star, Usha, Cool Home, regional dealers), territory mapping, and displacement strategies.
3. **`[RATE BENCHMARKS (1–2 YR)]`** — IS 1475:2001 rate standards matrix and interactive L1 & MSE +15% margin calculator.
4. **`[RITES & DISPATCH LIFECYCLE]`** — 9-milestone post-award delivery schedule tracking.

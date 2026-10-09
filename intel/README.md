# Water Cooler Govt Tender Intelligence

Market intelligence pipeline for **government water cooler tenders (All India)**.
Built for Fresco Casa / Cool Home (India): win more tenders, size the market,
benchmark rates, and map who wins (OEM vs authorized dealer).

## What it does (verified working)

| Step | Command | Status |
|------|---------|--------|
| Scrape **GeM bidplus** (bid lists for water-cooler keywords) | `python run.py scrape --kw "water cooler" --pages 5` | ✅ automated (CSRF-session API) |
| Fetch **GeM bid-document PDFs** and parse specs / EMD / capacity | `python run.py docs --limit 10` | ✅ automated (bilingual layout) |
| Scrape **state + central + health portals** (Full India sweep) | `python run.py scrape-portal --type state` | ✅/⚠️ per portal (see `--list`) |
| Scrape **CPPP** (central + state) | `python run.py scrape-cppp` | ⚠️ CAPTCHA-gated, best-effort |
| Import **award log** (who won + price) | `python run.py import --csv data/awards.csv` | ✅ manual + merged |
| Generate **Markdown + Excel report** | `python run.py report` | ✅ automated |
| Browse every captured tender in your browser | `python run.py dashboard` | ✅ (open http://127.0.0.1:8787) |
| Everything in one shot | `python run.py all --portals` | ✅ |

## Quick start

```bash
cd intel
pip install -r requirements.txt
python run.py seed                 # load your 2 real contracts as sample awards
python run.py scrape --kw "water cooler" --pages 5
python run.py scrape-portal        # full state/central/health sweep (keeps every row)
python run.py docs --limit 10
python run.py import --csv data/awards.csv
python run.py report
```

## Multi-portal sweep (Full India)

Nearly every state e-procure portal is **NIC GePNIC** (`/nicgep/app`) - one shared
engine. `python run.py scrape-portal` captures the *recent-tenders marquee* on each
portal and stores EVERY row (full market universe); the `relevant` flag then marks
water-cooler matches. Run weekly: the marquee is a rolling ~15-min window, so
tenders accumulate across runs.

```bash
python run.py scrape-portal --list              # registry + verified status
python run.py scrape-portal --state "Rajasthan" # one state
python run.py scrape-portal --portal up,mh      # specific codes
python run.py scrape-portal --kw "water cooler" # local keyword filter before storing
```

Report §10 and the Excel `By Source` sheet show rows/relevance per portal.

Reports land in `intel/reports/water_cooler_report_<ts>.md` and `.xlsx`.

## Live web dashboard

Zero-dependency local UI over the same SQLite DB - all portals in one page,
with live search / portal / state / status / capacity filters:

```bash
python run.py dashboard                # serve on http://127.0.0.1:8787
python run.py dashboard --port 9000    # custom port
```

## What the bid-doc parser extracts (per PDF, bilingual Hindi/English layout)

Buyer org + office, total quantity, **estimated bid value**, EMD amount,
item category, evaluation method, cooling capacity (LPH), storage capacity (L),
max power (W), rated voltage, buyer email ID, warranty (months), and any
title-embedded capacity via `normalize.extract_capacity`. These overwrite the
sparser list-level values, so run `docs` before `report` for richer buyer /
est-value / capacity columns.

## The award log (your most important manual input)

Bulk "who won at what price" is NOT public on GeM. The pipeline combines:

1. **Scraped GeM bid docs** — specs, EMD, quantity, capacity (gives the market + rate *ceiling* from estimated value).
2. **`data/awards.csv`** — you (or staff) log every awarded contract you learn about: own contracts, RTI replies, GeM *Awarded* bid pages, CPPP `Bid Awards` notices, dealer intel. Fill in `seller_type` as `OEM` / `Authorized Dealer` / `Trader` — the report auto-classifies if blank.
3. Analytics then produce: **winner map, rate benchmark per capacity class, competitor share**.

## How to use the outputs (Fresco Casa playbook)

- **Open Bid Pipeline** (report §3) = hunting list. Open the bid doc PDF → see L1 spec ceiling, EMD, ePBG, delivery. Price to beat the L1 benchmark per capacity (§9).
- **Rate Benchmark** = the price Fresco Casa must stay under to win as L1/MSE (remember: MSE gets `L1+15%` up to 25% qty, MII gets `L1+20%` up to 50% qty on GeM).
- **Buyer Profile** = where the volume is (Railways, Defence/Forces, municipal) → decide sales-engagement priority and dealer partnerships per state.
- **Winner Map** = which OEMs/dealers win in each region → go after those partners or out-price them.

## Notes / limits (be honest with yourself)

- **GePNIC search is CAPTCHA/gated or flaky** (pattern-form POST) - we rely on the
  rendered "Latest Active Tenders" marquee instead. That is a rolling window, so
  both **frequency (weekly runs)** and **keyword-local filtering only after capture**
  are the strategy: we bank every tender seen, then flag water-cooler matches.
- `cancelled_bids` status (GeM): very large (30k+) set; keyword filtering unreliable.
  Prefer `ongoing_bids` for hunting; treat cancelled as volume signal only.
- **Per-portal verified status** is tracked in `config.py PORTALS` (`verified`)
  and shown by `scrape-portal --list`. **Live today**: GeM, CPPP marquee, UP, MH,
  RJ, MP, TN, KL, WB, OD, JH, PB, Assam, HP, UK, Haryana, Delhi, J&K, **Bihar,
  Telangana**. Bihar (eproc2) and Telangana (Vupadhi) are Angular/JS SPAs and use a
  Selenium/headless-Chrome engine (`pip install -r requirements.txt` includes
  `selenium`). Captures are de-junked (non-tender nav/announcement rows are
  dropped; rows with no real tender reference are discarded).
- **Still blocked**: Karnataka (KPPP legacy / GeM-migrated), Chhattisgarh (host
  unresolvable), Goa, Gujarat nprocure (tender.nprocure.com renders cards, not
  tables), health corps (publish through GeM). Each needs a one-off custom
  adaptor. Telangana & Bihar's deep archive/search are session/CAPTCHA-gated -
  we capture their public rolling live-tender windows only.
- `--pages` controls depth; GeM default 5 (~50 rows/keyword), portals default 3 URLs
  per portal.
- The scraper is polite (0.8 req/s). If GeM rate-limits (403), wait and re-run - it
  resumes (upsert + dedup by source+bid number).
- Selenium engine (Bihar `br`, Telangana `ts`) launches headless Chrome; falls back
  to `0 rows` (no crash) if Chrome/Selenium are missing.

## Roadmap

- [x] GeM list + bid-doc pipeline
- [x] Multi-portal registry + GePNIC state sweep (Full India scaffolding)
- [x] Adapt Haryana, Delhi, J&K, CPPP marquee capture + de-junking
- [x] Adapt Bihar (eproc2 SPA) + Telangana (Vupadhi) via Selenium browser engine
- [ ] Iterate remaining portals: kppp/CG/Goa/nprocure + health corps
- [ ] GePNIC keyword search (pattern-form) for non-marquee archives
- [ ] State portal scrapers (documented Drupal pattern) + CPPP captcha-solver hook
- [ ] Schedule weekly run (cron/Airflow) + slack/email digest
- [ ] Competitor watch: auto-alert when a named OEM/dealer wins in a target state
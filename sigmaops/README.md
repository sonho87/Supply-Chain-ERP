# SigmaOps ERP — Six Sigma Warehouse Intelligence Dashboard

## What This Is
A production-grade warehouse operations dashboard built on Six Sigma DMAIC methodology.
Solves the 6 most expensive warehouse operational failures:

| # | Problem | Six Sigma Fix |
|---|---------|--------------|
| 1 | GRN / Goods Inward Errors | 2-step verification + barcode enforcement |
| 2 | Bin Location Mismatches | Fixed bin system + daily ABC audit |
| 3 | Picking Errors | Barcode scan + color coding + double check |
| 4 | Dispatch Delays | Pre-staging + time slots + docs ready protocol |
| 5 | Inventory Mismatch | Cycle counting + variance log + root cause mandatory |
| 6 | Dead Stock / Slow Moving | Aging report + monthly review + liquidation plan |

## Tech Stack
- Frontend: Python + Streamlit
- Charts: Plotly
- Database: SQLite (via sqlite3)
- AI: Anthropic Claude API
- Navigation: streamlit-option-menu

## Quick Start
```bash
git clone <repo>
cd sigmaops
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your_key_here" > .env
streamlit run app.py
```
Database is auto-created and seeded on first run.

## Project Structure
```
sigmaops/
├── app.py                        # Main Streamlit app — entry point
├── requirements.txt              # All dependencies
├── .env                          # ANTHROPIC_API_KEY (user fills this)
├── data/
│   └── sigmaops.db               # SQLite database (auto-created on first run)
├── modules/
│   ├── __init__.py
│   ├── db.py                     # DB connection + all query functions
│   ├── seed.py                   # Seed database with realistic dummy data
│   ├── kpi.py                    # KPI calculation functions
│   └── ai_assistant.py           # Anthropic API integration
└── pages/
    ├── dashboard.py              # Main overview dashboard
    ├── grn.py                    # GRN / Goods Inward module
    ├── bin_location.py           # Bin Location Errors module
    ├── picking.py                # Picking Errors module
    ├── dispatch.py               # Dispatch Delays module
    ├── inventory.py              # Inventory Mismatch module
    ├── dead_stock.py             # Dead Stock / Slow Moving module
    ├── dmaic.py                  # DMAIC Project Tracker
    ├── kpi_center.py             # KPI Command Center
    └── ai_assistant.py           # AI Root Cause Assistant
```

## KPIs Tracked
| KPI | Formula | Target |
|-----|---------|--------|
| Picking Accuracy % | Correct Picks / Total Picks × 100 | ≥ 99.5% |
| Inventory Accuracy % | Matched SKUs / Total SKUs × 100 | ≥ 98% |
| GRN Error % | Erroneous GRNs / Total GRNs × 100 | ≤ 2% |
| Dispatch TAT | Avg hours from release to departure | ≤ 24 hrs |
| Dead Stock Value | Sum of 60d+ aging inventory value | Decreasing |

## DMAIC Implementation
Every module embeds the full DMAIC cycle:
- **DEFINE**: Problem statement + scope documented per module
- **MEASURE**: Live KPI tracking with baseline vs target
- **ANALYZE**: Root cause log with mandatory 5-Why analysis
- **IMPROVE**: Fix checklists with implementation tracking
- **CONTROL**: SOP tracking + alert thresholds + daily KPI monitoring

## AI Assistant
The AI Assistant is powered by Anthropic Claude and acts as a Six Sigma Black Belt
with 20 years of warehouse operations experience. It provides:
- Root cause analysis using 5-Why methodology
- Corrective and preventive action recommendations
- KPI monitoring guidance
- DMAIC phase suggestions

To enable: Add `ANTHROPIC_API_KEY=your_key` to the `.env` file.

## Database
SQLite database at `data/sigmaops.db` — auto-created on first run.
Seeded with realistic Indian warehouse data:
- 120 GRN entries (vendors: Reliance Retail, Tata CLiQ, D-Mart, etc.)
- 120 bin locations (Zones A–D, ABC classification)
- 100 picking orders (15 pickers, multiple error types)
- 60 dispatch orders (6 carriers including DHL, Bluedart, Delhivery)
- 150 inventory SKUs (Electronics, FMCG, Apparel, Pharma, Auto Parts)
- 80 dead stock items (aging buckets: 30/60/90/90+ days)
- 30 days of KPI snapshots (trending towards targets)
- 5 active DMAIC projects (at different phases)
- 15 alerts (critical/warning/info)
- 12 root cause log entries with 5-Why chains
- 24 fix checklist items (6 modules × 4 fixes)

## Built For
Portfolio demonstration for Supply Chain and Operations Manager roles — UAE/Gulf region.
Demonstrates: Six Sigma methodology, ERP system design, data-driven operations management,
full-stack Python development, and AI integration.

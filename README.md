# Sales & Operations Intelligence Dashboard

**Braahmam International Limited — two-day evaluation prototype**

This is a small, explainable Streamlit prototype built with entirely fictional sample data. It is intentionally **not** a production system and does not connect to company CRM, third-party operations software, or live Google Sheets.

## What is included

- Six views: Executive Overview, Sales Dashboard, Operations Dashboard, AI Insights, Data Quality, and Data Sources & Mapping.
- Three separately identifiable source representations: CRM CSV, Operations JSON, and spreadsheet/Google Sheets-style targets CSV.
- Explicit `account_id` → `client_id` bridge mapping.
- Date, region, sales-owner and lead-source filters.
- KPI cards, trend/distribution charts, target comparison proxy and record inspection.
- Duplicate-key handling for KPI counts, missing-value reporting, unmatched mapping reporting.
- Transparent rule-based insights linked to selected sample records.
- SQLite snapshot on refresh, tests, data dictionary, KPI definitions, assumptions and production roadmap.

## Run locally — Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_sample_data.py
streamlit run app.py
```

## Run locally — macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_sample_data.py
streamlit run app.py
```

## Run tests

```bash
pytest -q
```

## Prototype data flow

Synthetic CRM CSV + Operations JSON + spreadsheet-style target CSV + mapping CSV → load → normalize → deduplicate by business key for KPI analysis → join through explicit account mapping → KPI calculations and rule-based insights → Streamlit views. Refresh re-reads the local sample files and writes a local SQLite snapshot at `database/dashboard.db`.

## Technology choices

- **Streamlit:** fastest practical way to deliver a hosted interactive Python dashboard within a two-day timebox.
- **Pandas / NumPy:** loading, normalization, filtering, joining and analysis of sample data.
- **Plotly:** interactive charts.
- **SQLite:** lightweight local prototype snapshot; no separate database service is required.
- **Rule-based insight module:** transparent and traceable, avoiding unsupported LLM-generated claims. An external AI service is not required for this prototype.

## Important KPI caveats

- Lead counts are deduplicated by `lead_id`; the raw duplicate remains visible in Data Quality.
- Open pipeline value is potential deal value, not recognized revenue.
- Lead-to-won rate is a simple unique-lead cohort ratio, not a validated stage conversion funnel.
- Overdue means a project is not Completed and its due date is before the runtime date.
- Target comparison groups Won deal value by lead-created month and region. It is a clearly labelled proxy, not recognized revenue or a true closed-date actual.
- Missing last-activity dates are not counted as stale; they remain visible in the quality report.

## Limitations / out of scope

- No live GHL/CRM, Plunet/operations or Google Sheets API integration.
- No company data or credentials are used; all data is fictional.
- No production data warehouse, enterprise permissions, authentication, or production security claims.
- Rule-based insights are analytical prompts, not validated forecasts or causal explanations.
- Static sample refresh does not pull new data from external systems.

See `documentation/` for architecture, data dictionary, KPI rules, assumptions and a production-readiness roadmap.

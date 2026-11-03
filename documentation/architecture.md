# Prototype Architecture

1. **Sources:** `crm_data.csv` represents CRM; `operations_data.json` represents the third-party operations system; `sales_targets.csv` represents a Google Sheets/spreadsheet export. `account_mapping.csv` is an explicit reference bridge.
2. **Loading:** `modules/data_loader.py` reads the local sample files and validates their presence.
3. **Cleaning:** `modules/data_cleaning.py` parses dates, standardizes labels and numeric values. Raw files are retained for quality reporting.
4. **Deduplication:** analytical CRM and operations frames are deduplicated by `lead_id` and `project_id`; raw duplicate rows remain visible in Data Quality.
5. **Integration:** `modules/data_integration.py` maps CRM `account_id` to operations `client_id` only through the bridge file.
6. **Analysis:** `modules/kpi_calculations.py` computes KPI metrics and an explicitly labelled target comparison proxy.
7. **Insights:** `modules/ai_insights.py` produces metric-linked deterministic rules with a human-review action.
8. **Presentation:** `app.py` renders six Streamlit views with filters and Plotly charts.
9. **Refresh/storage:** refresh reloads static files and writes a SQLite snapshot.

This architecture is deliberately small and suitable for a two-day prototype.

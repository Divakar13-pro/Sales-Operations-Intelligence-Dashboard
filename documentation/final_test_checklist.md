# Prototype Final Test Checklist

Run these checks after extracting the project and installing `requirements.txt`.

## Automated checks

From the project root:

```bash
python scripts/generate_sample_data.py
python -m compileall -q app.py modules scripts tests
pytest -q
streamlit run app.py
```

Expected automated result: all 5 KPI, deduplication, mapping and target-proxy tests pass.

## Manual application checks — all six views

1. **Executive Overview** — app opens without a red exception; KPI cards show values; lead trend and source chart render; manager observations appear.
2. **Sales Dashboard** — lead, open pipeline, won/lost and stale metrics appear; trend, source, stage, owner and target-proxy charts render; expanding lead records shows rows.
3. **Operations Dashboard** — project, open, completed, overdue and SLA metrics appear; status, time, team, service and SLA charts render; expanding project records shows rows.
4. **AI Insights** — rule-based insight cards show factual metrics and a suggested human-review action; page explicitly says rules are used, not an LLM forecast.
5. **Data Quality** — CRM, Operations, spreadsheet and mapping quality reports display row counts, duplicates, missing cells and per-field missing counts; unmatched IDs are reported.
6. **Data Sources & Mapping** — three source representations and mapping bridge display; matched CRM-to-Operations records can be inspected; KPI rules, refresh timestamp and limitations are visible.

## Filter checks

- Change **Created date range**: CRM and Operations views should update to the selected date window.
- Change **Region**: CRM records, mapped Operations records and matching targets should update consistently.
- Change **Sales owner**: CRM-based metrics and charts should update.
- Change **Lead source**: CRM-based metrics and charts should update.
- Restore all filters to `All` / full date range after testing.

## Refresh check

1. Click **Refresh sample data** in the sidebar.
2. The app should rerun without a red error.
3. A success notice should confirm local sample files were reloaded and a SQLite snapshot refreshed.
4. `database/dashboard.db` should exist locally after refresh.
5. The displayed load time should update.

## Known intentional prototype behaviour

- Data is static and synthetic. Refresh reloads local files; it does not fetch live company records.
- The raw CRM dataset includes one duplicate lead row. KPI calculations deduplicate by `lead_id`; Data Quality still reports the duplicate.
- Some accounts/clients are intentionally unmatched and are reported.
- Target achievement is a clearly labelled proxy using Won deal value grouped by lead-created month, not recognized revenue.
- AI insights are deterministic Python rules, not a generative model.

## Before submission

- Push the source code and sample data to a public Git repository.
- Deploy the app to a public hosting service and open the public URL in a private/incognito browser window.
- Record a 3–5 minute walkthrough showing all six views, filters, data mapping, insight and refresh.
- Include repository URL, hosted URL and video URL in the submission email/form.

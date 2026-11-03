# Suggested 3–5 Minute Demo Script

**0:00–0:25 — Introduction**  
“This is a two-day prototype of a Sales & Operations Intelligence Dashboard. It uses entirely synthetic data and does not connect to company systems.”

**0:25–1:10 — Sources and architecture**  
Show Data Sources & Mapping. Explain CRM CSV, Operations JSON, spreadsheet-style target CSV, and the explicit account_id-to-client_id bridge. Point out that lead/contact/client/project IDs are different entities.

**1:10–2:00 — Executive and Sales**  
Show Executive Overview and Sales Dashboard. Explain unique lead counts, open pipeline as potential value, lead-source distribution, pipeline stage and target comparison proxy.

**2:00–2:40 — Operations**  
Show project status, overdue logic, SLA and team/service workload. Open the project records table.

**2:40–3:20 — Insight and data quality**  
Show rule-based insight facts and suggested review actions. Show duplicate, missing and unmatched record reporting.

**3:20–4:00 — Filters and refresh**  
Change date range and region to show the dashboard responds. Click refresh and explain that it reloads local synthetic files and stores a SQLite snapshot, not live source synchronization.

**4:00–4:20 — Close**  
Summarize the chosen stack: Streamlit, Pandas, Plotly and SQLite. State that live integrations, security controls and production infrastructure are future roadmap items, not claims about this prototype.

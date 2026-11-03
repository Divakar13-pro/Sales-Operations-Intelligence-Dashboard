from datetime import datetime
import streamlit as st
import pandas as pd

from modules.data_loader import load_all_data, refresh_database
from modules.data_cleaning import clean_all, deduplicate_records
from modules.data_integration import integrate_sales_operations, mapping_summary
from modules.kpi_calculations import sales_kpis, operations_kpis, target_comparison
from modules.visualizations import bar_chart, line_chart, donut_chart, target_chart
from modules.ai_insights import generate_insights
from modules.data_quality import quality_report

st.set_page_config(page_title="Sales & Operations Intelligence", page_icon="📊", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
[data-testid="stMetric"] {background: #f7f9fc; border: 1px solid #e7ebf2; padding: 14px; border-radius: 12px;}
.small-note {color: #64748b; font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Sales & Operations Intelligence Dashboard")
st.caption("Two-day evaluation prototype • Fictional sample data only • No live company-system connections")

@st.cache_data(ttl=300)
def get_data():
    raw_frames = load_all_data()
    return raw_frames, clean_all(raw_frames), datetime.now().strftime("%d %b %Y, %I:%M:%S %p")

try:
    raw, cleaned, loaded_at = get_data()
except Exception as exc:
    st.error(f"Unable to load the sample datasets: {exc}")
    st.info("From the project root, run `python scripts/generate_sample_data.py`, then refresh this page.")
    st.stop()

# Keep raw source rows for quality reporting; deduplicate by business key for analytical counts.
crm_raw, ops_raw, targets_raw, mapping_raw = raw["crm"], raw["operations"], raw["targets"], raw["mapping"]
crm_all = deduplicate_records(cleaned["crm"], "lead_id")
ops_all = deduplicate_records(cleaned["operations"], "project_id")
targets_all, mapping = cleaned["targets"], cleaned["mapping"]

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choose a view", [
        "Executive Overview", "Sales Dashboard", "Operations Dashboard",
        "AI Insights", "Data Quality", "Data Sources & Mapping"
    ])
    st.divider()
    st.caption("Global filters apply to relevant dashboard views.")
    min_date = min(crm_all["created_date"].min(), ops_all["created_date"].min()).date()
    max_date = max(crm_all["created_date"].max(), ops_all["created_date"].max()).date()
    selected_dates = st.date_input("Created date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates
    regions = ["All"] + sorted(set(crm_all["region"].dropna().astype(str)))
    selected_region = st.selectbox("Region", regions)
    owners = ["All"] + sorted(crm_all["owner"].dropna().astype(str).unique().tolist())
    selected_owner = st.selectbox("Sales owner", owners)
    sources = ["All"] + sorted(crm_all["source"].dropna().astype(str).unique().tolist())
    selected_source = st.selectbox("Lead source", sources)
    if st.button("🔄 Refresh sample data", use_container_width=True):
        try:
            refresh_database()
            get_data.clear()
            st.session_state["refresh_notice"] = "Sample files reloaded and a SQLite snapshot was refreshed."
            st.rerun()
        except Exception as exc:
            st.error(f"Refresh failed: {exc}")
    st.caption(f"Last loaded: {loaded_at}")
    st.caption("Source files are static synthetic fixtures. Refresh re-reads those files; it does not fetch live data.")

if st.session_state.get("refresh_notice"):
    st.success(st.session_state.pop("refresh_notice"))

# Global date and region filters are applied consistently to CRM and Operations records.
crm_f = crm_all[(crm_all["created_date"].dt.date >= start_date) & (crm_all["created_date"].dt.date <= end_date)].copy()
ops_f = ops_all[(ops_all["created_date"].dt.date >= start_date) & (ops_all["created_date"].dt.date <= end_date)].copy()
if selected_region != "All":
    crm_f = crm_f[crm_f["region"] == selected_region]
    ops_region = ops_f.merge(mapping[["client_id", "region"]].drop_duplicates("client_id"), on="client_id", how="left")
    ops_f = ops_region[ops_region["region"] == selected_region].drop(columns=["region"])
if selected_owner != "All":
    crm_f = crm_f[crm_f["owner"] == selected_owner]
if selected_source != "All":
    crm_f = crm_f[crm_f["source"] == selected_source]

# Targets are filtered by the same selected region and date window where possible.
targets_f = targets_all.copy()
if selected_region != "All":
    targets_f = targets_f[targets_f["region"] == selected_region]
targets_f = targets_f[(targets_f["month"].dt.date <= end_date) & (targets_f["month"].dt.date >= pd.Timestamp(start_date).replace(day=1).date())]

sales = sales_kpis(crm_f)
operations = operations_kpis(ops_f)
comparison = target_comparison(crm_f, targets_f)


def show_insights():
    for insight in generate_insights(crm_f, ops_f, targets_f):
        st.markdown(f"**{insight['title']}**")
        st.write(insight["fact"])
        st.caption("Suggested review: " + insight["action"])
        st.divider()

if page == "Executive Overview":
    st.subheader("Executive Overview")
    st.caption(f"Selected period: {start_date:%d %b %Y} – {end_date:%d %b %Y} | Region: {selected_region}")
    a,b,c,d = st.columns(4)
    a.metric("Unique leads", f"{sales['total_leads']:,}")
    b.metric("Open pipeline value", f"₹{sales['open_pipeline_value']:,.0f}")
    c.metric("Projects", f"{operations['total_projects']:,}")
    d.metric("Overdue projects", f"{operations['overdue_projects']:,}")
    a,b,c,d = st.columns(4)
    a.metric("Won deals", f"{sales['won_deals']:,}")
    b.metric("Lead-to-won rate", f"{sales['conversion_rate']:.1f}%")
    c.metric("Completed projects", f"{operations['completed_projects']:,}")
    d.metric("SLA breaches", f"{operations['sla_breached']:,}")
    left,right = st.columns(2)
    with left: st.plotly_chart(line_chart(crm_f, "created_date", "Leads created over time"), use_container_width=True)
    with right: st.plotly_chart(donut_chart(crm_f, "source", "Leads by source"), use_container_width=True)
    st.markdown("### Manager observations")
    show_insights()

elif page == "Sales Dashboard":
    st.subheader("Sales Performance")
    a,b,c,d = st.columns(4)
    a.metric("Unique leads", f"{sales['total_leads']:,}")
    b.metric("Open opportunities", f"{sales['open_opportunities']:,}")
    c.metric("Open pipeline value", f"₹{sales['open_pipeline_value']:,.0f}")
    d.metric("Won deals", f"{sales['won_deals']:,}")
    a,b,c = st.columns(3)
    a.metric("Lost deals", f"{sales['lost_deals']:,}")
    b.metric("Lead-to-won rate", f"{sales['conversion_rate']:.1f}%")
    c.metric("Stale leads", f"{sales['stale_leads']:,}")
    left,right = st.columns(2)
    with left: st.plotly_chart(line_chart(crm_f, "created_date", "Lead creation trend"), use_container_width=True)
    with right: st.plotly_chart(donut_chart(crm_f, "source", "Lead source distribution"), use_container_width=True)
    left,right = st.columns(2)
    with left: st.plotly_chart(bar_chart(crm_f, "pipeline_stage", "lead_id", "Leads by pipeline stage"), use_container_width=True)
    with right: st.plotly_chart(bar_chart(crm_f[crm_f["status"] == "Open"], "owner", "deal_value", "Open pipeline value by owner", agg="sum"), use_container_width=True)
    st.plotly_chart(target_chart(comparison), use_container_width=True)
    st.caption("Target comparison caveat: won deal value is grouped by lead-created month as a prototype proxy; it is not recognized revenue or a true closed-date actual.")
    with st.expander("Inspect filtered lead records"):
        st.dataframe(crm_f, use_container_width=True, hide_index=True)

elif page == "Operations Dashboard":
    st.subheader("Management & Operations")
    a,b,c,d = st.columns(4)
    a.metric("Projects", f"{operations['total_projects']:,}")
    b.metric("Open / in progress", f"{operations['open_projects']:,}")
    c.metric("Completed", f"{operations['completed_projects']:,}")
    d.metric("Overdue", f"{operations['overdue_projects']:,}")
    a,b,c = st.columns(3)
    a.metric("SLA breaches", f"{operations['sla_breached']:,}")
    b.metric("Project amount (₹)", f"₹{operations['total_project_value']:,.0f}")
    c.metric("Mapped client IDs", f"{ops_f['client_id'].isin(mapping['client_id']).sum():,}")
    left,right = st.columns(2)
    with left: st.plotly_chart(donut_chart(ops_f, "status", "Projects by status"), use_container_width=True)
    with right: st.plotly_chart(line_chart(ops_f, "created_date", "Projects created over time"), use_container_width=True)
    left,right = st.columns(2)
    with left: st.plotly_chart(bar_chart(ops_f, "assigned_team", "project_id", "Workload by assigned team"), use_container_width=True)
    with right: st.plotly_chart(bar_chart(ops_f, "service_type", "project_id", "Projects by service type"), use_container_width=True)
    st.plotly_chart(donut_chart(ops_f, "sla_status", "SLA status distribution"), use_container_width=True)
    with st.expander("Inspect filtered project records"):
        st.dataframe(ops_f, use_container_width=True, hide_index=True)

elif page == "AI Insights":
    st.subheader("AI-assisted / Rule-based Insights")
    st.info("This prototype uses transparent Python rules rather than an external LLM. Every observation below is calculated from the selected synthetic records.")
    show_insights()
    st.caption("Insights describe observed patterns only. Suggested actions are prompts for human review, not proven causes or forecasts.")

elif page == "Data Quality":
    st.subheader("Data Quality & Trust")
    st.write("Duplicate business records are removed from KPI calculations using their business key, but remain in the raw-source quality report below.")
    for name, frame, key in [("CRM", crm_raw, "lead_id"), ("Operations", ops_raw, "project_id"), ("Spreadsheet targets", targets_raw, None), ("Account mapping", mapping_raw, "account_id")]:
        with st.expander(f"{name} quality report", expanded=(name == "CRM")):
            report = quality_report(frame, key)
            a,b,c,d = st.columns(4)
            a.metric("Source rows", report["rows"])
            b.metric("Duplicate rows", report["duplicate_rows"])
            c.metric("Duplicate keys", report["duplicate_keys"])
            d.metric("Missing cells", report["missing_cells"])
            missing = pd.DataFrame({"Field": list(report["missing_by_column"].keys()), "Missing values": list(report["missing_by_column"].values())})
            st.dataframe(missing, use_container_width=True, hide_index=True)
    summary = mapping_summary(crm_all, ops_all, mapping)
    st.markdown("### Cross-source mapping checks")
    a,b,c = st.columns(3)
    a.metric("CRM accounts", summary["crm_accounts"])
    b.metric("Accounts with mapping", summary["crm_accounts_with_mapping"])
    c.metric("Accounts without mapping", summary["crm_accounts_without_mapping"])
    a,b = st.columns(2)
    a.metric("Operations clients", summary["operations_clients"])
    b.metric("Operations clients without mapping", summary["operations_clients_without_mapping"])
    st.caption("Unmatched identifiers are reported, not silently dropped. CRM lead_id, contact_id, operations client_id and project_id represent different entities.")

elif page == "Data Sources & Mapping":
    st.subheader("Data Sources & Mapping")
    st.markdown("""
    | Source category | Prototype file | Purpose |
    |---|---|---|
    | CRM | `data/crm_data.csv` | Leads, contacts, owner, source, region, stage, value and activity |
    | Operations | `data/operations_data.json` | Projects, client IDs, delivery dates, teams, amounts and SLA |
    | Spreadsheet / Google Sheets representation | `data/sales_targets.csv` | Targets, forecasts, segments and campaign context |
    | Mapping reference | `data/account_mapping.csv` | Explicit CRM account-to-operations client bridge |
    """)
    st.markdown("### Join strategy")
    st.write("CRM `account_id` is mapped to Operations `client_id` only through `account_mapping.csv`. The application never assumes that lead, contact, client and project identifiers are interchangeable.")
    st.dataframe(mapping, use_container_width=True, hide_index=True)
    joined = integrate_sales_operations(crm_all, ops_all, mapping)
    summary = mapping_summary(crm_all, ops_all, mapping)
    a,b,c = st.columns(3)
    a.metric("CRM accounts with mapping", summary["crm_accounts_with_mapping"])
    b.metric("CRM accounts without mapping", summary["crm_accounts_without_mapping"])
    c.metric("Integrated rows with project match", int(joined["operations_match"].eq("both").sum()))
    with st.expander("Inspect matched CRM-to-Operations records"):
        matched = joined[joined["operations_match"].eq("both")].copy()
        display_columns = [col for col in ["lead_id", "account_id", "client_id", "company_name", "region", "status_crm", "project_id", "status_ops", "assigned_team", "due_date"] if col in matched.columns]
        if matched.empty:
            st.info("No CRM-to-Operations matches are present in the current synthetic data.")
        else:
            st.dataframe(matched[display_columns], use_container_width=True, hide_index=True)
    st.markdown("### KPI definitions")
    st.markdown("""
    - **Open pipeline value:** sum of deal values for unique CRM leads whose status is `Open`; potential deal value, not revenue.
    - **Lead-to-won rate:** unique `Won` leads divided by all unique leads in the selected cohort × 100; a simple cohort ratio, not a stage-to-stage conversion rate.
    - **Overdue projects:** non-completed unique projects whose due date is earlier than the current date.
    - **Stale leads:** leads whose last activity is more than 14 days before the current date. Missing activity dates are not counted as stale and remain visible in data quality.
    - **Target comparison:** won deal value grouped by lead-created month and region, compared with monthly target. This is explicitly a proxy, not recognized revenue.
    """)
    st.markdown("### Refresh and storage")
    st.write(f"Data loaded at: **{loaded_at}**")
    st.write("The Refresh button re-reads the local synthetic CSV/JSON files and writes a SQLite snapshot to `database/dashboard.db`. It does not connect to company systems or fetch live data.")
    st.markdown("### Prototype limitations")
    st.write("All records are fictional. No live CRM, third-party operations platform or Google Sheets account is connected. Rule-based insights are explainable examples, not validated AI predictions.")

st.divider()
st.caption("Braahmam International assignment prototype • Synthetic data only • Built for evaluation, not production use")

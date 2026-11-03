import pandas as pd


def generate_insights(crm, operations, targets=None):
    """Create explainable, metric-linked rule-based insights (not an LLM forecast)."""
    insights = []
    if not crm.empty:
        total = len(crm)
        source_counts = crm["source"].fillna("Unknown").value_counts()
        if len(source_counts):
            source = source_counts.index[0]
            count = int(source_counts.iloc[0])
            share = count / total * 100
            insights.append({"title": "Lead-source concentration", "fact": f"{source} generated {count} of {total} leads ({share:.1f}%) in the selected period.", "action": "Review lead quality and conversion by source before reallocating marketing effort."})
        open_rows = crm[crm["status"].eq("Open")]
        if len(open_rows):
            owner_values = open_rows.groupby("owner")["deal_value"].sum().sort_values(ascending=False)
            if len(owner_values):
                owner = str(owner_values.index[0])
                amount = float(owner_values.iloc[0])
                insights.append({"title": "Open-pipeline concentration", "fact": f"{owner} holds the largest open pipeline value: ₹{amount:,.0f}.", "action": "Check workload balance and confirm that high-value opportunities have current next steps."})
        cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=14)
        stale = int((crm["last_activity_date"] < cutoff).fillna(False).sum())
        if stale:
            insights.append({"title": "Follow-up review", "fact": f"{stale} leads have a recorded last-activity date more than 14 days ago. Missing activity dates are excluded from this count and shown in Data Quality.", "action": "Review these lead records and update activity dates after follow-up."})
    if not operations.empty:
        today = pd.Timestamp.today().normalize()
        overdue_mask = (~operations["status"].eq("Completed")) & operations["due_date"].notna() & (operations["due_date"] < today)
        overdue = int(overdue_mask.sum())
        if overdue:
            teams = operations.loc[overdue_mask, "assigned_team"].value_counts()
            top_team = str(teams.index[0]) if len(teams) else "Unassigned"
            insights.append({"title": "Overdue delivery work", "fact": f"{overdue} non-completed projects are past their due date. {top_team} has the highest count among affected teams.", "action": "Review project owners, blockers and revised delivery dates. This is a priority indicator, not a root-cause diagnosis."})
        else:
            insights.append({"title": "Delivery status", "fact": "No non-completed projects with a due date earlier than today were found in the selected records.", "action": "Continue monitoring due dates and SLA status."})
    if not insights:
        insights.append({"title": "No records in selection", "fact": "The current filters returned no records for the selected data view.", "action": "Widen the date range or change the filters."})
    return insights

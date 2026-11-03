import pandas as pd


def sales_kpis(crm):
    total = len(crm)
    won = int(crm["status"].eq("Won").sum())
    lost = int(crm["status"].eq("Lost").sum())
    open_rows = crm[crm["status"].eq("Open")]
    cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(days=14)
    stale = int((crm["last_activity_date"] < cutoff).fillna(False).sum())
    return {
        "total_leads": total,
        "open_opportunities": len(open_rows),
        "open_pipeline_value": float(open_rows["deal_value"].sum()),
        "won_deals": won,
        "lost_deals": lost,
        "conversion_rate": (won / total * 100) if total else 0.0,
        "stale_leads": stale,
        "won_value": float(crm.loc[crm["status"].eq("Won"), "deal_value"].sum()),
    }


def operations_kpis(ops, as_of=None):
    today = pd.Timestamp(as_of or pd.Timestamp.today()).normalize()
    completed = ops["status"].eq("Completed")
    overdue = (~completed) & ops["due_date"].notna() & (ops["due_date"] < today)
    return {
        "total_projects": len(ops),
        "open_projects": int((~completed).sum()),
        "completed_projects": int(completed.sum()),
        "overdue_projects": int(overdue.sum()),
        "total_project_value": float(ops["amount"].sum()),
        "sla_breached": int(ops["sla_status"].eq("Breached").sum()),
    }


def target_comparison(crm, targets):
    """Illustrative comparison: won deal value grouped by lead-created month and region.

    This is a proxy, not recognized revenue or a true closed-date actual.
    """
    won = crm[crm["status"].eq("Won")].copy()
    if won.empty or targets.empty:
        return pd.DataFrame(columns=["month", "region", "target", "won_deal_value_proxy", "achievement_pct"])
    won["month"] = pd.to_datetime(won["created_date"]).dt.to_period("M").dt.to_timestamp()
    actuals = won.groupby(["month", "region"], as_index=False)["deal_value"].sum()
    actuals = actuals.rename(columns={"deal_value": "won_deal_value_proxy"})
    target_data = targets.copy()
    target_data["month"] = pd.to_datetime(target_data["month"]).dt.to_period("M").dt.to_timestamp()
    result = target_data.groupby(["month", "region"], as_index=False).agg(target=("target", "sum"), forecast=("forecast", "sum"))
    result = result.merge(actuals, on=["month", "region"], how="left")
    result["won_deal_value_proxy"] = result["won_deal_value_proxy"].fillna(0)
    result["achievement_pct"] = result.apply(lambda r: (r["won_deal_value_proxy"] / r["target"] * 100) if r["target"] else 0, axis=1)
    return result

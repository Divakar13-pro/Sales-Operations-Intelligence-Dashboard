import pandas as pd


def _normalize_labels(series):
    return series.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)


def _normalize_status(series):
    aliases = {
        "in progress": "In Progress", "in-progress": "In Progress", "progress": "In Progress",
        "complete": "Completed", "done": "Completed", "closed won": "Won",
        "closed lost": "Lost", "pending": "Pending", "open": "Open",
        "won": "Won", "lost": "Lost", "completed": "Completed"
    }
    clean = _normalize_labels(series)
    return clean.str.lower().map(aliases).fillna(clean.str.title())


def clean_all(frames):
    crm = frames["crm"].copy()
    ops = frames["operations"].copy()
    targets = frames["targets"].copy()
    mapping = frames["mapping"].copy()

    for col in ["created_date", "last_activity_date"]:
        crm[col] = pd.to_datetime(crm[col], errors="coerce")
    for col in ["created_date", "due_date", "completed_date"]:
        ops[col] = pd.to_datetime(ops[col], errors="coerce")
    targets["month"] = pd.to_datetime(targets["month"], errors="coerce")

    for col in ["source", "owner", "company_name", "region", "pipeline_stage", "account_id", "lead_id", "contact_id"]:
        if col in crm:
            crm[col] = _normalize_labels(crm[col])
    crm["status"] = _normalize_status(crm["status"])
    for col in ["status", "service_type", "assigned_team", "sla_status", "client_id", "project_id"]:
        if col in ops:
            ops[col] = _normalize_status(ops[col]) if col == "status" else _normalize_labels(ops[col])
    for col in ["region", "account_segment", "campaign_mapping"]:
        if col in targets:
            targets[col] = _normalize_labels(targets[col])
    for col in ["account_id", "client_id", "region"]:
        if col in mapping:
            mapping[col] = _normalize_labels(mapping[col])

    crm["deal_value"] = pd.to_numeric(crm["deal_value"], errors="coerce")
    ops["amount"] = pd.to_numeric(ops["amount"], errors="coerce")
    for col in ["target", "forecast"]:
        targets[col] = pd.to_numeric(targets[col], errors="coerce")

    # Null amounts are kept null in the source-quality report, then treated as zero for sums.
    crm["deal_value"] = crm["deal_value"].fillna(0)
    ops["amount"] = ops["amount"].fillna(0)
    targets[["target", "forecast"]] = targets[["target", "forecast"]].fillna(0)
    return {"crm": crm, "operations": ops, "targets": targets, "mapping": mapping}


def deduplicate_records(df, key):
    """Keep the first record per business key; source duplicates remain visible in quality reporting."""
    if key not in df.columns:
        return df.copy()
    return df.drop_duplicates(subset=[key], keep="first").copy()

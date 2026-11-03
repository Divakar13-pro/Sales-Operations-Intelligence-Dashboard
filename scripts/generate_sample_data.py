"""Generate realistic-looking fictional datasets for the assignment prototype."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
rng = np.random.default_rng(42)
regions = ["Bengaluru", "Mumbai", "Chennai", "Hyderabad", "Pune"]
owners = ["Aarav", "Diya", "Kabir", "Meera", "Rohan"]
sources = ["Website", "LinkedIn", "Referral", "Advertisement", "Email"]
stages = ["New", "Qualified", "Proposal", "Negotiation"]
accounts = [f"A{i:04d}" for i in range(1, 91)]

# Explicit cross-system bridge. CRM region is sourced from this bridge for mapped accounts.
mapping = pd.DataFrame({
    "account_id": accounts[:78],
    "client_id": [f"C{i:04d}" for i in range(1, 79)],
    "region": [regions[(i - 1) % len(regions)] for i in range(1, 79)],
})
mapping.to_csv(DATA / "account_mapping.csv", index=False)
region_by_account = dict(zip(mapping.account_id, mapping.region))

n = 300
created = pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 306, n), unit="D")
crm_accounts = rng.choice(accounts, n)
crm_regions = [region_by_account.get(a, rng.choice(regions)) for a in crm_accounts]
crm = pd.DataFrame({
    "lead_id": [f"L{i:05d}" for i in range(1, n + 1)],
    "contact_id": [f"CT{i:05d}" for i in range(1, n + 1)],
    "account_id": crm_accounts,
    "created_date": created,
    "source": rng.choice(sources, n, p=[.30, .22, .20, .18, .10]),
    "owner": rng.choice(owners, n),
    "company_name": [f"Sample Company {int(x[1:]):03d}" for x in crm_accounts],
    "region": crm_regions,
    "pipeline_stage": rng.choice(stages, n, p=[.30, .30, .25, .15]),
    "deal_value": rng.integers(15000, 250000, n),
    "status": rng.choice(["Open", "Won", "Lost"], n, p=[.62, .23, .15]),
    "last_activity_date": pd.to_datetime([min(d + pd.Timedelta(days=int(delta)), pd.Timestamp("2026-11-03")) for d, delta in zip(created, rng.integers(0, 15, n))]),
})
crm.loc[7, "company_name"] = None
crm.loc[12, "last_activity_date"] = None
crm = pd.concat([crm, crm.iloc[[0]]], ignore_index=True)  # intentional duplicate to demonstrate quality checks
crm.to_csv(DATA / "crm_data.csv", index=False, date_format="%Y-%m-%d")

m = 160
project_created = pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 290, m), unit="D")
statuses = rng.choice(["Open", "In Progress", "Completed"], m, p=[.18, .45, .37])
due = project_created + pd.to_timedelta(rng.integers(15, 75, m), unit="D")
completed = [due[i] + pd.to_timedelta(int(rng.integers(-10, 20)), unit="D") if statuses[i] == "Completed" else None for i in range(m)]
ops = pd.DataFrame({
    "project_id": [f"P{i:05d}" for i in range(1, m + 1)],
    "client_id": rng.choice([f"C{i:04d}" for i in range(1, 91)], m),
    "status": statuses,
    "service_type": rng.choice(["Implementation", "Consulting", "Support", "Development", "Training"], m),
    "created_date": project_created,
    "due_date": due,
    "completed_date": completed,
    "amount": rng.integers(10000, 300000, m),
    "assigned_team": rng.choice(["Delivery A", "Delivery B", "Support", "Consulting"], m),
    "sla_status": rng.choice(["Met", "At Risk", "Breached"], m, p=[.65, .22, .13]),
})
ops.loc[4, "amount"] = None
ops.to_json(DATA / "operations_data.json", orient="records", date_format="iso", indent=2)

rows = []
for month in pd.date_range("2026-01-01", periods=10, freq="MS"):
    for region in regions:
        target = int(rng.integers(350000, 800000))
        rows.append({"month": month.strftime("%Y-%m-%d"), "region": region,
                     "target": target, "forecast": int(target * rng.uniform(.85, 1.15)),
                     "account_segment": rng.choice(["SMB", "Mid-Market", "Enterprise"]),
                     "campaign_mapping": rng.choice(["Campaign Alpha", "Campaign Beta", "Campaign Gamma"])})
pd.DataFrame(rows).to_csv(DATA / "sales_targets.csv", index=False)
print(f"Generated CRM ({len(crm)} rows), Operations ({len(ops)} rows), Targets ({len(rows)} rows), Mapping ({len(mapping)} rows) in {DATA}")

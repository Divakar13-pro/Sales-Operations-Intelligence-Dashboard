import pandas as pd
from modules.kpi_calculations import sales_kpis, operations_kpis, target_comparison
from modules.data_cleaning import deduplicate_records
from modules.data_integration import mapping_summary


def test_sales_kpis():
    df = pd.DataFrame({
        "status": ["Open", "Won", "Lost"],
        "deal_value": [100, 200, 50],
        "last_activity_date": pd.to_datetime(["2026-01-01"] * 3),
    })
    result = sales_kpis(df)
    assert result["total_leads"] == 3
    assert result["open_opportunities"] == 1
    assert result["open_pipeline_value"] == 100
    assert result["won_deals"] == 1
    assert abs(result["conversion_rate"] - (100 / 3)) < 1e-9


def test_operations_kpis():
    today = pd.Timestamp("2026-11-03")
    df = pd.DataFrame({
        "status": ["Completed", "Open"],
        "due_date": [today - pd.Timedelta(days=2), today - pd.Timedelta(days=1)],
        "amount": [100, 200],
        "sla_status": ["Met", "Breached"],
    })
    result = operations_kpis(df, as_of=today)
    assert result["total_projects"] == 2
    assert result["completed_projects"] == 1
    assert result["overdue_projects"] == 1
    assert result["sla_breached"] == 1


def test_deduplication_uses_business_key():
    df = pd.DataFrame({"lead_id": ["L1", "L1", "L2"], "value": [10, 10, 20]})
    assert len(deduplicate_records(df, "lead_id")) == 2


def test_mapping_summary_reports_unmatched_ids():
    crm = pd.DataFrame({"account_id": ["A1", "A2"]})
    ops = pd.DataFrame({"client_id": ["C1", "C2"]})
    mapping = pd.DataFrame({"account_id": ["A1"], "client_id": ["C1"], "region": ["Bengaluru"]})
    result = mapping_summary(crm, ops, mapping)
    assert result["crm_accounts_with_mapping"] == 1
    assert result["crm_accounts_without_mapping"] == 1
    assert result["operations_clients_without_mapping"] == 1


def test_target_comparison_calculates_proxy():
    crm = pd.DataFrame({
        "status": ["Won", "Open"], "created_date": pd.to_datetime(["2026-01-15", "2026-01-20"]),
        "region": ["Bengaluru", "Bengaluru"], "deal_value": [250, 100]
    })
    targets = pd.DataFrame({"month": pd.to_datetime(["2026-01-01"]), "region": ["Bengaluru"], "target": [500], "forecast": [550]})
    result = target_comparison(crm, targets)
    assert result.iloc[0]["won_deal_value_proxy"] == 250
    assert result.iloc[0]["achievement_pct"] == 50


def test_generated_sample_data_has_three_sources_and_mapping():
    from modules.data_loader import load_all_data
    frames = load_all_data()
    assert len(frames["crm"]) >= 100
    assert len(frames["operations"]) >= 50
    assert len(frames["targets"]) >= 10
    assert {"account_id", "client_id", "region"}.issubset(frames["mapping"].columns)


def test_join_uses_explicit_bridge():
    from modules.data_integration import integrate_sales_operations
    crm = pd.DataFrame({"lead_id": ["L1"], "account_id": ["A1"], "status": ["Open"]})
    ops = pd.DataFrame({"project_id": ["P1"], "client_id": ["C1"], "status": ["In Progress"]})
    mapping = pd.DataFrame({"account_id": ["A1"], "client_id": ["C1"], "region": ["Bengaluru"]})
    joined = integrate_sales_operations(crm, ops, mapping)
    assert len(joined) == 1
    assert joined.loc[0, "operations_match"] == "both"

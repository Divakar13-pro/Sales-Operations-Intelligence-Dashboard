import pandas as pd


def integrate_sales_operations(crm, operations, mapping):
    """Join account-level CRM and operations data only through the documented bridge."""
    bridge = mapping[["account_id", "client_id", "region"]].rename(columns={"region": "mapped_region"}).drop_duplicates(subset=["account_id"])
    crm_accounts = crm.merge(bridge, on="account_id", how="left", indicator="mapping_match")
    combined = crm_accounts.merge(
        operations, on="client_id", how="left", suffixes=("_crm", "_ops"),
        indicator="operations_match"
    )
    return combined


def mapping_summary(crm, operations, mapping):
    crm_accounts = set(crm["account_id"].dropna().astype(str))
    mapped_accounts = set(mapping["account_id"].dropna().astype(str))
    mapped_clients = set(mapping["client_id"].dropna().astype(str))
    ops_clients = set(operations["client_id"].dropna().astype(str))
    return {
        "crm_accounts": len(crm_accounts),
        "crm_accounts_with_mapping": len(crm_accounts & mapped_accounts),
        "crm_accounts_without_mapping": len(crm_accounts - mapped_accounts),
        "operations_clients": len(ops_clients),
        "operations_clients_with_mapping": len(ops_clients & mapped_clients),
        "operations_clients_without_mapping": len(ops_clients - mapped_clients),
    }

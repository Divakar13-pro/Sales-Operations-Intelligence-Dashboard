# Assumptions and Limitations

- All organizations, leads, clients, projects, values and activity records are fictional.
- Sample monetary values are shown as INR.
- CRM `account_id` maps to Operations `client_id` only through `account_mapping.csv`.
- For mapped accounts, region is consistent across CRM and the bridge. Unmapped operations clients cannot be assigned a region from the bridge and are not included when a specific region is selected.
- Duplicate CRM leads and duplicate operations projects are removed from KPI analysis by business key; raw records remain available for quality reporting.
- Lead-to-won rate is a simplified cohort ratio.
- Won deal value is grouped by lead-created month for the target comparison proxy because a closed/won date is not provided.
- Rule-based insights describe observed patterns and offer review prompts; they do not establish causality or predict future results.
- Refresh reloads static local files and writes a SQLite snapshot; it does not synchronize with live services.
- Authentication, enterprise permissions, production monitoring and a production warehouse are out of scope.

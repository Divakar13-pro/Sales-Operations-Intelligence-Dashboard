# Data Dictionary

All data is fictional and generated for this prototype. Amounts are illustrative Indian Rupees (INR); dates are ISO `YYYY-MM-DD` or ISO timestamps.

## CRM — `data/crm_data.csv`
- `lead_id`: CRM lead business key.
- `contact_id`: contact identifier; not interchangeable with lead or project IDs.
- `account_id`: CRM account identifier, linked to operations only through the bridge file.
- `created_date`: lead creation date.
- `source`: lead acquisition channel.
- `owner`: sales owner.
- `company_name`: fictional account/company label.
- `region`: sample sales region; for mapped accounts, generated consistently with the bridge.
- `pipeline_stage`: New, Qualified, Proposal or Negotiation.
- `deal_value`: illustrative deal amount in INR.
- `status`: Open, Won or Lost.
- `last_activity_date`: latest recorded activity date.

## Operations — `data/operations_data.json`
- `project_id`: unique project/order identifier.
- `client_id`: operations-side client identifier.
- `status`: Open, In Progress or Completed.
- `service_type`: type of service delivered.
- `created_date`, `due_date`, `completed_date`: project lifecycle dates.
- `amount`: illustrative project amount in INR.
- `assigned_team`: responsible operations team.
- `sla_status`: Met, At Risk or Breached.

## Spreadsheet representation — `data/sales_targets.csv`
- `month`: target month.
- `region`: sales region.
- `target`: illustrative monthly target in INR.
- `forecast`: illustrative forecast in INR.
- `account_segment`: SMB, Mid-Market or Enterprise.
- `campaign_mapping`: fictional campaign category.

## Mapping bridge — `data/account_mapping.csv`
- `account_id`: CRM account key.
- `client_id`: operations client key.
- `region`: shared sample region used to filter operations by region.

The sample deliberately includes missing fields, one duplicate CRM lead row, and unmapped accounts/clients to demonstrate data-quality reporting.

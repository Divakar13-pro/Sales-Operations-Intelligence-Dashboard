# KPI Definitions

- **Unique leads:** number of distinct CRM `lead_id` values after deduplication.
- **Open opportunities:** unique CRM leads whose status is `Open`.
- **Open pipeline value:** sum of `deal_value` for open unique leads. This is potential value, not recognized revenue.
- **Won / Lost deals:** count of unique CRM leads with the respective status.
- **Lead-to-won rate:** Won unique leads divided by all unique leads in the selected cohort × 100. It is not a stage-to-stage conversion metric.
- **Stale leads:** leads whose non-null `last_activity_date` is more than 14 days before runtime date. Missing dates are reported separately and are not silently classified as stale.
- **Open projects:** unique operations projects not marked `Completed`.
- **Overdue projects:** non-completed projects with `due_date` before runtime date.
- **Completed projects:** unique operations projects marked `Completed`.
- **SLA breaches:** projects whose SLA status is `Breached`.
- **Target comparison proxy:** Won deal value grouped by lead-created month and region, compared with monthly target. This is not recognized revenue or a closed-date actual, and is labelled as a proxy in the UI.

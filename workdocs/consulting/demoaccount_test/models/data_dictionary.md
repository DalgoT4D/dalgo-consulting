# Data Dictionary — Demo Account Test

## Data Dictionary

| schema | model_name | column_name | data_type | plain_english_description | example_value | source_table | source_column | kpi_ids | dashboards_or_visuals | filter_or_drilldown_usage | pii | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| staging | stg_orders | order_id | varchar | Unique identifier for an order. |  | staging.raw_orders | id | kpi_001, kpi_002 | dash_001 |  | false | Used to preserve order-level grain. |
| staging | stg_orders | customer | varchar | Customer name from the raw order source. |  | staging.raw_orders | customer |  |  |  | true | PII retained only in staging and excluded from downstream marts. |
| staging | stg_orders | store_id | varchar | Identifier of the store where the order was placed. |  | staging.raw_orders | store_id | kpi_001, kpi_002 | dash_001 | Store filter via joined store name | false | Joins to stg_stores.store_id. |
| staging | stg_orders | order_total | numeric | Total order amount. | 3015 | staging.raw_orders | order_total | kpi_001, kpi_002 | vis_001, vis_002, vis_003 |  | false | Primary amount for gross revenue and calculated tax. |
| staging | stg_orders | tax_paid | numeric | Tax amount recorded on the order. | 16 | staging.raw_orders | tax_paid | kpi_001 | vis_003 |  | false | Retained to validate calculated tax. |
| staging | stg_orders | order_date | date | Calendar date when the order was placed. | 2017-02-26 | staging.raw_orders | ordered_at | kpi_001, kpi_002 | vis_001, vis_002, vis_003 | Order Date filter and month → week → day drilldown | false | Derived from the parsed ordered_at timestamp. |
| staging | stg_stores | store_id | varchar | Unique identifier for a store. |  | staging.raw_stores | id | kpi_001, kpi_002 | dash_001 | Store filter | false | Joins to stg_orders.store_id. |
| staging | stg_stores | store_name | varchar | Store display name. | Chicago | staging.raw_stores | name | kpi_001, kpi_002 | vis_001, vis_002, vis_003 | Store Name filter and chart grouping | false |  |
| staging | stg_stores | tax_rate | numeric | Tax rate for the store. | 0.06 | staging.raw_stores | tax_rate | kpi_001 | vis_003 |  | false | Used to calculate tax from order totals. |
| intermediate | int_order_store_sales | calculated_tax_paid | numeric | Calculated tax amount for an order. |  | staging.raw_orders, staging.raw_stores | order_total, tax_rate | kpi_001 | vis_003 |  | false | Calculated as order_total multiplied by tax_rate. |
| marts | marts_store_sales_daily | gross_revenue | numeric | Total order value for a store on a date. |  | int_order_store_sales | order_total | kpi_002 | vis_001, vis_002 | Aggregates by store and date filters | false |  |
| marts | marts_store_sales_daily | calculated_tax_paid | numeric | Calculated tax amount for a store on a date. |  | int_order_store_sales | calculated_tax_paid | kpi_001 | vis_003 | Aggregates by store, week, and month | false | Default tax metric until client confirms raw versus calculated tax. |
| marts | marts_store_sales_daily | tax_variance | numeric | Difference between calculated tax and raw tax paid. |  | int_order_store_sales | calculated_tax_paid, tax_paid | kpi_001 | vis_003 |  | false | Used for validation and review. |

## Model Summary

| schema | model_name | model_type | grain | purpose | upstream_models | kpis_supported | dashboards_or_visuals_supported | refresh_or_cadence_notes | validation_notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| staging | stg_orders | staging | one row per order | Clean raw order records and cast text amounts and timestamps. | source: staging.raw_orders | kpi_001, kpi_002 | dash_001 | Follows raw order refresh cadence. | dbt execution blocked in this environment; row count should match raw_orders. |
| staging | stg_stores | staging | one row per store | Clean store lookup records and cast tax rates. | source: staging.raw_stores | kpi_001, kpi_002 | dash_001 | Follows raw store refresh cadence. | dbt execution blocked in this environment; store_id should be unique. |
| intermediate | int_order_store_sales | intermediate | one row per order | Join orders to stores using store_id and calculate order-level tax. | stg_orders, stg_stores | kpi_001, kpi_002 | dash_001 | Rebuilds from staging models. | dbt execution blocked; verify no row loss versus stg_orders. |
| marts | marts_store_sales_daily | marts | one row per store per order date | Provide chart-ready store revenue and tax metrics for Dalgo dashboards. | int_order_store_sales | kpi_001, kpi_002 | dash_001, vis_001, vis_002, vis_003 | Supports daily revenue and monthly tax reporting. | dbt execution blocked; verify totals against staged order amounts. |

## Open Questions

| question_id | related_model_or_column | question | why_it_matters | owner | status |
| --- | --- | --- | --- | --- | --- |
| dq_001 | marts_store_sales_daily.calculated_tax_paid | Should official tax reporting use calculated tax or raw tax_paid? | The dashboard metric may differ if source tax values include rounding or adjustments. | client | needs_client_input |
| dq_002 | all generated dbt models | Can the generated models be run through dbt using the intended project profile? | Direct dbt CLI execution is blocked in this session and the project profile is missing locally. | consultant | active |

# ER Diagram — Demo Account Test

## Inputs Reviewed

- `workdocs/consulting/demoaccount_test/discovery/me_goals.md`
- `workdocs/consulting/demoaccount_test/framework/kpi_framework.json`
- `workdocs/consulting/demoaccount_test/framework/dbt_plan.md`
- `/Users/pratiksharao/code/dbt_demoaccount/models/sources/sources.yml`

## Mermaid ER Diagram

```mermaid
erDiagram
    RAW_STORES ||--o{ RAW_ORDERS : "id to store_id"
    RAW_ORDERS ||--|| STG_ORDERS : "cleaned as"
    RAW_STORES ||--|| STG_STORES : "cleaned as"
    STG_STORES ||--o{ INT_ORDER_STORE_SALES : "store_id"
    STG_ORDERS ||--|| INT_ORDER_STORE_SALES : "order_id"
    INT_ORDER_STORE_SALES ||--o{ MARTS_STORE_SALES_DAILY : "aggregated by store and date"

    RAW_ORDERS {
        varchar id PK
        varchar store_id FK
        varchar order_total
        varchar tax_paid
        varchar ordered_at
        varchar customer PII
    }

    RAW_STORES {
        varchar id PK
        varchar name
        varchar tax_rate
        varchar opened_at
    }

    STG_ORDERS {
        varchar order_id PK
        varchar store_id FK
        numeric order_total
        numeric tax_paid
        timestamp ordered_at
        date order_date
    }

    STG_STORES {
        varchar store_id PK
        varchar store_name
        numeric tax_rate
        timestamp opened_at
    }

    INT_ORDER_STORE_SALES {
        varchar order_id PK
        varchar store_id FK
        varchar store_name
        date order_date
        numeric order_total
        numeric tax_paid
        numeric calculated_tax_paid
    }

    MARTS_STORE_SALES_DAILY {
        date order_date PK
        varchar store_id PK
        varchar store_name
        date week_start_date
        date order_month
        bigint order_count
        numeric gross_revenue
        numeric calculated_tax_paid
        numeric raw_tax_paid
        numeric tax_variance
    }
```

## Entity And Grain Notes

| Entity / Model | Grain | Primary Key | Notes |
|---|---|---|---|
| RAW_ORDERS | one row per order | id | Customer is PII and should not flow into marts. |
| RAW_STORES | one row per store | id | Store lookup; six stores profiled. |
| STG_ORDERS | one row per order | order_id | Casts text amounts and timestamps defensively. |
| STG_STORES | one row per store | store_id | Casts tax rate and store opened timestamp. |
| INT_ORDER_STORE_SALES | one row per order | order_id | Adds store name and tax rate to each order. |
| MARTS_STORE_SALES_DAILY | one row per store per order date | order_date + store_id | Chart-ready table for revenue and tax visuals. |

## Source-To-Model Mapping

| Source | Staging | Intermediate | Mart |
|---|---|---|---|
| staging.raw_orders | stg_orders | int_order_store_sales | marts_store_sales_daily |
| staging.raw_stores | stg_stores | int_order_store_sales | marts_store_sales_daily |

## KPI And Visual Join Paths

| KPI / Visual | Serving Model | Join Path | Grain Assumption |
|---|---|---|---|
| kpi_001 Gross Tax paid per store | marts_store_sales_daily | raw_orders.store_id → raw_stores.id | Aggregate order rows to store and date before dashboard rollups. |
| kpi_002 Gross revenue generated per store | marts_store_sales_daily | raw_orders.store_id → raw_stores.id | Sum order_total at the selected date/store grain. |
| vis_001 Gross revenue by store | marts_store_sales_daily | mart only | Dashboard can aggregate daily rows by store. |
| vis_002 Daily gross revenue trend | marts_store_sales_daily | mart only | One row per store per date supports store-colored trends. |
| vis_003 Tax paid by store and week | marts_store_sales_daily | mart only | Dashboard can aggregate daily rows to week. |

## Filter And Drilldown Support

- `store_name` supports the shared store filter.
- `order_date` supports date range filtering.
- `order_month`, `week_start_date`, and `order_date` support month → week → day drilldowns.

## Cardinality Risks

- Store joins should be many orders to one store. Profiling found no duplicate `raw_stores.id` values and no unmatched order store IDs.
- The prior generated model joined `order_total` to `raw_stores.id`; that would cause row loss and incorrect metrics. The planned models use `store_id`.
- If future customer-level metrics are added, customer PII handling must be revisited before adding mart columns.

## Assumptions And Open Questions

- Assumption: `raw_orders.id` is stable and unique enough to use as `order_id`.
- Assumption: `raw_stores.id` is the canonical store key.
- Open question: Confirm whether calculated tax or raw `tax_paid` is the official reporting value.

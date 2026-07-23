# M&E Goals — Demo Account Test

## Engagement Context

Demo Account Test is a test engagement for visualizing sales trends for a jaffle shop. The program areas named in the Requirements Sheet are sales, customer, product, and orders. The overall monitoring and analytics goals are to track customer trends, store trends, product trends, and net profits.

The Requirements Sheet did not provide an NGO website.

## Programs & Reporting

| Program | Reporting Cadence | Audience |
|---|---|---|
| sales | Daily and monthly, depending on metric | Internal Program |
| customer | Not specified | Not specified |
| product | Not specified | Not specified |
| orders | Daily and monthly, depending on metric | Internal Program |

## Key M&E Questions

- How much gross revenue is generated per store?
- How much tax is paid per store location?
- How do sales and order amounts trend by store over daily and monthly reporting periods?
- Which store-level attributes are needed to calculate revenue and tax metrics?

## Data Sources

| Data Source | Table / Form Name | Column Name | Data Type | Description | Example Values |
|---|---|---|---|---|---|
| raw_stores | Google Sheet | name | varchar | store name | Text |
| raw_stores | Google Sheet | tax_rate | varchar | tax rate | percentage (in decimal) |
| raw_stores | Google Sheet | id | varchar | store id | Id |
| raw_orders | Google Sheet | store_id | varchar | store at which order placed | Id |
| raw_orders | Google Sheet | order_total | varchar | order total amount | decimal |
| raw_orders | Google Sheet | id | varchar | order id | Id |

## Metrics Required

| # | Metric Name | What is measured | Calculation logic | Data source ref | Audience | Frequency | Breakdown dimensions | Consultant notes |
|---|---|---|---|---|---|---|---|---|
| 1 | Gross Tax paid per store | Total taxation amount paid per store location | gross revenue generated * tax_rate | raw_stores | Internal Program | Monthly | Store Name, Week |  |
| 2 | Gross revenue generated per store | Total sum of all order amounts at per store location | sum of order_total for all orders | raw_orders, raw_stores | Internal Program | Daily | Store Name |  |

## Open Questions & Ambiguities

- The tax metric references `raw_stores` only, but the calculation requires gross revenue from `raw_orders` joined to `raw_stores` by store ID.
- The required weekly breakdown for the monthly tax metric needs an order date or reporting date column, but the Requirements Sheet only lists order ID, store ID, and order total.
- Customer, product, and net profit goals are mentioned in the engagement context, but the Metrics tab only defines store revenue and store tax metrics.
- The source column data types are recorded as `varchar` in the Requirements Sheet even for numeric fields such as `tax_rate` and `order_total`; dbt staging should cast these defensively.

---
_Generated from Requirements Sheet: https://docs.google.com/spreadsheets/d/1djM6ivz9nHwkGJhYmRWHO5lbG7Ij3TectyzTZFO45DY/edit?usp=sharing_
_Track: new | dbt repo: /Users/pratiksharao/code/dbt_demoaccount | Date: 2026-07-23_

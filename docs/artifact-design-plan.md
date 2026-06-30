# New Engagement — Artifact Design Plan

This document identifies every artifact that must be designed for the new engagement flow, organized by phase. Each artifact listed here needs a template, schema, or scaffold before the agentic skills can be built around the consulting process.

See [process.md](process.md) for the full workflow reference.

---

## Phase 1: Discovery

| Artifact | Format | What needs to be designed |
|---|---|---|
| Requirements Sheet | Google Sheet | 4-tab workbook — single shared artifact for the entire engagement: **Instructions** (column guide for client), **Engagement Context** (consultant-filled: meeting notes, NGO website URL, program names, overall M&E goals), **Data Sources** (consultant-maintained post-ingestion: raw tables and columns for client reference when writing KPI logic), **Metrics** (client-filled: one row per KPI with metric name, what is measured, calculation logic, data source, audience, frequency, breakdown dimensions, consultant notes). |
| `me_goals.md` | Markdown | LLM-generated summary synthesised from all tabs of the Requirements Sheet (Engagement Context + Data Sources + Metrics). Serves as the single source of truth and shared context for all downstream phases — every subsequent skill (data exploration, framework, model development) reads this file as its primary input. |

---

## Phase 2: Data Exploration

| Artifact | Format | What needs to be designed |
|---|---|---|
| `sources.yml` (input) | YAML | Schema that the consultant creates before the LLM runs — raw table names, source system (Kobo, GSheets, etc.), PII column flags with descriptions pre-filled by consultant. |
| `sources.yml` (output) | YAML | Extended schema that the LLM populates — adds column data types, null rates, cardinality, sample values, join key annotations, date field formats, and anomaly notes per column. |

---

## Phase 3: Framework

| Artifact | Format | What needs to be designed |
|---|---|---|
| `metrics.md` | Markdown | Output format of `/curate_metrics` — a deduplicated, annotated list of KPIs with flags for ambiguity and mapping back to Requirements Sheet rows. |
| KPI Framework Sheet | Google Sheet | Template structure: KPI name, requirements alignment, plain English definition, calculation logic, data source(s), filters/conditions, granularity, mart model name, status column. |
| `er_diagram.md` | Markdown (Mermaid) | ER diagram in Mermaid — entities with grain, relationships with cardinality, raw-table-to-entity mapping, and join paths per KPI. |

---

## Phase 4: Model Development

| Artifact | Format | What needs to be designed |
|---|---|---|
| `stg_*.sql` templates | SQL | Staging model scaffold — column rename conventions, cast patterns, dedup logic, null handling, and JSON unnesting patterns. |
| `int_*.sql` templates | SQL | Intermediate model scaffold — join patterns, cohort construction, derived field conventions. |
| `fct_*.sql` / `dim_*.sql` templates | SQL | Mart model scaffold — aggregation patterns, period logic, filter conventions aligned to KPI Framework columns. |
| `schema.yml` | YAML | Structure for dbt column descriptions, tests (not null, unique, accepted values), and dbt-osmosis-compatible metadata blocks. |
| Data Dictionary Sheet | Google Sheet | Template with columns: schema, table name, column name, data type, description, example value, source column, KPI reference. Client-facing — descriptions must be plain English. |

---

## Summary

| Phase | Artifacts to design |
|---|---|
| 1 — Discovery | Requirements Sheet (GSheet — 4 tabs), `me_goals.md` |
| 2 — Data Exploration | `sources.yml` input schema, `sources.yml` output schema |
| 3 — Framework | `metrics.md`, KPI Framework Sheet (GSheet), `er_diagram.md` |
| 4 — Model Development | `stg_*.sql`, `int_*.sql`, `fct_*.sql`/`dim_*.sql`, `schema.yml`, Data Dictionary Sheet (GSheet) |

**Total: 3 Google Sheet templates, 4 Markdown schemas/templates, 3 SQL model scaffolds — 10 artifacts.**

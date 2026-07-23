# Dalgo Consulting - Claude Code Guide

This repo contains the AI-assisted consulting workflow for building dbt data models that transform raw NGO program data into M&E metrics and Dalgo dashboards. Engagements move through four phases: **Discovery -> Data Exploration -> Framework -> Model Development**.

See `docs/process.md` for the full process reference.

## What This Repo Is

- **Not** a product codebase. There is no app to run or deploy here.
- **Yes** a workspace for LLM-assisted consulting: generating artifacts, writing dbt SQL/YAML, exploring raw data, and managing the engagement lifecycle.
- Client dbt project repos are referenced separately. Models may live inside those repos, not here.

## Repo Structure

```
dalgo-consulting/
├── .claude/
│   ├── agents/
│   └── skills/
│       ├── 00-router/
│       ├── 01-discovery/
│       ├── 02-exploration/
│       ├── 03-framework/
│       ├── 04-implementation/
│       ├── 05-change-management/
│       └── 06-delivery/
├── secrets/
│   └── my_service_key.json
├── docs/
│   ├── process.md
│   └── artifact-design-plan.md
├── scripts/
│   ├── read_requirements.py
│   ├── kpi_framework_sheet.py
│   └── data_dictionary_sheet.py
└── workdocs/consulting/
    └── {engagement}/
        ├── discovery/
        │   └── me_goals.md
        ├── data_exploration/
        │   └── sources.yml
        ├── framework/
        │   ├── kpi_framework.md
        │   ├── kpi_framework.json
        │   ├── dbt_plan.md
        │   ├── er_diagram.md
        │   └── phase3_metadata.json
        ├── models/
        │   ├── data_dictionary.md
        │   ├── data_dictionary.json
        │   ├── phase4_metadata.json
        │   ├── staging/
        │   ├── intermediate/
        │   └── marts/
        ├── modifications/
        └── investigations/
```

## Execution Surface

dbt-wizard is the consultant execution surface. It discovers workflow instructions from `.claude/skills/**/SKILL.md`; all workflow logic must live in skills. Slash commands are deprecated and should not be restored.

Start broad user requests with `dalgo-consulting-workflow`. Invoke focused skills directly only when the user names a specific phase or task.

## Skill Organization

| Folder | Skills |
|---|---|
| `00-router` | `dalgo-consulting-workflow` |
| `01-discovery` | `discover-engagement`, `read-requirements` |
| `02-exploration` | `explore-data`, `validate-warehouse-access` |
| `03-framework` | `build-kpi-framework`, `read-kpi-framework`, `plan-dbt-architecture`, `generate-er-diagram` |
| `04-implementation` | `read-phase-context`, `write-dbt-staging`, `write-dbt-intermediate`, `write-dbt-marts`, `generate-data-dictionary` |
| `05-change-management` | `modify-requirements`, `apply-kpi-framework-patch`, `investigate-issue`, `dbt-edit-plan` |
| `06-delivery` | `finalize-dbt-project`, `github-delivery` |

## Core Skills

| Skill | What It Does |
|---|---|
| `dalgo-consulting-workflow` | Master router for new engagements, phase reruns, requirement changes, investigations, implementation, finalization, and GitHub delivery. |
| `discover-engagement` | Creates engagement folders, captures repo/sheet context, and calls `read-requirements` to generate `me_goals.md`. |
| `read-requirements` | Reads the four-tab Requirements Sheet via Google Sheets API and generates or refreshes `me_goals.md`. |
| `explore-data` | Profiles warehouse tables from one or more source YAMLs, respects PII flags, and enriches those same YAMLs in place. |
| `validate-warehouse-access` | Shared tunnel/profile/dbt connectivity validation for warehouse-backed skills. |
| `build-kpi-framework` | Builds the KPI Framework Sheet and local Markdown/JSON artifacts from `me_goals.md` and enriched source YAMLs. |
| `read-kpi-framework` | Refreshes local `kpi_framework.md` and `kpi_framework.json` from the KPI Framework Sheet. |
| `plan-dbt-architecture` | Writes `dbt_plan.md` for dashboards, metrics, charts, alerts, filters, drilldowns, and dbt model layers. |
| `generate-er-diagram` | Writes `er_diagram.md` with valid Mermaid entity syntax and join paths aligned to the dbt plan. |
| `read-phase-context` | Resolves accepted Phase 3 artifacts and dbt repo context for implementation skills. |
| `write-dbt-staging` | Writes `stg_*.sql` and dbt YAML for source-aligned cleaning, casting, deduplication, and null handling. |
| `write-dbt-intermediate` | Writes `int_*.sql` and dbt YAML for joins, cohorts, derived fields, and intermediate reshaping. |
| `write-dbt-marts` | Writes chart-ready `marts_*.sql` and dbt YAML for Dalgo dashboards, charts, filters, drilldowns, and alerts. |
| `generate-data-dictionary` | Produces the client-facing Data Dictionary Sheet plus local Markdown/JSON copies. |
| `finalize-dbt-project` | Runs final dbt validation, SQLFluff checks when available, YAML documentation/test review, and dbt docs generation. |
| `modify-requirements` | Handles requirement changes and proposes KPI Framework edits before invoking `dbt-edit-plan`. |
| `apply-kpi-framework-patch` | Applies a confirmed KPI Framework patch and refreshes local framework artifacts. |
| `investigate-issue` | Diagnoses wrong numbers, duplicates, freshness issues, and dashboard discrepancies; writes findings and every SQL query run. |
| `dbt-edit-plan` | Produces a scoped dbt edit plan and implements SQL/YAML changes only after explicit confirmation. |
| `github-delivery` | Confirms scope, commits, pushes, and optionally opens a PR for GitHub-backed dbt repos. |

## Tracks

**New engagement:** `dalgo-consulting-workflow` -> `discover-engagement` -> `explore-data` -> `build-kpi-framework` -> `plan-dbt-architecture` -> `generate-er-diagram` -> `write-dbt-staging` -> `write-dbt-intermediate` -> `write-dbt-marts` -> `generate-data-dictionary` -> `finalize-dbt-project`.

**Requirement change:** use `modify-requirements`. It writes a durable change folder, proposes KPI Framework changes only when needed, asks for confirmation before sheet edits, then routes dbt changes through `dbt-edit-plan`.

**Model/dashboard bug:** use `investigate-issue`. It validates warehouse access, writes reproducible SQL in `queries.sql`, and either recommends a fix or reports inconclusive findings. Code changes still go through `dbt-edit-plan`.

## Key Constraints

- KPI Framework is the contract. No dbt model should be written without a corresponding KPI, dashboard, chart, filter, drilldown, or alert requirement.
- Chart type belongs in the visual/output rows, not only in the KPI row.
- Marts are chart-ready, not facts/dimensions by default. Final models use `marts_` naming and are shaped around Dalgo output requirements.
- Valid KPI Framework statuses are `active`, `revised`, `deprecated`, and `needs_client_input`.
- `modify-requirements` must not edit the KPI Framework until the user confirms the patch.
- `dbt-edit-plan` must not edit dbt SQL/YAML until the user confirms the plan.
- Any skill that needs to inspect warehouse schemas/tables, verify physical tables, profile source data, run investigative SQL, or run dbt commands that query the warehouse must first ask exactly: `Can I read your database schema tables?`
- `dbt-edit-plan` must update `dbt_plan.md` after implementation when architecture changes.
- Data Dictionary updates are required when exposed models or columns change.
- Warehouse-backed skills must validate profile/tunnel access before querying and must never print credentials, tokens, passwords, private keys, or resolved secret values.
- Investigation artifacts must include the SQL that was run.
- PII must not be exposed in artifacts. Do not store raw sensitive values.
- Finalization is mandatory before every delivery.
- GitHub delivery is explicit and PR-based for client repos.

## Users

The end clients are NGO M&E managers and program staff. Client-facing artifacts such as the KPI Framework Sheet, Data Dictionary Sheet, and `me_goals.md` must be written in plain English: no SQL, no unexplained acronyms, and no implementation jargon unless the artifact is explicitly technical.

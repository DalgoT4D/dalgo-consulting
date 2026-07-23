---
name: dalgo-consulting-workflow
description: "Top-level dbt-wizard router for Dalgo consulting workflows. Use when the user asks to run Phase 1, Phase 2, Phase 3, Phase 4, the whole engagement flow, a modification, an investigation, or a final delivery using the Dalgo consulting process."
---

# Dalgo Consulting Workflow

Use this skill as the canonical dbt-wizard entrypoint. All executable workflow logic lives in skills.

## Routing

Map the user's request to the smallest set of skills that completes the requested phase or workflow.

| User intent | Invoke |
|---|---|
| Start a new engagement, run Phase 1, create `me_goals.md` | `discover-engagement` |
| Read or refresh the Requirements Sheet only | `read-requirements` |
| Run Phase 2, profile raw tables, enrich source YAML | `explore-data` |
| Run Phase 3 end to end | `build-kpi-framework`, then `plan-dbt-architecture`, then `generate-er-diagram` |
| Build only the KPI Framework | `build-kpi-framework` |
| Build only `dbt_plan.md` | `plan-dbt-architecture` |
| Build only `er_diagram.md` | `generate-er-diagram` |
| Run Phase 4 end to end | `write-dbt-staging`, then `write-dbt-intermediate`, then `write-dbt-marts`, then `generate-data-dictionary`, then `finalize-dbt-project` |
| Write or rerun staging only | `write-dbt-staging` |
| Write or rerun intermediate only | `write-dbt-intermediate` |
| Write or rerun marts only | `write-dbt-marts` |
| Generate client data dictionary | `generate-data-dictionary` |
| Final validation and delivery readiness | `finalize-dbt-project` |
| Requirement change to KPI/dashboard/chart/filter/drilldown/alert logic | `modify-requirements` |
| Wrong numbers, duplicates, freshness, dashboard discrepancy, or suspected bug | `investigate-issue` |
| Direct scoped dbt model edit request | `dbt-edit-plan` |

## Full New Engagement Flow

Run in this order unless the user explicitly asks for a subset:

1. `discover-engagement`
2. `explore-data`
3. `build-kpi-framework`
4. `plan-dbt-architecture`
5. `generate-er-diagram`
6. `write-dbt-staging`
7. `write-dbt-intermediate`
8. `write-dbt-marts`
9. `generate-data-dictionary`
10. `finalize-dbt-project`

Do not skip phase prerequisites:
- Phase 2 requires `me_goals.md` and source YAML files.
- Phase 3 requires enriched source YAMLs.
- Phase 4 requires reviewed Phase 3 artifacts unless the user explicitly accepts proceeding from draft artifacts.

## Modification Flow

Requirement changes go through `modify-requirements`.

Data-quality/model/dashboard bugs go through `investigate-issue` first. If the investigation finds a dbt fix, route to `dbt-edit-plan`.

`dbt-edit-plan` is also directly callable when the user already knows which models need editing.

## Confirmation Gates

Preserve these gates in dbt-wizard:
- Any skill that needs to inspect warehouse schemas/tables, verify physical table existence, profile source data, run investigative SQL, or run dbt commands that query the warehouse must ask the user first:
  > "Can I read your database schema tables?"
  Continue only after the user confirms.
- `modify-requirements` must not edit the KPI Framework until the user confirms the proposed KPI Framework patch.
- `dbt-edit-plan` must not edit SQL, macros, source YAML, dbt `.yml`, `dbt_plan.md`, `er_diagram.md`, or Data Dictionary artifacts until the user confirms the dbt edit plan.
- `github-delivery` must not commit, push, or open a PR until the user confirms.

## Shared Context

Every phase after discovery should read `me_goals.md` first. Phase 3 and Phase 4 skills should also use `read-phase-context` when they need accepted artifacts, dbt repo path, metadata, source YAMLs, or existing dbt files.

When warehouse access is needed, invoke `validate-warehouse-access` rather than copying profile/tunnel logic.

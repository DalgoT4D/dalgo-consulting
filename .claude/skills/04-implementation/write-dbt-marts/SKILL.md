---
name: write-dbt-marts
description: "Write and verify chart-ready marts_ dbt models and dbt YAML docs/tests for Dalgo dashboards, charts, filters, drilldowns, alerts, and KPIs."
---

# Write Dbt Marts

Writes `marts_` dbt models for Dalgo dashboards, charts, filters, drilldowns, alerts, and KPIs.

Use this after intermediate models have been written and verified.

The mart layer should be chart-ready. Build `marts_` models around the shapes required by the KPI Framework and `dbt_plan.md`.

---

## Step 0 — Resolve Context

Invoke the `read-phase-context` skill.

Stop if:
- required intermediate models do not exist.
- the KPI Framework has unresolved blockers for mart logic.
- `dbt_plan.md` does not specify mart model names.
- the working tree has unexpected changes in files this skill would edit.

---

## Step 1 — Map Mart Models To Dalgo Outputs

For each planned `marts_` model, confirm:
- dashboards served
- visual IDs served
- KPI IDs served
- output grain
- required metric columns
- required filter columns
- required drilldown columns
- required alert-support columns
- long vs wide shape

If multiple charts need incompatible grains, create separate `marts_` models rather than hiding grain mismatches in one bloated table.

---

## Step 2 — Write Mart Models

Create or update `marts_*.sql` models.

Each mart model should:
- read from `ref()` intermediate or staging models
- expose chart-ready metrics
- include all required filter and drilldown columns
- materialize numerator, denominator, and rate fields where useful for auditability
- implement alert threshold support where required
- use safe division and documented null handling
- make date grain explicit
- avoid requiring core metric calculations in the Dalgo dashboard layer

Use macros for repeated logic identified in `dbt_plan.md`.

---

## Step 3 — Write Mart YAML

Create or update the relevant dbt YAML files, such as `schema.yml` or folder-level `.yml` files used by the client repo.

Include:
- model purpose
- chart/dashboard usage
- grain
- KPI IDs supported
- column descriptions
- tests for keys, metric ranges, accepted values, and important non-null fields
- notes on filters, drilldowns, and alerts

Write the YAML files directly as part of this skill; do not leave documentation/tests as prose-only recommendations.

---

## Step 4 — Run And Verify

Before running dbt commands or warehouse validation queries, ask the user exactly:
> "Can I read your database schema tables?"

Continue only after the user confirms. If the user declines or does not answer, stop before `dbt run` or any warehouse-backed KPI/filter/drilldown checks and report mart validation as blocked.

Run:

```bash
dbt run --select marts --project-dir "{dbt_repo_path}"
```

If the repo does not use a `marts` selector, use the marts model path or `marts_*` selector that fits the repo.

Verify:
- KPI outputs match the KPI Framework definitions
- dashboard-required filters work across related charts
- drilldown paths retain the needed columns and grain
- alert-support fields calculate correctly
- no mart exposes raw PII unnecessarily
- row counts and grains are explainable

Fix failures and rerun until marts pass, or stop with clear blockers.

---

## Step 5 — Update Metadata

Update:

```text
workdocs/consulting/{engagement}/models/phase4_metadata.json
```

Add:

```json
{
  "marts": {
    "status": "complete",
    "models": ["marts_..."],
    "last_run_invocation": "dbt run --select ...",
    "notes": []
  }
}
```

Preserve existing keys.

---

## Step 6 — Completion Summary

Print:

```text
✓ mart models:       {mart_model_count}
✓ dbt YAML files:    updated
✓ dbt run:           passed/blocked
✓ KPI checks:        passed/blocked
✓ filter/drilldown:  passed/blocked
```

Then print:
> "Next → run the `generate-data-dictionary` skill after reviewing mart outputs."

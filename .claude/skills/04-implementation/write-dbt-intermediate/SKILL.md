---
name: write-dbt-intermediate
description: "Write and verify int_ dbt models and dbt YAML docs/tests from staging models, the KPI Framework, dbt_plan.md, and er_diagram.md."
---

# Write Dbt Intermediate

Writes `int_` dbt models from staging models, `dbt_plan.md`, `er_diagram.md`, and the KPI Framework.

Use this after staging models have been written and verified.

---

## Step 0 — Resolve Context

Invoke the `read-phase-context` skill.

Stop if:
- staging models required by `dbt_plan.md` do not exist.
- staging has not been run successfully, unless the user explicitly chooses to proceed.
- the working tree has unexpected changes in files this skill would edit.

---

## Step 1 — Inspect Existing Models And Plan

Read the staging SQL and dbt YAML files.
Use `dbt_plan.md` and `er_diagram.md` to identify required intermediate entities, grains, and join paths.

Pay special attention to:
- one-to-many joins
- many-to-many relationships
- duplicated IDs
- missing join keys
- cohort construction
- date alignment
- filter and drilldown columns needed by marts

---

## Step 2 — Write Intermediate Models

Create or update `int_*.sql` models.

Each intermediate model should:
- read from `ref()` staging models
- define one clear grain
- implement joins with explicit cardinality assumptions
- construct reusable business entities or event tables
- add derived fields needed by multiple marts
- perform light aggregations only when reusable
- protect against fan-out
- preserve filter and drilldown columns needed downstream

Do not calculate final dashboard KPIs unless the calculation is a reusable intermediate building block.

---

## Step 3 — Write Intermediate YAML

Create or update the relevant dbt YAML files, such as `schema.yml` or folder-level `.yml` files used by the client repo.

Include:
- model purpose
- grain
- upstream models
- join assumptions
- column descriptions
- tests for keys and important categorical values
- notes on fan-out or row-loss checks

Write the YAML files directly as part of this skill; do not leave documentation/tests as prose-only recommendations.

---

## Step 4 — Run And Verify

Before running dbt commands or warehouse validation queries, ask the user exactly:
> "Can I read your database schema tables?"

Continue only after the user confirms. If the user declines or does not answer, stop before `dbt run` or any warehouse-backed cardinality/fan-out checks and report intermediate validation as blocked.

Run:

```bash
dbt run --select intermediate --project-dir "{dbt_repo_path}"
```

If the repo does not use an `intermediate` selector, use the intermediate model path or `int_*` selector that fits the repo.

Verify:
- join cardinalities match the ER diagram
- no unexpected fan-out or row loss
- derived fields are correct on spot checks
- intermediate grains match `dbt_plan.md`
- downstream-required filter and drilldown columns are present

Fix failures and rerun until intermediate models pass, or stop with clear blockers.

---

## Step 5 — Update Metadata

Update:

```text
workdocs/consulting/{engagement}/models/phase4_metadata.json
```

Add:

```json
{
  "intermediate": {
    "status": "complete",
    "models": ["int_..."],
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
✓ intermediate models: {intermediate_model_count}
✓ dbt YAML files:      updated
✓ dbt run:             passed/blocked
✓ cardinality checks:  passed/blocked
```

Then print:
> "Next → run the `write-dbt-marts` skill after reviewing intermediate outputs."

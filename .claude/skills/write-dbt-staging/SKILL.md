---
name: write-dbt-staging
description: "Write and verify stg_ dbt models and dbt YAML docs/tests from enriched source YAMLs and the accepted dbt_plan.md."
---

# Write Dbt Staging

Writes `stg_` dbt models from enriched source YAMLs and the accepted `dbt_plan.md`.

Use this after Phase 3 has been reviewed. Staging models should clean raw sources without implementing business KPI logic.

Treat the skill input as optional source YAML paths or a dbt selector.

---

## Step 0 — Resolve Context

Invoke the `read-phase-context` skill.

Stop if:
- `dbt_plan.md` is missing.
- source YAMLs are missing.
- the dbt repo cannot be resolved.
- the working tree has uncommitted changes in files this skill would edit and the user has not confirmed they are expected.

---

## Step 1 — Inspect Existing dbt Conventions

Before writing code, inspect:
- `dbt_project.yml` model paths and schema naming
- existing staging models
- existing `schema.yml` layout
- existing macros
- SQL style conventions, including CTE naming and references

Follow the client repo's conventions.

---

## Step 2 — Write Staging Models

For every staging model required by `dbt_plan.md`, create or update `stg_*.sql`.

Each staging model should:
- read from dbt `source()` definitions
- preserve source row grain unless deduplication is explicitly required
- rename columns into clear snake_case names
- cast dates, timestamps, numbers, booleans, and IDs defensively
- normalize common enumerations where appropriate
- handle blank strings and null-like placeholders
- extract or flatten JSON only when downstream models need those fields
- deduplicate using a documented rule from the source YAML or dbt plan
- avoid business KPI calculations
- avoid exposing raw PII unless required for joins or deduplication

If reusable logic appears across staging models, add a macro only when it materially reduces duplication or risk.

---

## Step 3 — Write Staging YAML

Create or update the relevant dbt YAML files, such as `schema.yml` or folder-level `.yml` files used by the client repo.

For every staging model:
- add model description
- add column descriptions
- add useful dbt tests such as `not_null`, `unique`, `accepted_values`, and relationships when appropriate
- document source lineage
- document PII-sensitive columns without including raw values

Write the YAML files directly as part of this skill; do not leave documentation/tests as prose-only recommendations.

---

## Step 4 — Run And Verify

Run:

```bash
dbt run --select staging --project-dir "{dbt_repo_path}"
```

If the repo does not use a `staging` selector, use the staging model path or `stg_*` selector that fits the repo.

Then verify:
- staging row counts match or intentionally differ from sources
- key columns have expected null rates
- type casts succeeded
- deduplication did not drop unexpected rows
- PII is not accidentally exposed in generated docs or sample outputs

Fix failures and rerun until staging passes, or stop with clear blockers.

---

## Step 5 — Update Metadata

Create or update:

```text
workdocs/consulting/{engagement}/models/phase4_metadata.json
```

Add:

```json
{
  "staging": {
    "status": "complete",
    "models": ["stg_..."],
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
✓ dbt repo:        {dbt_repo_path}
✓ staging models:  {staging_model_count}
✓ dbt YAML files:  updated
✓ dbt run:         passed/blocked
```

Then print:
> "Next → run the `write-dbt-intermediate` skill after reviewing staging outputs."

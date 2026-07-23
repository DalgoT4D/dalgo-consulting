---
name: modify-requirements
description: "Handle existing Dalgo engagement requirement changes: create an auditable change folder, classify requirement changes versus bugs, draft and confirm KPI Framework changes, then route to dbt-edit-plan."
---

# Modify Requirements

Entry point for requirement changes on an existing Dalgo engagement.

Use the `modify-requirements` skill for new KPIs, revised KPI logic, new dashboard/chart/filter/drilldown/alert requirements, or new source requirements.

Do not use the `modify-requirements` skill for wrong numbers, duplicates, freshness problems, or suspected model/dashboard bugs. Route those to the `investigate-issue` skill first.

Treat the skill input as the change request.

---

## Step 0 — Resolve Context

If no change request text was provided, ask:
> "What change do you want to make to this existing engagement?"

Invoke the `read-phase-context` skill.

Create a durable change folder:

```text
workdocs/consulting/{engagement}/modifications/{YYYYMMDD_HHMMSS}_{slug}/
```

Write:

```text
workdocs/consulting/{engagement}/modifications/{change}/change_request.md
```

Include:
- original user request
- engagement
- dbt repo path
- timestamp
- initial classification

---

## Step 1 — Classify The Request

Classify the request as:

- requirement change
- data-quality/model/dashboard bug
- unclear

If it is a data-quality/model/dashboard bug, stop the `modify-requirements` skill and route to:

```text
Invoke the `investigate-issue` skill with `{original_request}`.
```

If unclear, ask one clarifying question to determine whether this is a requirement change or a bug.

Proceed only for requirement changes.

---

## Step 2 — Check For New Source Work

If the change requires a new data source or previously unexplored source table:

1. Record that in `change_request.md`.
2. Tell the user:
   > "This change needs source ingestion/exploration before dbt edits can be planned. Ingest the source via Airbyte, then run the `explore-data` skill with `path/to/source.yml`."
3. Stop before KPI Framework or dbt code edits unless the user already provided enriched source YAMLs for the new source.

If enriched source YAMLs are already available, continue.

---

## Step 3 — Determine Whether KPI Framework Changes Are Needed

Read the current KPI Framework tabs and determine whether the request requires changes to:

- KPI Catalog
- Dashboard Outputs
- Charts & Visuals
- Filters & Drilldowns
- Alerts
- Open Questions

Some changes may not require KPI Framework edits, such as a purely technical implementation cleanup that does not alter the analytics contract.

If no KPI Framework edits are needed:
- record that decision in `change_request.md`
- skip to Step 7 and invoke the `dbt-edit-plan` skill

---

## Step 4 — Draft KPI Framework Patch

If KPI Framework edits are needed, draft:

```text
workdocs/consulting/{engagement}/modifications/{change}/kpi_framework_patch.json
```

The patch should describe:
- rows to add
- rows to revise
- rows to deprecate
- tabs affected
- exact field changes
- reason for each change

Use KPI Framework status values:
- `active`
- `revised`
- `deprecated`
- `needs_client_input`

Use `needs_client_input` for unresolved open questions. Do not use `open`, `closed`, `draft`, `planned`, or any other status value in KPI Framework patches.

Set:
- `change_request_id`
- `change_reason`
- `changed_at`

Do not write the Google Sheet yet.

---

## Step 5 — KPI Framework Confirmation Gate

Show the proposed KPI Framework changes in a concise table.

Ask:
> "Confirm that I should apply these KPI Framework changes? This will update the Google Sheet. (yes / no)"

If the answer is not clearly yes:
- stop
- leave `kpi_framework_patch.json` and `change_request.md` in the modification folder
- do not edit the KPI Framework Sheet
- do not call the `dbt-edit-plan` skill

---

## Step 6 — Apply Confirmed KPI Framework Changes

If confirmed:

Invoke the `apply-kpi-framework-patch` skill with:
- `{engagement}`
- `{patch_path}`
- `{spreadsheet_id}`
- `{change_request_id}`

Do not drop existing rows or tabs not mentioned by the patch.

---

## Step 7 — Invoke The `dbt-edit-plan` Skill

Invoke:

```text
Invoke the `dbt-edit-plan` skill with `workdocs/consulting/{engagement}/modifications/{change}/change_request.md`.
```

Pass along:
- the modification folder
- `kpi_framework_patch.json` if one exists
- whether KPI Framework edits were applied

The `dbt-edit-plan` skill must still ask for explicit confirmation before editing dbt code.

---

## Step 8 — Completion Summary

Print:

```text
✓ change request:       workdocs/consulting/{engagement}/modifications/{change}/change_request.md
✓ KPI Framework edits:  applied/skipped/not confirmed
✓ next step:            dbt-edit-plan
```

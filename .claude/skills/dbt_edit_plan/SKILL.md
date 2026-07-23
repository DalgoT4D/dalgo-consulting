---
name: dbt_edit_plan
description: Plan and, after explicit confirmation, implement scoped dbt edits for an existing Dalgo engagement using the KPI Framework, dbt_plan.md, er_diagram.md, source YAMLs, and current dbt repo.
---

# dbt Edit Plan

Create a scoped edit plan for dbt changes, then implement it only after explicit user confirmation.

Use this skill from `/dbt_edit_plan`, `/modify`, or `/investigate` when dbt models, macros, source YAMLs, or dbt model `.yml` files may need changes.

## Inputs

- `{change_request_path}` — optional path to a durable change request
- `{investigation_path}` — optional path to investigation findings
- `{user_prompt}` — optional direct user request
- `{engagement}` — optional engagement slug
- `{dbt_repo_path}` — optional dbt repo path
- `{mode}` — `plan` or `implement_confirmed`; default `plan`

## Step 1 — Resolve Context

Invoke `read_phase_context`.

Read fully:
- `me_goals.md`
- `kpi_framework.json`
- `dbt_plan.md`
- `er_diagram.md`
- enriched source YAMLs
- relevant SQL models and dbt `.yml` files
- optional `{change_request_path}`
- optional `{investigation_path}`

## Step 2 — Create Durable Edit Folder

If the caller did not provide a modification folder, create one:

```text
workdocs/consulting/{engagement}/modifications/{YYYYMMDD_HHMMSS}_{slug}/
```

Use a short slug derived from the user prompt, change request, or investigation title.

## Step 3 — Classify The Edit

Classify the requested work as one or more of:

- KPI/analytics requirement change
- dashboard/chart/filter/drilldown/alert shape change
- data-quality fix
- source YAML update
- staging model edit
- intermediate model edit
- `marts_` model edit
- macro edit
- dbt `.yml` documentation/test edit
- Data Dictionary refresh
- architecture update requiring `dbt_plan.md`
- relationship update requiring `er_diagram.md`

## Step 4 — Draft `dbt_edit_plan.md`

Write:

```text
workdocs/consulting/{engagement}/modifications/{change}/dbt_edit_plan.md
```

Use this structure:

```markdown
# dbt Edit Plan — {change_title}

## Request
## Classification
## Context Reviewed
## Files To Edit
## Files Not To Touch
## Layer Impact
## Planned SQL Changes
## Planned dbt YAML Changes
## Macro Changes
## dbt_plan.md / er_diagram.md Updates
## Data Dictionary Impact
## Validation Plan
## Risks And Blockers
## Implementation Checklist
```

Be precise about paths, model names, selectors, and validation checks.

## Step 5 — Stop After Planning Unless Confirmed Mode

If `{mode}` is `plan`, stop after writing `dbt_edit_plan.md` and return the plan path to the caller.

Do not edit any dbt repo files, framework artifacts, source YAMLs, or Data Dictionary files in `plan` mode.

If `{mode}` is `implement_confirmed`, continue. This mode may only be used after the caller has already received explicit user confirmation.

## Step 6 — Implement Confirmed Edits

- For broad layer work, invoke the appropriate existing command with the scoped plan:
  - `/write_staging`
  - `/write_intermediate`
  - `/write_mart`
  - `/generate_data_dict`
- For narrow fixes, edit the listed SQL, macro, source YAML, and dbt `.yml` files directly, following the plan.

Always write/update dbt `.yml` files directly when model columns, tests, or descriptions change.

If architecture changes, update `dbt_plan.md`.
If relationships or join paths change, update `er_diagram.md`.
If columns/models exposed to the client change, trigger `/generate_data_dict`.

## Step 7 — Validate

Run the affected dbt selectors from the validation plan.

Use the narrowest selector that verifies the change unless finalization is requested.

Record:
- commands run
- pass/fail status
- important query results
- unresolved blockers

## Step 8 — Update Metadata

Write or update:

```text
workdocs/consulting/{engagement}/modifications/{change}/modification_metadata.json
```

Include:

```json
{
  "dbt_edit_plan": "workdocs/consulting/{engagement}/modifications/{change}/dbt_edit_plan.md",
  "status": "planned|implemented|blocked",
  "files_edited": [],
  "dbt_commands_run": [],
  "data_dictionary_refresh_required": true,
  "dbt_plan_updated": false,
  "er_diagram_updated": false
}
```

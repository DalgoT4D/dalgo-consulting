---
name: investigate
description: Diagnose wrong numbers, duplicates, dashboard discrepancies, freshness issues, and other metric/data quality problems using warehouse data, the KPI Framework, dbt plan, dbt models, and the user prompt.
---

# Investigate

Diagnose a dashboard, KPI, or data-quality issue and produce reproducible findings.

Use this skill from `/investigate`. It should suggest a fix when evidence supports one, or state that the root cause could not be found while preserving useful investigative results.

## Inputs

- `{user_prompt}` — symptom or issue description
- `{engagement}` — optional engagement slug
- `{affected_kpi}` — optional KPI ID/name
- `{affected_dashboard_or_visual}` — optional dashboard/visual ID/name
- `{expected_value}` — optional expected result
- `{time_window}` — optional diagnostic window

## Step 1 — Resolve Context

Invoke `read_phase_context`.

Read:
- KPI Framework
- `dbt_plan.md`
- `er_diagram.md`
- enriched source YAMLs
- relevant dbt SQL and `.yml` files

## Step 2 — Create Investigation Folder

Create:

```text
workdocs/consulting/{engagement}/investigations/{YYYYMMDD_HHMMSS}_{slug}/
```

Store paths:
- `{investigation_dir}`
- `{investigation_md}`
- `{queries_sql}`
- `{investigation_metadata_json}`

## Step 3 — Verify Warehouse Access

Use the same warehouse access pattern as `/explore_data`:

1. Ask the user to confirm any required SSH tunnel is running and capture the local port.
2. Resolve the dbt profile from:
   - `{dbt_repo_path}/profiles.yml`
   - `{dbt_repo_path}/profiles.yaml`
   - `~/.dbt/profiles.yml`
3. Resolve environment variables.
4. Run `dbt debug`.
5. Confirm the active adapter is Postgres-compatible for v1.
6. Build the warehouse connection for investigative SQL.

Credential handling is strict:
- Never print, copy, or summarize raw `profiles.yml` / `profiles.yaml` contents.
- Never print resolved passwords, tokens, private keys, usernames, or environment variable values.
- If reporting connection context, show only the profile name, target name, adapter type, database, schema, and redacted host/port as needed.
- If an error message includes credentials, redact it before showing it to the user or writing artifacts.

If access cannot be verified, stop and write the blocker to `investigation.md`.

## Step 4 — Define The Diagnostic Question

Write the initial diagnostic frame:
- symptom
- affected KPI/dashboard/chart if known
- expected vs actual if known
- filters and time window
- metric grain
- controlling metric definition from the KPI Framework
- relevant mart model(s)

If a missing input materially changes the investigation, ask the user. Otherwise make a reasonable assumption and record it.

## Step 5 — Run Reproducible Checks

Write every SQL query executed to:

```text
workdocs/consulting/{engagement}/investigations/{investigation}/queries.sql
```

Use comments before each query explaining the purpose.

Run checks that fit the issue:
- reproduce the mart metric
- compare numerator and denominator to KPI Framework logic
- check dashboard filters against mart columns
- trace back from `marts_` to intermediate and staging models
- check duplicate keys and join fan-out
- check row counts by layer
- check freshness / latest source timestamps
- check date parsing and window boundaries
- check nulls, placeholder values, and category normalization
- compare source rows to modeled rows

Never write raw PII values into `investigation.md` or `queries.sql` comments. Aggregate or redact where needed.

## Step 6 — Write `investigation.md`

Use this structure:

```markdown
# Investigation — {issue_title}

## Issue
## Context Reviewed
## Diagnostic Question
## Queries Run
## Findings
## Likely Cause
## Suggested Fix
## Confidence
## Could Not Determine
## Follow-Up Checks
## Recommended Next Step
```

If the cause is found, include evidence and recommend whether to route to `/dbt_edit_plan`.

If the cause is not found, say so clearly and include the useful narrowed findings.

## Step 7 — Update Metadata

Write:

```text
workdocs/consulting/{engagement}/investigations/{investigation}/investigation_metadata.json
```

Include:

```json
{
  "status": "cause_found|inconclusive|blocked",
  "investigation": ".../investigation.md",
  "queries": ".../queries.sql",
  "recommended_next_step": "dbt_edit_plan|user_input|no_action",
  "affected_models": [],
  "affected_kpis": []
}
```

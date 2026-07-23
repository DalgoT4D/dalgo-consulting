# /investigate — Diagnose Dashboard Or Data Issues

Diagnoses wrong numbers, duplicates, dashboard mismatches, freshness problems, unexpected nulls, and other metric/data-quality issues.

Use `/investigate` for bugs or discrepancies. If the user is asking to change what should be measured, use `/modify` instead.

Treat the text after `/investigate` as the issue description.

---

## Step 0 — Resolve Issue

If no issue was provided, ask:
> "What dashboard, KPI, or data issue should I investigate?"

Invoke the `investigate` skill with:
- the user issue
- engagement if known
- affected KPI/dashboard/chart if known
- expected value or comparison if provided
- time window if provided

---

## Step 1 — Confirm Warehouse Access

The skill must verify warehouse access using the same pattern as `/explore_data`:
- SSH tunnel readiness prompt
- profile resolution
- environment variable resolution
- `dbt debug`
- Postgres-compatible connection for v1

If access is blocked, write the blocker to the investigation folder and stop.

---

## Step 2 — Preserve Reproducibility

Every query executed during investigation must be written to:

```text
workdocs/consulting/{engagement}/investigations/{investigation}/queries.sql
```

The final findings must be written to:

```text
workdocs/consulting/{engagement}/investigations/{investigation}/investigation.md
```

---

## Step 3 — Present Findings

Return one of:
- likely cause found, with evidence and suggested fix
- multiple plausible causes, ranked by evidence
- inconclusive, with useful narrowed findings and recommended next checks
- blocked, with exact missing access/input

If a dbt fix is recommended, ask:

> "Should I create a dbt edit plan for this fix? (yes / no)"

If yes, call:

```text
/dbt_edit_plan workdocs/consulting/{engagement}/investigations/{investigation}/investigation.md
```

`/dbt_edit_plan` must still ask for explicit confirmation before editing code.

---

## Step 4 — Completion Summary

Print:

```text
✓ investigation:  workdocs/consulting/{engagement}/investigations/{investigation}/investigation.md
✓ queries:        workdocs/consulting/{engagement}/investigations/{investigation}/queries.sql
✓ status:         cause_found/inconclusive/blocked
✓ next step:      dbt_edit_plan/user_input/no_action
```

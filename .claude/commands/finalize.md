# /finalize — Final Verification And PR Readiness

Runs the final dbt verification, linting, documentation, and PR-readiness checks.

Use this after `/generate_data_dict`.

Model and column documentation/tests should already be written directly in dbt YAML files by the Phase 4 commands.

---

## Step 0 — Resolve Context

Invoke the `read_phase_context` skill.

Stop if:
- Phase 4 metadata does not show staging, intermediate, marts, and Data Dictionary completion, unless the user explicitly chooses to proceed.
- required dbt YAML documentation or tests are missing.
- the dbt repo path cannot be resolved.

---

## Step 1 — Check Git State

In the dbt repo and this consulting repo, run:

```bash
git status --short --branch
```

If there are unrelated dirty changes, do not modify or revert them. Ask the user how they want to handle unrelated changes before committing or opening a PR.

---

## Step 2 — Run dbt Validation

Run the broadest safe dbt validation for the project:

```bash
dbt compile --project-dir "{dbt_repo_path}"
dbt build --project-dir "{dbt_repo_path}"
```

If a full `dbt build` is too expensive or unsafe for the client repo, explain why and run the accepted narrower selector from `dbt_plan.md`.

Fix model failures when they are clearly caused by the generated work. Stop with blockers when failures depend on missing data, permissions, warehouse access, or unresolved business decisions.

---

## Step 3 — Run SQLFluff

Run SQLFluff across the full dbt model set, not just files changed in the current task.

Use the repo's existing SQLFluff command if documented. Otherwise try:

```bash
sqlfluff lint models
```

Fix lint violations caused by generated work. If the repo has pre-existing unrelated lint failures, report them separately.

---

## Step 4 — Review dbt YAML Files

Inspect generated and edited dbt YAML files, such as `schema.yml` or folder-level `.yml` files.

Verify:
- every generated model has a clear model description
- important columns have plain-English descriptions
- KPI, dashboard, filter, drilldown, and alert usage is documented where relevant
- PII-sensitive columns are documented without raw values
- descriptions are suitable for generated dbt docs and the Data Dictionary

Update the YAML files directly where needed.

---

## Step 5 — Generate dbt Docs

Run:

```bash
dbt docs generate --project-dir "{dbt_repo_path}"
```

Confirm docs generation succeeds.

---

## Step 6 — Update Metadata

Update:

```text
workdocs/consulting/{engagement}/models/phase4_metadata.json
```

Add:

```json
{
  "finalization": {
    "status": "complete",
    "dbt_compile": "passed",
    "dbt_build": "passed",
    "sqlfluff": "passed",
    "dbt_docs_generate": "passed",
    "notes": []
  }
}
```

Preserve existing keys.

---

## Step 7 — PR Readiness And Delivery

If all checks pass, ask the user whether to create/push a branch and open a GitHub PR.

Do not create, push, or open a PR without explicit user confirmation.

If confirmed:
- create or switch to a dedicated delivery branch
- commit only the intended consulting/dbt changes
- push the branch
- open a PR against `main`

Print:

```text
✓ dbt compile:       passed/blocked
✓ dbt build:         passed/blocked
✓ SQLFluff:          passed/blocked
✓ dbt docs generate: passed/blocked
✓ Data Dictionary:   complete/missing
✓ PR readiness:      ready/blocked/opened
```

If ready, list the files changed and suggest the branch/PR title.

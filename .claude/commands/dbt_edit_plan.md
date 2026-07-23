# /dbt_edit_plan — Plan And Implement Scoped dbt Edits

Creates a scoped dbt edit plan for an existing engagement and implements it only after explicit user confirmation.

This command is directly callable by the user and is also called by `/modify` and recommended by `/investigate`.

Treat the text after `/dbt_edit_plan` as a change request path, investigation path, or direct edit request.

---

## Step 0 — Resolve Inputs

If the argument is a file path, read it fully.

If no argument was provided, ask:
> "What dbt change should I plan?"

Invoke the `dbt_edit_plan` skill in `plan` mode with:
- user prompt or file path
- engagement if known
- dbt repo path if known

---

## Step 1 — Present The Plan

After the skill writes `dbt_edit_plan.md`, summarize:
- files to edit
- files not to touch
- affected layers
- validation commands
- whether `dbt_plan.md` or `er_diagram.md` will be updated
- whether Data Dictionary refresh is required

---

## Step 2 — Code Edit Confirmation Gate

Ask:
> "Confirm that I should implement this dbt edit plan? I will only edit the files listed in the plan. (yes / no)"

If the answer is not clearly yes:
- stop
- do not edit SQL, macros, YAML, framework artifacts, or docs
- leave the plan in the modification folder

---

## Step 3 — Implement Confirmed Edits

If confirmed, invoke the `dbt_edit_plan` skill in `implement_confirmed` mode with the generated `dbt_edit_plan.md`.

Implementation may:
- directly edit narrow SQL/macro/source YAML/dbt `.yml` files listed in the plan
- invoke `/write_staging`, `/write_intermediate`, or `/write_mart` for larger layer edits
- update `dbt_plan.md` if architecture changes
- update `er_diagram.md` if relationships or join paths change
- invoke `/generate_data_dict` when columns or exposed models change

Do not edit files outside the plan without returning to the user for confirmation.

---

## Step 4 — Completion Summary

Print:

```text
✓ dbt edit plan:      {dbt_edit_plan_path}
✓ implementation:     completed/skipped/blocked
✓ files edited:       {files_edited}
✓ validation:         passed/blocked/not run
✓ Data Dictionary:    refreshed/not required/pending
```

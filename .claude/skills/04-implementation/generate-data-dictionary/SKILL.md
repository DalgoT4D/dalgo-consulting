---
name: generate-data-dictionary
description: "Create or update the client-facing Data Dictionary Sheet plus local data_dictionary.md and data_dictionary.json from final dbt models, dbt YAML files, the KPI Framework, and dbt_plan.md."
---

# Generate Data Dictionary

Creates or updates the client-facing Data Dictionary Sheet from final dbt models, `schema.yml`, the KPI Framework, and `dbt_plan.md`.

Use this after `marts_` models have been written, documented, and verified.

---

## Step 0 — Resolve Context

Invoke the `read-phase-context` skill.

Stop if:
- mart models required by `dbt_plan.md` do not exist.
- `schema.yml` documentation is missing for final models.
- `phase4_metadata.json` does not show mart verification, unless the user explicitly chooses to proceed.

---

## Step 1 — Resolve Or Create The Data Dictionary Sheet

Check:

```text
workdocs/consulting/{engagement}/models/phase4_metadata.json
```

If it contains `data_dictionary_sheet.spreadsheet_id`, use that sheet after confirming with the user.

If no existing sheet is available, ask:
> "Should I share the Data Dictionary Sheet with a Google account? If yes, provide the email address; otherwise press Enter."

Then create the sheet:

```bash
python3 scripts/data_dictionary_sheet.py create \
  --title "Data Dictionary - {engagement_display}" \
  --metadata-output "workdocs/consulting/{engagement}/models/phase4_metadata.json"
```

If an email is provided, include `--share-with {email}`.

If sheet creation fails because the service account cannot create files, ask the user to create a blank Google Sheet manually, share it with the service account, and paste the URL. Then continue using that sheet ID.

---

## Step 2 — Build The Local Data Dictionary Draft

Read:
- final `marts_` SQL files
- supporting `stg_` and `int_` SQL files where lineage is needed
- relevant `schema.yml` files
- `kpi_framework.json`
- `dbt_plan.md`

Generate:

```text
workdocs/consulting/{engagement}/models/data_dictionary_draft.json
```

The JSON must have these tabs:

- `Data Dictionary`
- `Model Summary`
- `Open Questions`

### Data Dictionary Rows

One row per documented model column.

Fields:
- `schema`
- `model_name`
- `column_name`
- `data_type`
- `plain_english_description`
- `example_value`
- `source_table`
- `source_column`
- `kpi_ids`
- `dashboards_or_visuals`
- `filter_or_drilldown_usage`
- `pii`
- `notes`

Do not include raw PII example values. Leave `example_value` blank for PII fields.

### Model Summary Rows

One row per generated model.

Fields:
- `schema`
- `model_name`
- `model_type` — `staging`, `intermediate`, or `marts`
- `grain`
- `purpose`
- `upstream_models`
- `kpis_supported`
- `dashboards_or_visuals_supported`
- `refresh_or_cadence_notes`
- `validation_notes`

### Open Questions Rows

Include any documentation gaps or unresolved model semantics.

---

## Step 3 — Write The Data Dictionary Sheet

Run:

```bash
python3 scripts/data_dictionary_sheet.py write \
  --sheet-id {spreadsheet_id} \
  --input-json "workdocs/consulting/{engagement}/models/data_dictionary_draft.json"
```

Then read it back into local files:

```bash
python3 scripts/data_dictionary_sheet.py read \
  --sheet-id {spreadsheet_id} \
  --format markdown \
  --output "workdocs/consulting/{engagement}/models/data_dictionary.md"
```

```bash
python3 scripts/data_dictionary_sheet.py read \
  --sheet-id {spreadsheet_id} \
  --format json \
  --output "workdocs/consulting/{engagement}/models/data_dictionary.json"
```

---

## Step 4 — Update Metadata

Update:

```text
workdocs/consulting/{engagement}/models/phase4_metadata.json
```

Add:

```json
{
  "data_dictionary": {
    "status": "complete",
    "local_markdown": "workdocs/consulting/{engagement}/models/data_dictionary.md",
    "local_json": "workdocs/consulting/{engagement}/models/data_dictionary.json"
  }
}
```

Preserve existing keys.

---

## Step 5 — Completion Summary

Print:

```text
✓ Data Dictionary Sheet: {data_dictionary_sheet_url}
✓ local markdown:        workdocs/consulting/{engagement}/models/data_dictionary.md
✓ local JSON:            workdocs/consulting/{engagement}/models/data_dictionary.json
✓ open questions:        {open_question_count}
```

Then print:
> "Next → run the `finalize-dbt-project` skill after reviewing the Data Dictionary."

---
name: read_kpi_framework
description: Read all tabs from a Dalgo KPI Framework Sheet and save normalized local Markdown and JSON artifacts for downstream Phase 3 and Phase 4 commands.
---

# Read KPI Framework Sheet

Read the KPI Framework Sheet and normalize it into local artifacts.

Use this skill whenever a command needs the KPI Framework after `/build_kpi_sheet`, including `/dbt_plan`, `/generate_er_diagram`, and model-development commands.

## Inputs

- `{spreadsheet_id}` — Google Sheet ID for the KPI Framework Sheet
- `{engagement}` — folder slug, such as `give_do`
- `{key_file}` — optional path to the Google service account key; default `secrets/my_service_key.json`

## Step 1 — Validate The Sheet ID

If `{spreadsheet_id}` was not passed by the caller:

1. Look for `workdocs/consulting/{engagement}/framework/phase3_metadata.json`.
2. Read `kpi_framework_sheet.spreadsheet_id`.
3. If the metadata file is missing or the sheet ID is blank, ask the user:
   > "What is the Google Sheet ID or URL for the KPI Framework Sheet?"

If the user provides a URL, extract the ID from:
`https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/...`

Store the final value as `{spreadsheet_id}`.

## Step 2 — Read The Sheet

Run:

```bash
python3 scripts/kpi_framework_sheet.py read \
  --sheet-id {spreadsheet_id} \
  --format markdown \
  --output workdocs/consulting/{engagement}/framework/kpi_framework.md
```

Then run:

```bash
python3 scripts/kpi_framework_sheet.py read \
  --sheet-id {spreadsheet_id} \
  --format json \
  --output workdocs/consulting/{engagement}/framework/kpi_framework.json
```

If the command fails with a Google API permission error, stop and tell the user to share the KPI Framework Sheet with the service account in `secrets/my_service_key.json`.

## Step 3 — Validate Required Tabs

Read the generated `kpi_framework.json` and verify it contains these tabs:

- `KPI Catalog`
- `Dashboard Outputs`
- `Charts & Visuals`
- `Filters & Drilldowns`
- `Alerts`
- `Open Questions`

Warn, but do not fail, if a tab has no rows. Empty `Alerts` or `Open Questions` tabs are acceptable. Empty KPI, dashboard, or visual tabs should be called out because they may block `/dbt_plan`.

## Step 4 — Update Metadata

Create or update `workdocs/consulting/{engagement}/framework/phase3_metadata.json` with:

```json
{
  "kpi_framework_sheet": {
    "spreadsheet_id": "{spreadsheet_id}",
    "url": "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
  },
  "local_artifacts": {
    "kpi_framework_markdown": "workdocs/consulting/{engagement}/framework/kpi_framework.md",
    "kpi_framework_json": "workdocs/consulting/{engagement}/framework/kpi_framework.json"
  }
}
```

Preserve any existing metadata keys not owned by this skill.

## Step 5 — Confirm

Confirm:

```text
✓ KPI Framework Sheet: {sheet_url}
✓ Markdown: workdocs/consulting/{engagement}/framework/kpi_framework.md
✓ JSON:     workdocs/consulting/{engagement}/framework/kpi_framework.json
```

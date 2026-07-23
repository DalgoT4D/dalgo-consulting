---
name: apply-kpi-framework-patch
description: "Apply a confirmed KPI Framework patch for a Dalgo modification, preserving all untouched tabs/rows and refreshing local KPI Framework Markdown and JSON artifacts."
---

# Apply KPI Framework Patch

Use this skill only after `modify-requirements` has drafted `kpi_framework_patch.json` and the user has explicitly confirmed that the KPI Framework changes should be applied.

## Inputs

- `{engagement}` — engagement slug
- `{patch_path}` — path to `kpi_framework_patch.json`
- `{kpi_framework_json_path}` — usually `workdocs/consulting/{engagement}/framework/kpi_framework.json`
- `{spreadsheet_id}` — KPI Framework Sheet ID when Google Sheets is available
- `{change_request_id}` — stable modification ID

## Rules

- Do not apply unconfirmed patches.
- Do not drop existing rows or tabs not mentioned by the patch.
- Every non-empty row status must be one of:
  - `active`
  - `revised`
  - `deprecated`
  - `needs_client_input`
- Preserve `change_request_id`, `change_reason`, and `changed_at` on changed rows.
- If Google Sheets is unavailable or the service account cannot write, update local artifacts and record the blocker in modification metadata.

## Steps

1. Read the current `kpi_framework.json`.
2. Read `kpi_framework_patch.json`.
3. Apply row additions, revisions, and deprecations by stable IDs.
4. Validate required tabs:
   - `KPI Catalog`
   - `Dashboard Outputs`
   - `Charts & Visuals`
   - `Filters & Drilldowns`
   - `Alerts`
   - `Open Questions`
5. Validate status values.
6. Write the updated local `kpi_framework.json`.
7. If `{spreadsheet_id}` is available, run:

```bash
python3 scripts/kpi_framework_sheet.py write --sheet-id "{spreadsheet_id}" --input-json "{kpi_framework_json_path}"
```

8. Invoke `read-kpi-framework` to refresh local Markdown and JSON from the sheet when the sheet write succeeds.
9. Update modification metadata with applied/skipped/blocked status.

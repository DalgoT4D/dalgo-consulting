---
name: build-kpi-framework
description: "Run Phase 3 KPI Framework creation or update: transform me_goals.md and enriched source YAMLs into the multi-tab Dalgo KPI Framework contract, write Google Sheet/local artifacts, and validate status fields."
---

# Build Kpi Framework

Creates or updates the multi-tab KPI Framework Sheet for Phase 3.
Use this after the `explore-data` skill, once `me_goals.md` exists and the relevant `source.yml` / `sources.yml` files have been enriched.

The KPI Framework is the analytics contract for Dalgo outputs. It must organize the client requirements from `me_goals.md` into the metrics, dashboards, charts, filters, drilldowns, and alerts needed to plan dbt models.

Treat the skill input as optional source YAML paths. Run through each step in order.

---

## Step 0 — Resolve Inputs

If the caller provided one or more paths, treat them as `{sources_paths}`.

If no paths were provided:
- Try to infer relevant enriched source YAMLs from the engagement folder or dbt repo.
- If there are multiple plausible files, ask:
  > "What are the paths to the enriched `source.yml` / `sources.yml` files for this engagement?"

For every source YAML:
- Verify the file exists.
- Verify it parses as YAML.
- Verify it contains a root `sources` collection.
- Verify at least one table has generated enrichment fields such as `row_count`, `candidate_join_keys`, `date_columns`, or column-level `null_rate`.

If the files do not appear enriched by the `explore-data` skill, warn the user and ask whether to continue. The KPI Framework should usually be built only after exploration.

Store:
- `{sources_paths}`
- `{sources_yamls}`

---

## Step 1 — Resolve Engagement And `me_goals.md`

Prefer automatic resolution:

1. If all `{sources_paths}` are under `workdocs/consulting/{engagement}/...`, derive `{engagement}` from the path.
2. Otherwise, if all `{sources_paths}` are inside the same dbt repo, search `workdocs/consulting/*/discovery/me_goals.md` for a footer line containing that dbt repo path.
3. If neither yields exactly one engagement, ask:
   > "What is the path to the relevant `me_goals.md` file?"

Validate:
- `{me_goals_path}` exists.
- Read the file fully.

Create the framework folder if needed:

```text
workdocs/consulting/{engagement}/framework/
```

Store:
- `{engagement}`
- `{engagement_display}` — use the display name from `me_goals.md` if present; otherwise derive it from `{engagement}`
- `{me_goals_path}`
- `{me_goals_contents}`
- `{framework_dir}`

---

## Step 2 — Resolve Or Create The KPI Framework Sheet

Check for:

```text
workdocs/consulting/{engagement}/framework/phase3_metadata.json
```

If it contains `kpi_framework_sheet.spreadsheet_id`, ask:
> "A KPI Framework Sheet already exists for this engagement. Update it? (yes / no)"

If yes, store the existing `{spreadsheet_id}`.

If no existing sheet is available, create one:

Ask:
> "Should I share the KPI Framework Sheet with a Google account? If yes, provide the email address; otherwise press Enter."

If an email is provided, include `--share-with {email}`.

```bash
python3 scripts/kpi_framework_sheet.py create \
  --title "KPI Framework - {engagement_display}" \
  --metadata-output "workdocs/consulting/{engagement}/framework/phase3_metadata.json"
```

If sheet creation fails because the service account cannot create files, ask the user to create a blank Google Sheet manually, share it with the service account, and paste the URL. Then continue using that sheet ID.

Store:
- `{spreadsheet_id}`
- `{kpi_framework_sheet_url}`

---

## Step 3 — Draft The KPI Framework Rows

Use `me_goals.md` as the source of client intent and the enriched source YAMLs as the source of data reality.

Generate a complete local JSON draft at:

```text
workdocs/consulting/{engagement}/framework/kpi_framework_draft.json
```

The JSON must have exactly these top-level keys:

- `KPI Catalog`
- `Dashboard Outputs`
- `Charts & Visuals`
- `Filters & Drilldowns`
- `Alerts`
- `Open Questions`

Do not write a pointer-only or metadata-only draft. Even when Google Sheets is unavailable and a local fallback is used, `kpi_framework_draft.json` and `kpi_framework.json` must use the full tab-shaped object above.

Every non-empty row in every tab must use one of these status values only:
- `active`
- `revised`
- `deprecated`
- `needs_client_input`

Do not use `open`, `closed`, `draft`, `planned`, or any other value in KPI Framework `status` fields.

### KPI Catalog

One row per KPI or metric.

Required fields:
- `kpi_id` — stable ID such as `kpi_001`
- `kpi_name`
- `program`
- `outcome_area`
- `requirements_alignment` — row number, metric name, or quote from `me_goals.md`
- `plain_english_definition`
- `calculation_logic`
- `numerator_logic`
- `denominator_logic`
- `source_tables`
- `required_columns`
- `filters_conditions`
- `grain`
- `time_grain`
- `breakdown_dimensions`
- `mart_model`
- `status` — `active`, `revised`, `deprecated`, or `needs_client_input`
- `change_request_id`
- `change_reason`
- `changed_at`
- `open_questions`

### Dashboard Outputs

One row per dashboard, page, or major dashboard section needed in Dalgo.

Required fields:
- `dashboard_id`
- `dashboard_name`
- `program`
- `audience`
- `decision_supported`
- `cadence`
- `primary_kpis`
- `required_filters`
- `required_drilldowns`
- `status` — `active`, `revised`, `deprecated`, or `needs_client_input`
- `change_request_id`
- `change_reason`
- `changed_at`
- `notes`

### Charts & Visuals

One row per metric card, chart, table, map, or operational view.

Required fields:
- `visual_id`
- `dashboard_id`
- `visual_title`
- `visual_type` — e.g. `scorecard`, `line_chart`, `bar_chart`, `stacked_bar`, `table`, `map`, `alert_list`
- `kpi_ids`
- `program`
- `x_axis_or_grouping`
- `y_metric`
- `series_or_color_dimension`
- `required_dimensions`
- `sort_logic`
- `default_time_window`
- `grain_needed`
- `mart_model`
- `status` — `active`, `revised`, `deprecated`, or `needs_client_input`
- `change_request_id`
- `change_reason`
- `changed_at`
- `notes`

Do not derive chart type only from the KPI. A KPI can appear in multiple visual forms. Choose visual types from the user need in `me_goals.md`, the reporting audience, and the breakdown dimensions.

### Filters & Drilldowns

One row per reusable dashboard filter or drilldown path.

Required fields:
- `filter_or_drilldown_id`
- `label`
- `type` — `filter` or `drilldown`
- `applies_to_dashboards`
- `applies_to_visuals`
- `source_column`
- `canonical_dimension_model`
- `allowed_values_logic`
- `default_value`
- `required_for_all_charts`
- `status` — `active`, `revised`, `deprecated`, or `needs_client_input`
- `change_request_id`
- `change_reason`
- `changed_at`
- `notes`

Use this tab to make cross-chart filter compatibility explicit. Shared filters usually imply shared dimension columns in mart models.

### Alerts

One row per alert or threshold requirement. Leave empty if no alert requirement exists.

Required fields:
- `alert_id`
- `kpi_id`
- `program`
- `alert_condition`
- `threshold`
- `comparison_period`
- `recipient_or_audience`
- `cadence`
- `required_grain`
- `mart_model`
- `status` — `active`, `revised`, `deprecated`, or `needs_client_input`
- `change_request_id`
- `change_reason`
- `changed_at`
- `notes`

### Open Questions

One row per ambiguity that affects implementation.

Required fields:
- `question_id`
- `related_kpi_or_visual`
- `question`
- `why_it_matters`
- `suggested_default`
- `owner`
- `status`

Use `active` for current rows, `revised` for rows changed by a modification, `deprecated` for rows intentionally retired, and `needs_client_input` where the calculation, grain, filters, charting requirement, or source mapping cannot be safely inferred.

---

## Step 4 — PII And Safety Checks

Before writing the sheet:
- Do not include raw PII sample values in any tab.
- Do not expose person names, phone numbers, emails, exact addresses, or person-level IDs from source samples.
- It is acceptable to reference PII-like columns by column name when needed for joins or deduplication, but mark that usage carefully in notes.
- Prefer plain English in client-facing definitions.
- Put unresolved ambiguity in `Open Questions`; do not silently invent confirmed business logic.

---

## Step 5 — Write The Google Sheet

Run:

```bash
python3 scripts/kpi_framework_sheet.py write \
  --sheet-id {spreadsheet_id} \
  --input-json "workdocs/consulting/{engagement}/framework/kpi_framework_draft.json"
```

If write fails with a permission error, stop and tell the user to share the sheet with the service account in `secrets/my_service_key.json`.

---

## Step 6 — Normalize Local Copies

Invoke the `read-kpi-framework` skill with:

- `{spreadsheet_id}`
- `{engagement}`

This produces:

```text
workdocs/consulting/{engagement}/framework/kpi_framework.md
workdocs/consulting/{engagement}/framework/kpi_framework.json
```

Update `workdocs/consulting/{engagement}/framework/phase3_metadata.json` with:

```json
{
  "source_yaml_files": ["..."],
  "local_artifacts": {
    "kpi_framework_markdown": "workdocs/consulting/{engagement}/framework/kpi_framework.md",
    "kpi_framework_json": "workdocs/consulting/{engagement}/framework/kpi_framework.json"
  }
}
```

Preserve existing keys.

---

## Step 7 — Completion Summary

Print:

```text
✓ me_goals.md:            {me_goals_path}
✓ source YAML files:      {sources_paths}
✓ KPI Framework Sheet:    {kpi_framework_sheet_url}
✓ local markdown:         workdocs/consulting/{engagement}/framework/kpi_framework.md
✓ local JSON:             workdocs/consulting/{engagement}/framework/kpi_framework.json
✓ open questions:         {open_question_count}
```

Then print:
> "Review the KPI Framework Sheet with the consultant/client. Once accepted, run the `plan-dbt-architecture` skill."

---
name: read_phase_context
description: Resolve and read the accepted Dalgo consulting context for Phase 4 commands, including me_goals.md, KPI Framework, dbt_plan.md, er_diagram.md, source YAMLs, dbt repo path, and metadata.
---

# Read Phase Context

Resolve and read the engagement context needed by Phase 4 commands.

Use this skill at the start of `/modify`, `/dbt_edit_plan`, `/investigate`, `/write_staging`, `/write_intermediate`, `/write_mart`, `/generate_data_dict`, and `/finalize`.

## Inputs

- `{engagement}` — optional folder slug
- `{sources_paths}` — optional source YAML paths
- `{dbt_repo_path}` — optional dbt repo path

## Step 1 — Resolve Engagement

Resolve `{engagement}` in this order:

1. If the caller passed `{engagement}`, use it.
2. If the current path is inside `workdocs/consulting/{engagement}/...`, derive it from the path.
3. If source YAML paths are provided and all are inside one `workdocs/consulting/{engagement}/...`, derive it from those paths.
4. If exactly one `workdocs/consulting/*/framework/phase3_metadata.json` exists, ask the user to confirm that engagement.
5. Otherwise ask:
   > "Which engagement should this command use?"

Store `{engagement}`.

## Step 2 — Read Metadata

Read, if present:

```text
workdocs/consulting/{engagement}/framework/phase3_metadata.json
workdocs/consulting/{engagement}/models/phase4_metadata.json
```

Preserve the parsed metadata for the caller.

Also list, if present:

```text
workdocs/consulting/{engagement}/modifications/
workdocs/consulting/{engagement}/investigations/
```

## Step 3 — Resolve And Read Required Artifacts

Validate and read fully:

- `workdocs/consulting/{engagement}/discovery/me_goals.md`
- `workdocs/consulting/{engagement}/framework/kpi_framework.md`
- `workdocs/consulting/{engagement}/framework/kpi_framework.json`
- `workdocs/consulting/{engagement}/framework/dbt_plan.md`
- `workdocs/consulting/{engagement}/framework/er_diagram.md`

If the KPI Framework Sheet ID is available in metadata, invoke `read_kpi_framework` first to refresh the local Markdown and JSON copies.

If `dbt_plan.md` or `er_diagram.md` is missing, stop and tell the user to finish Phase 3 before model development.

## Step 4 — Resolve Source YAMLs

Resolve `{sources_paths}` in this order:

1. Caller-provided paths.
2. `source_yaml_files` from Phase 3 metadata.
3. YAML files under `workdocs/consulting/{engagement}/data_exploration/`.
4. Ask the user:
   > "What are the enriched source YAML files for this engagement?"

Validate every file exists and contains a root `sources` collection.
Warn if no generated enrichment fields are present.

## Step 5 — Resolve dbt Repo

Resolve `{dbt_repo_path}` in this order:

1. Caller-provided path.
2. Footer line in `me_goals.md`: `dbt repo: ...`
3. `dbt_repo_path` from metadata if present.
4. Ask the user:
   > "What is the local path to the dbt repo for this engagement?"

Validate:
- the path exists
- `{dbt_repo_path}/dbt_project.yml` exists

Read:
- `dbt_project.yml`
- existing model directories
- existing dbt YAML files under the model paths, such as `schema.yml` or folder-level `.yml` files
- existing macros if a `macros/` directory exists

## Step 6 — Return Context To Caller

Make these values available to the calling command:

- `{engagement}`
- `{me_goals_path}`
- `{me_goals_contents}`
- `{kpi_framework_markdown_path}`
- `{kpi_framework_json_path}`
- `{kpi_framework_json}`
- `{dbt_plan_path}`
- `{dbt_plan_contents}`
- `{er_diagram_path}`
- `{er_diagram_contents}`
- `{sources_paths}`
- `{sources_yamls}`
- `{dbt_repo_path}`
- `{dbt_project_contents}`
- `{phase3_metadata}`
- `{phase4_metadata}`
- `{modifications_dir}`
- `{investigations_dir}`

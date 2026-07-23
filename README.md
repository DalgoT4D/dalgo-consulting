# dalgo-consulting

AI-assisted consulting workflow for building dbt data models that transform raw NGO program data into M&E metrics and Dalgo dashboards. Each engagement moves through four phases: **Discovery -> Data Exploration -> Framework -> Model Development**.

The repo is skills-first. `dbt-wizard` is the consultant execution surface, and all workflow logic lives in `.claude/skills/**/SKILL.md`. Slash commands are no longer part of the workflow.

## Repo Structure

```
dalgo-consulting/
├── .claude/
│   ├── agents/                       # Specialized AI agents
│   └── skills/
│       ├── 00-router/                # User-facing workflow router
│       ├── 01-discovery/             # Requirements Sheet -> me_goals.md
│       ├── 02-exploration/           # Warehouse/profile checks and source YAML enrichment
│       ├── 03-framework/             # KPI Framework, dbt plan, ER diagram
│       ├── 04-implementation/        # dbt SQL/YAML and Data Dictionary
│       ├── 05-change-management/     # Modify, investigate, and edit live projects
│       └── 06-delivery/              # Validation, GitHub delivery, handoff
├── docs/
│   ├── process.md
│   └── artifact-design-plan.md
├── scripts/
│   ├── read_requirements.py
│   ├── kpi_framework_sheet.py
│   └── data_dictionary_sheet.py
├── secrets/
│   └── my_service_key.json           # Google service account key (gitignored)
└── workdocs/
    └── consulting/
        └── {engagement}/
            ├── discovery/
            │   └── me_goals.md
            ├── data_exploration/
            │   └── sources.yml       # Optional local copy; dbt repo YAMLs may be edited directly
            ├── framework/
            │   ├── kpi_framework.md
            │   ├── kpi_framework.json
            │   ├── dbt_plan.md
            │   ├── er_diagram.md
            │   └── phase3_metadata.json
            ├── models/               # Or inside the client's dbt repo
            │   ├── data_dictionary.md
            │   ├── data_dictionary.json
            │   ├── phase4_metadata.json
            │   ├── staging/
            │   ├── intermediate/
            │   └── marts/
            ├── modifications/
            │   └── {change}/
            │       ├── change_request.md
            │       ├── kpi_framework_patch.json
            │       ├── dbt_edit_plan.md
            │       └── modification_metadata.json
            └── investigations/
                └── {issue}/
                    ├── investigation.md
                    ├── queries.sql
                    └── investigation_metadata.json
```

Google Sheets are linked from local metadata and are not committed:

| Sheet | Purpose |
|---|---|
| Requirements Sheet | Four-tab client/consultant workbook: Instructions, Engagement Context, Data Sources, Metrics. |
| KPI Framework Sheet | Multi-tab analytics contract for metrics, dashboards, charts, filters, drilldowns, alerts, grains, and model mappings. |
| Data Dictionary Sheet | Client-facing handoff workbook generated after dbt models are complete. |

## Skills-First Execution

Consultants should start with `dalgo-consulting-workflow` unless they know the exact skill they need. The router decides whether the request is a new engagement, a phase rerun, a requirement modification, a bug investigation, or a delivery task, then calls the appropriate skills in order.

Skill names stay stable even though the files are organized into subfolders. `dbt-wizard` discovers skills recursively from `.claude/skills/**/SKILL.md`.

### Skill Folders

| Folder | Skills | Responsibility |
|---|---|---|
| `.claude/skills/00-router/` | `dalgo-consulting-workflow` | Master workflow navigation and phase routing. |
| `.claude/skills/01-discovery/` | `discover-engagement`, `read-requirements` | Create engagement folders and turn the Requirements Sheet into `me_goals.md`. |
| `.claude/skills/02-exploration/` | `explore-data`, `validate-warehouse-access` | Validate dbt profiles/tunnels and enrich source YAMLs with warehouse-backed profiling. |
| `.claude/skills/03-framework/` | `build-kpi-framework`, `read-kpi-framework`, `plan-dbt-architecture`, `generate-er-diagram` | Convert goals and explored sources into KPI Framework, dbt plan, and ER diagram. |
| `.claude/skills/04-implementation/` | `read-phase-context`, `write-dbt-staging`, `write-dbt-intermediate`, `write-dbt-marts`, `generate-data-dictionary` | Write dbt SQL/YAML layer by layer and produce the Data Dictionary. |
| `.claude/skills/05-change-management/` | `modify-requirements`, `apply-kpi-framework-patch`, `investigate-issue`, `dbt-edit-plan` | Handle live requirement changes, dashboard bugs, reproducible investigations, and scoped dbt edits. |
| `.claude/skills/06-delivery/` | `finalize-dbt-project`, `github-delivery` | Run final dbt validation, lint/docs checks, and confirmed GitHub delivery. |

### Skill Catalog

| Skill | Use When | Inputs | Writes | Gates |
|---|---|---|---|---|
| `dalgo-consulting-workflow` | User asks to run the whole flow, continue a phase, modify requirements, investigate an issue, or finalize delivery. | User prompt, engagement name/path, dbt repo path, optional sheet URLs. | Routes to downstream skills; does not replace their artifacts. | Uses downstream confirmation gates. |
| `discover-engagement` | Starting Phase 1 for a new engagement. | Requirements Sheet URL, dbt repo path, engagement name. | Engagement folder structure, metadata, `me_goals.md` through `read-requirements`. | Ask before proceeding if required inputs are missing. |
| `read-requirements` | Reading or refreshing the Requirements Sheet. | Google Sheet URL/ID, service account key. | `workdocs/consulting/{engagement}/discovery/me_goals.md`. | Falls back only when sheet access is unavailable and clearly labels the fallback. |
| `validate-warehouse-access` | Any skill needs warehouse access. | dbt repo path, profiles context, tunnel port if needed. | Connectivity notes for the caller. | Asks `Can I read your database schema tables?` before warehouse reads; never prints credentials or resolved secret values. |
| `explore-data` | Running Phase 2 or enriching new sources during a modification. | `me_goals.md`, one or more source YAMLs, dbt profile/tunnel details. | Updates the same source YAMLs in place with profiling metadata, PII flags, table notes, and column notes. | Asks `Can I read your database schema tables?` and prompts for tunnel/profile readiness before querying. |
| `build-kpi-framework` | Running Phase 3 after source exploration. | `me_goals.md`, enriched source YAMLs. | KPI Framework Sheet plus `kpi_framework.md` and `kpi_framework.json`. | Mark unresolved rows as `needs_client_input`. |
| `read-kpi-framework` | Refreshing local copies of the KPI Framework Sheet. | KPI Framework Sheet URL/ID. | `kpi_framework.md`, `kpi_framework.json`. | Preserve row status values: `active`, `revised`, `deprecated`, `needs_client_input`. |
| `plan-dbt-architecture` | Designing dbt models from the KPI Framework. | `me_goals.md`, KPI Framework, enriched source YAMLs. | `framework/dbt_plan.md`. | Use chart-ready `marts_` outputs, not forced fact/dimension naming. |
| `generate-er-diagram` | Documenting model/entity relationships after the dbt plan. | `me_goals.md`, KPI Framework, `dbt_plan.md`, enriched source YAMLs. | `framework/er_diagram.md`. | Mermaid ER blocks must use valid attribute syntax and no free-text notes inside entity blocks. |
| `read-phase-context` | Any Phase 4 skill needs accepted upstream artifacts. | Engagement path, dbt repo path, source YAML hints. | Context summary for the caller. | Stop if required upstream artifacts are missing or stale. |
| `write-dbt-staging` | Implementing Phase 4 staging. | `dbt_plan.md`, enriched sources. | `stg_*.sql` and dbt `.yml` files. | Run and verify staging before moving on. |
| `write-dbt-intermediate` | Implementing Phase 4 intermediate models. | KPI Framework, `dbt_plan.md`, ER diagram, staging models. | `int_*.sql` and dbt `.yml` files. | Validate join cardinality and fan-out. |
| `write-dbt-marts` | Implementing Phase 4 reporting models. | KPI Framework, `dbt_plan.md`, intermediate models. | Chart-ready `marts_*.sql` and dbt `.yml` files. | Validate KPI values against framework definitions. |
| `generate-data-dictionary` | Handoff or when model/column exposure changes. | Final dbt models/YAML, KPI Framework. | Data Dictionary Sheet, `data_dictionary.md`, `data_dictionary.json`. | No raw PII examples in client-facing outputs. |
| `finalize-dbt-project` | Before delivery for new work or modifications. | Full dbt model set. | Final validation notes, docs/lint status, optional delivery handoff. | Must run before delivery. |
| `modify-requirements` | Existing engagement has a requirement change: KPI, dashboard, chart, filter, drilldown, or alert. | User change request, existing KPI Framework, dbt repo context. | Durable modification folder; optional `kpi_framework_patch.json`; invokes `dbt-edit-plan` when dbt changes are needed. | Do not edit KPI Framework until user confirms the proposed patch. |
| `apply-kpi-framework-patch` | A KPI Framework patch was confirmed. | `kpi_framework_patch.json`, existing KPI Framework Sheet/artifacts. | Updated sheet rows and refreshed local framework artifacts. | Only runs after confirmation from `modify-requirements`. |
| `investigate-issue` | Dashboard/model bug: wrong numbers, duplicates, freshness, missing rows, or discrepancy. | User issue, warehouse access, KPI Framework, dbt plan, current models. | `investigation.md`, `queries.sql`, investigation metadata; may recommend `dbt-edit-plan`. | Asks `Can I read your database schema tables?`, writes every SQL query it runs, and does not edit code directly. |
| `dbt-edit-plan` | Direct dbt model edit request or a fix from modify/investigate. | Change request or investigation, repo context, relevant artifacts. | `dbt_edit_plan.md`, confirmed SQL/YAML edits, `dbt_plan.md` updates when architecture changes, Data Dictionary refresh if columns/models change. | Do not edit dbt code/YAML until user confirms the plan. |
| `github-delivery` | User wants changes pushed or a PR opened. | Repo path, intended files, branch target. | Commit, push, optional PR. | Ask before commit/push/PR and summarize exact files. |

## Core Workflows

### New Engagement

```
Run the Dalgo consulting workflow for a new engagement.
Use the Requirements Sheet: <sheet-url>
Use the dbt repo: <path-or-github-url>
Run Phase 1 through Phase 4.
```

Execution order:

1. `dalgo-consulting-workflow`
2. `discover-engagement` -> `read-requirements`
3. `explore-data` -> `validate-warehouse-access`
4. `build-kpi-framework` -> `read-kpi-framework` -> `plan-dbt-architecture` -> `generate-er-diagram`
5. `read-phase-context` -> `write-dbt-staging` -> `write-dbt-intermediate` -> `write-dbt-marts` -> `generate-data-dictionary`
6. `finalize-dbt-project`
7. `github-delivery`, when the user asks to push or open a PR

### Requirement Change

Use this path when the client changes what they want to measure or show in Dalgo.

```
Modify requirements: add district drilldown to the attendance dashboard for <engagement>.
```

Execution order:

1. `modify-requirements`
2. Optional `apply-kpi-framework-patch` after user confirmation
3. `dbt-edit-plan`
4. Affected implementation skills only
5. `generate-data-dictionary` if exposed models or columns change
6. `finalize-dbt-project`
7. Optional `github-delivery`

### Bug Or Discrepancy

Use this path when the existing dashboard/model looks wrong.

```
Investigate issue: attendance rate is too high for June in the district dashboard.
```

Execution order:

1. `investigate-issue`
2. `dbt-edit-plan` only if a likely fix is identified and the user wants implementation
3. Affected implementation skills only
4. `generate-data-dictionary` if exposed models or columns change
5. `finalize-dbt-project`
6. Optional `github-delivery`

## Key Principles

- Requirements Sheet drives scope. It captures client intent in program language.
- `me_goals.md` is shared context for every downstream skill.
- KPI Framework is the analytics contract. It captures metrics, dashboards, charts, filters, drilldowns, alerts, grains, source mappings, and open questions.
- Chart requirements belong in the KPI Framework. Chart type is visual-level metadata, because one KPI may appear in multiple output forms.
- Marts are chart-ready, not forced into facts/dimensions. Final models use the `marts_` prefix and are shaped around Dalgo output requirements.
- Requirement changes and bugs use different paths: `modify-requirements` for analytics contract changes, `investigate-issue` for wrong numbers, duplicates, freshness, and dashboard discrepancies.
- No unconfirmed edits: `modify-requirements` asks before KPI Framework edits, `dbt-edit-plan` asks before dbt code/YAML edits, and `github-delivery` asks before commit/push/PR.
- No warehouse reads without consent. Any skill that needs to inspect warehouse schemas/tables, verify physical tables, profile source data, run investigative SQL, or run dbt commands that query the warehouse must first ask: `Can I read your database schema tables?`
- Modification work is auditable. Every change or investigation gets a durable folder with the request, plan, SQL run, and metadata.
- Warehouse access is validated before query-backed skills run, including tunnel/profile checks when needed.
- Data Dictionary updates are triggered when exposed models or columns change.
- PII must not be exposed in artifacts. PII columns may be flagged and profiled structurally, but raw sensitive values must not be stored.
- Finalization is mandatory before every delivery.
- Delivery is PR-based for client dbt repos.

## Demo Artifacts

The `workdocs/consulting/demoaccount_test/` folder contains a generated end-to-end demo from the sample Requirements Sheet and `DalgoT4D/dbt_demoaccount`. Use it to show the manager-facing flow: start with the Requirements Sheet, produce `me_goals.md`, enrich sources, build the KPI Framework, create `dbt_plan.md` and `er_diagram.md`, generate dbt models/YAML, and finish with a Data Dictionary plus validation notes.

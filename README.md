# dalgo-consulting

AI-assisted consulting workflow for building dbt data models that transform raw NGO program data into M&E metrics and dashboards. Each engagement moves through four phases: **Discovery → Data Exploration → Framework → Model Development**.

## Repo Structure

```
dalgo-consulting/
├── .claude/
│   ├── agents/              # Specialized AI agents (auto-invoked by context)
│   └── skills/              # Canonical dbt-wizard workflows and reusable helpers
├── docs/
│   ├── process.md
│   └── artifact-design-plan.md
├── scripts/
│   ├── read_requirements.py
│   ├── kpi_framework_sheet.py
│   └── data_dictionary_sheet.py
├── secrets/
│   └── my_service_key.json  # Google service account key (gitignored)
└── workdocs/
    └── consulting/
        └── {engagement}/
            ├── discovery/
            │   └── me_goals.md         # Shared context for ALL downstream phases
            ├── data_exploration/
            │   └── sources.yml         # Optional working copy; explore-data can also target dbt repo source YAMLs directly
            ├── framework/
            │   ├── kpi_framework.md    # Local normalized copy of KPI Framework Sheet
            │   ├── kpi_framework.json  # Machine-readable contract for downstream skills
            │   ├── dbt_plan.md         # dbt architecture plan for Dalgo outputs
            │   ├── er_diagram.md       # Entity-relationship diagram
            │   └── phase3_metadata.json
            ├── models/                 # Or inside the client's dbt repo
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

Google Sheets (linked from workdocs, not stored as files):
├── Requirements Sheet      ← 4-tab workbook: Instructions / Engagement Context / Data Sources / Metrics
├── KPI Framework Sheet     ← multi-tab analytics contract for Dalgo outputs
└── Data Dictionary Sheet   ← generated at engagement close
```

## Execution Surface

dbt-wizard is the primary consultant interface. It reads `.claude/skills/`, so skills are the canonical source of workflow logic.

| Type | Location | Purpose | How to Use |
|------|----------|---------|------------|
| **Skills** | `.claude/skills/` | Canonical workflows and reusable helpers for dbt-wizard | Ask dbt-wizard to run a phase or invoke a skill by name |
| **Agents** | `.claude/agents/` | Specialized personas invoked by context | Claude picks the right agent automatically |

---

## Consulting Workflow

### New Engagement

Full four-phase process for a new client or program.

```
Phase 1: Discovery
  discover-engagement     ← collects engagement details, creates folders,
                             reads Requirements Sheet -> generates me_goals.md

Phase 2: Data Exploration
  explore-data            ← reads me_goals.md + one or more passed source.yml/sources.yml files;
                             prompts for SSH tunnel port, respects pre-marked PII, infers additional
                             likely PII, and rewrites the same YAML files with enrichment

Phase 3: Framework
  build-kpi-framework     ← builds KPI Framework Sheet from me_goals.md + enriched sources.yml
  plan-dbt-architecture   ← designs dbt architecture for dashboards, metrics, charts, alerts,
                             filters, and drilldowns → dbt_plan.md
  generate-er-diagram     ← designs entity model from KPI Framework + dbt_plan.md → er_diagram.md

Phase 4: Model Development
  write-dbt-staging       ← stg_* models: rename, cast, deduplicate, null-handling
  write-dbt-intermediate  ← int_* models: joins, cohort construction, derived fields
  write-dbt-marts         ← marts_* models: chart-ready tables for Dalgo outputs
  generate-data-dictionary← produces Data Dictionary Sheet for client handoff

Finalization (mandatory)
  finalize-dbt-project    ← dbt validation, SQLFluff lint, dbt YAML review, dbt docs generation
```

### Modification Track

Lightweight path for existing clients adding or changing metrics.

```
  modify-requirements    ← requirement changes: KPI/dashboard/chart/filter/drilldown/alert changes
  investigate-issue      ← bugs/discrepancies: wrong numbers, duplicates, freshness, dashboard mismatches
  dbt-edit-plan          ← scoped dbt edit plan; directly callable or invoked by modification/investigation
  explore-data           ← only if a new data source was added
  build-kpi-framework    ← update existing KPI Framework Sheet rows
  plan-dbt-architecture  ← refresh architecture plan if outputs, filters, drilldowns, alerts,
                             or model boundaries change
  generate-er-diagram    ← refresh if entity relationships or join paths change
  write-dbt-staging      ← only affected models
  write-dbt-intermediate ← only affected models
  write-dbt-marts        ← only affected models
  generate-data-dictionary
  finalize-dbt-project   ← same finalization step as new engagement
```

### When to Use Which Track

| | New Engagement | Modification Track |
|---|---|---|
| **Trigger** | New client or new program | Change request on a live client |
| **Scope** | Full four-phase process | Affected layers only |
| **KPI Framework** | Built from scratch after data exploration | Existing sheet — add/revise rows |
| **dbt models** | All layers written fresh | Only impacted models rewritten |
| **Data Dictionary** | Generated at close | Updated in-place |

---

## Skills Reference

| Skill | Phase | Input | Output |
|---------|-------|-------|--------|
| `dalgo-consulting-workflow` | Router | Phase/workflow request | Invokes the right skills in order |
| `discover-engagement` | Discovery | Requirements Sheet URL, dbt repo path, engagement name | Folder structure + `me_goals.md` |
| `read-requirements` | Discovery helper | Requirements Sheet ID/URL | `me_goals.md` |
| `explore-data` | Data Exploration | One or more paths to `source.yml` / `sources.yml`; reads `me_goals.md` and dbt repo/profile context | Enriched source YAML files |
| `build-kpi-framework` | Framework | `me_goals.md`, enriched `sources.yml` files | KPI Framework Sheet, `kpi_framework.md`, `kpi_framework.json` |
| `read-kpi-framework` | Framework helper | KPI Framework Sheet ID | Refreshed local KPI Framework Markdown/JSON |
| `plan-dbt-architecture` | Framework | `me_goals.md`, KPI Framework, enriched `sources.yml` files | `dbt_plan.md` |
| `generate-er-diagram` | Framework | `me_goals.md`, KPI Framework, `dbt_plan.md`, enriched `sources.yml` files | `er_diagram.md` |
| `write-dbt-staging` | Model Dev | `dbt_plan.md`, enriched `sources.yml` files | `stg_*.sql` models and YAML |
| `write-dbt-intermediate` | Model Dev | KPI Framework, `dbt_plan.md`, `er_diagram.md`, staging models | `int_*.sql` models and YAML |
| `write-dbt-marts` | Model Dev | KPI Framework, `dbt_plan.md`, intermediate models | `marts_*.sql` models and YAML |
| `generate-data-dictionary` | Model Dev | Final dbt models, dbt YAML files, KPI Framework | Data Dictionary Sheet, `data_dictionary.md`, `data_dictionary.json` |
| `finalize-dbt-project` | Finalization | Full dbt model set | dbt validation, SQLFluff, dbt docs, optional GitHub delivery |
| `modify-requirements` | Modification | Existing engagement change request | Change folder, optional KPI patch, dbt edit plan |
| `investigate-issue` | Diagnostics | Dashboard/KPI/data-quality issue | `investigation.md`, `queries.sql`, optional dbt edit plan |
| `dbt-edit-plan` | Modification | Change request, investigation, or direct dbt edit request | `dbt_edit_plan.md`, confirmed dbt edits, optional Data Dictionary refresh |
| `read-phase-context` | Shared helper | Engagement/repo hints | Accepted artifacts and dbt repo context |
| `validate-warehouse-access` | Shared helper | dbt repo/profile hints | Safe warehouse connection context |
| `apply-kpi-framework-patch` | Shared helper | Confirmed KPI patch | Updated KPI Framework artifacts |
| `github-delivery` | Shared helper | Repo path and intended files | Confirmed branch/push/PR |

---

## Agents

| Agent | What It Does |
|-------|-------------|
| **ngo-data-platform-consultant** | Evaluates outputs as "Priya" — a non-technical NGO program manager. Catches jargon, complexity, and anything a field coordinator couldn't act on. |
| **dbt-engineer** | Writes and reviews dbt SQL models across staging, intermediate, and mart layers. Follows the medallion architecture and KPI Framework contract. |

---

## Skills

| Skill | What It Does |
|-------|-------------|
| **read-requirements** | Reads all tabs from the Requirements Sheet via Google Sheets API and generates `me_goals.md`. Called automatically by `discover-engagement`; also usable standalone to refresh `me_goals.md` at any point mid-engagement. |
| **read-kpi-framework** | Reads all tabs from the KPI Framework Sheet and writes normalized `kpi_framework.md` and `kpi_framework.json` for `plan-dbt-architecture`, `generate-er-diagram`, and model-development skills. |
| **read-phase-context** | Resolves and reads `me_goals.md`, KPI Framework, `dbt_plan.md`, `er_diagram.md`, enriched source YAMLs, dbt repo context, and metadata for Phase 4 skills. |
| **dbt-edit-plan** | Creates a scoped dbt edit plan and implements it only after explicit confirmation. Used directly or by `modify-requirements` and `investigate-issue`. |
| **investigate-issue** | Diagnoses wrong numbers, duplicates, freshness issues, and dashboard discrepancies using warehouse data, KPI Framework, dbt plan, and current models. |

---

## Common Workflows

### New Engagement

```
Ask dbt-wizard to run:

Run the Dalgo consulting workflow for a new engagement.
Phase 1 inputs: ...
Phase 2 source YAMLs: ...
Use the dbt repo at ...
```

### Modification

```
Ask dbt-wizard:

Modify requirements: add district drilldown to the attendance dashboard.

Investigate issue: attendance rate is too high for June in the district dashboard.

Create a dbt edit plan: fix duplicate enrollment join in marts_attendance.
```

### Spot-Check During Model Dev

```
# After each dbt run, verify:
# - Row counts match source (staging)
# - Join cardinalities correct, no fan-out (intermediate)
# - Metric values match KPI Framework spot calculations (marts)
```

---

## Key Principles

- **Requirements Sheet drives scope** — client fills it once; all changes route through an explicit KPI Framework update.
- **KPI Framework is the technical contract** — no dbt model is written without a corresponding KPI row.
- **Analytics outputs shape the dbt plan** — dashboards, charts, filters, drilldowns, and alerts are first-class requirements, not afterthoughts derived from KPIs alone.
- **Marts are chart-ready, not forced facts/dimensions** — final models use the `marts_` prefix and are shaped around Dalgo output requirements.
- **Requirement changes and bugs use different paths** — use `modify-requirements` for analytics contract changes, and `investigate-issue` for wrong numbers, duplicates, freshness, or dashboard discrepancies.
- **No unconfirmed edits** — `modify-requirements` asks before writing KPI Framework changes, and `dbt-edit-plan` asks before editing dbt code/YAML.
- **Modification work is auditable** — every change or investigation gets a durable folder with the request, plan, SQL run, and metadata.
- **GitHub delivery is explicit** — when a dbt repo has a GitHub remote, `dbt-edit-plan` and `finalize-dbt-project` ask before committing, pushing, or opening a PR.
- **Data exploration before framework authoring** — raw table shape is understood before the KPI Framework is built.
- **Layer-by-layer verification** — run and validate each dbt layer before writing the next.
- **PII must not be exposed in artifacts** — `explore-data` respects consultant-marked PII, avoids raw-value inspection for those columns, may infer additional likely PII heuristically, and never stores sample values for columns marked PII.
- **Finalization is mandatory** — dbt validation, SQLFluff, dbt YAML documentation/test review, and dbt docs generation before every delivery.
- **Delivery is PR-based** — consulting changes ship on a dedicated branch, never direct-pushed to main.
- **NGO data quality is often poor** — staging models must be defensive; document assumptions in `sources.yml` and dbt model `.yml` files.

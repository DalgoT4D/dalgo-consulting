# dalgo-consulting

AI-assisted consulting workflow for building dbt data models that transform raw NGO program data into M&E metrics and dashboards. Each engagement moves through four phases: **Discovery → Data Exploration → Framework → Model Development**.

## Repo Structure

```
dalgo-consulting/
├── .claude/
│   ├── agents/              # Specialized AI agents (auto-invoked by context)
│   ├── commands/            # Phase-specific consulting commands
│   └── skills/              # Reusable skills (read_requirements, tal-lens, etc.)
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
            │   └── sources.yml         # Optional working copy; /explore_data can also target dbt repo source YAMLs directly
            ├── framework/
            │   ├── kpi_framework.md    # Local normalized copy of KPI Framework Sheet
            │   ├── kpi_framework.json  # Machine-readable contract for downstream commands
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

## Three Types of Tools

| Type | Location | Purpose | How to Use |
|------|----------|---------|------------|
| **Commands** | `.claude/commands/` | Phase-specific workflows with structured inputs and outputs | `/discover`, `/explore_data`, etc. |
| **Agents** | `.claude/agents/` | Specialized personas invoked by context | Claude picks the right agent automatically |
| **Skills** | `.claude/skills/` | Reusable sub-routines called by commands or directly | Invoke by name (e.g. `/read_requirements`, `/tal-lens`) |

---

## Consulting Workflow

### New Engagement

Full four-phase process for a new client or program.

```
Phase 1: Discovery
  /discover               ← interactive wizard: collects engagement details, creates folders,
                             reads Requirements Sheet → generates me_goals.md

Phase 2: Data Exploration
  /explore_data           ← reads me_goals.md + one or more passed source.yml/sources.yml files;
                             prompts for SSH tunnel port, respects pre-marked PII, infers additional
                             likely PII, and rewrites the same YAML files with enrichment

Phase 3: Framework
  /build_kpi_sheet        ← builds KPI Framework Sheet from me_goals.md + enriched sources.yml
  /dbt_plan               ← designs dbt architecture for dashboards, metrics, charts, alerts,
                             filters, and drilldowns → dbt_plan.md
  /generate_er_diagram    ← designs entity model from KPI Framework + dbt_plan.md → er_diagram.md

Phase 4: Model Development
  /write_staging          ← stg_* models: rename, cast, deduplicate, null-handling
  /write_intermediate     ← int_* models: joins, cohort construction, derived fields
  /write_mart             ← marts_* models: chart-ready tables for Dalgo outputs
  /generate_data_dict     ← produces Data Dictionary Sheet for client handoff

Finalization (mandatory)
  /finalize               ← dbt validation, SQLFluff lint, dbt YAML review, dbt docs generation
```

### Modification Track

Lightweight path for existing clients adding or changing metrics.

```
  /modify                ← requirement changes: KPI/dashboard/chart/filter/drilldown/alert changes
  /investigate           ← bugs/discrepancies: wrong numbers, duplicates, freshness, dashboard mismatches
  /dbt_edit_plan         ← scoped dbt edit plan; directly callable or called by /modify or /investigate
  /explore_data           ← only if a new data source was added
  /build_kpi_sheet        ← update existing KPI Framework Sheet rows
  /dbt_plan               ← refresh architecture plan if outputs, filters, drilldowns, alerts,
                             or model boundaries change
  /generate_er_diagram    ← refresh if entity relationships or join paths change
  /write_staging          ← only affected models
  /write_intermediate     ← only affected models
  /write_mart             ← only affected models
  /generate_data_dict     ← update Data Dictionary Sheet
  /finalize               ← same finalization step as new engagement
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

## Commands Reference

| Command | Phase | Input | Output |
|---------|-------|-------|--------|
| `/discover` | Discovery | Interactive — Requirements Sheet URL, dbt repo path, engagement name | Folder structure + `me_goals.md` |
| `/explore_data` | Data Exploration | One or more paths to `source.yml` / `sources.yml`; reads `me_goals.md` and dbt repo/profile context | Rewrites the same YAML files with column profiles, explicit + inferred PII flags, and LLM notes |
| `/build_kpi_sheet` | Framework | `me_goals.md`, enriched `sources.yml` files | KPI Framework Sheet (Google Sheet), `kpi_framework.md`, `kpi_framework.json` |
| `/dbt_plan` | Framework | `me_goals.md`, KPI Framework, enriched `sources.yml` files | `dbt_plan.md` |
| `/generate_er_diagram` | Framework | `me_goals.md`, KPI Framework, `dbt_plan.md`, enriched `sources.yml` files | `er_diagram.md` |
| `/modify` | Modification | Existing engagement change request | `change_request.md`, optional `kpi_framework_patch.json`, then `/dbt_edit_plan` |
| `/investigate` | Diagnostics | Dashboard/KPI/data-quality issue, warehouse access, KPI Framework, dbt repo | `investigation.md`, `queries.sql`, optional `/dbt_edit_plan` |
| `/dbt_edit_plan` | Modification | Change request, investigation, or direct dbt edit request | `dbt_edit_plan.md`, confirmed dbt edits, optional Data Dictionary refresh |
| `/write_staging` | Model Dev | `dbt_plan.md`, enriched `sources.yml` files | `stg_*.sql` models |
| `/write_intermediate` | Model Dev | KPI Framework, `dbt_plan.md`, `er_diagram.md`, staging models | `int_*.sql` models |
| `/write_mart` | Model Dev | KPI Framework, `dbt_plan.md`, intermediate models | `marts_*.sql` models |
| `/generate_data_dict` | Model Dev | Final dbt models, dbt YAML files, KPI Framework | Data Dictionary Sheet (Google Sheet), `data_dictionary.md`, `data_dictionary.json` |
| `/finalize` | Finalization | Full dbt model set | dbt compile/build, SQLFluff clean, dbt YAML documentation/test review, dbt docs generation |

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
| **read_requirements** | Reads all tabs from the Requirements Sheet via Google Sheets API and generates `me_goals.md`. Called automatically by `/discover`; also usable standalone to refresh `me_goals.md` at any point mid-engagement. |
| **read_kpi_framework** | Reads all tabs from the KPI Framework Sheet and writes normalized `kpi_framework.md` and `kpi_framework.json` for `/dbt_plan`, `/generate_er_diagram`, and model-development commands. |
| **read_phase_context** | Resolves and reads `me_goals.md`, KPI Framework, `dbt_plan.md`, `er_diagram.md`, enriched source YAMLs, dbt repo context, and metadata for Phase 4 commands. |
| **dbt_edit_plan** | Creates a scoped dbt edit plan and implements it only after explicit confirmation. Used by `/dbt_edit_plan`, `/modify`, and `/investigate`. |
| **investigate** | Diagnoses wrong numbers, duplicates, freshness issues, and dashboard discrepancies using warehouse data, KPI Framework, dbt plan, and current models. |
| **tal-lens** | Tal Raviv's technology philosophy — demystify, build first, anti-hype, clarity over cleverness. Use when evaluating tooling choices or architecture decisions. |

---

## Common Workflows

### New Engagement (discovery to delivery)

```
# Phase 1 — Discovery
/discover
# (interactive — follow the prompts)

# Phase 2 — Data Exploration
/explore_data path/to/source.yml path/to/other_source.yml

# Phase 3 — Framework
/build_kpi_sheet path/to/source.yml path/to/other_source.yml
/dbt_plan path/to/source.yml path/to/other_source.yml
/generate_er_diagram

# Phase 4 — Model Development (iterate per layer)
/write_staging
# dbt run --select staging → verify → fix → re-run
/write_intermediate
# dbt run --select intermediate → verify → fix → re-run
/write_mart
# dbt run --select marts → compare to KPI Framework → fix → re-run
/generate_data_dict

# Finalization
/finalize
```

### Modification (change request on live client)

```
# Requirement change:
/modify "Add district drilldown to the attendance dashboard"

# Dashboard/model bug or wrong number:
/investigate "Attendance rate is too high for June in the district dashboard"

# Direct model edit when the change is already understood:
/dbt_edit_plan "Fix duplicate enrollment join in marts_attendance"

# If new data source:
/explore_data path/to/new_source.yml path/to/other_new_source.yml
/modify "Add new source-backed KPI from the new table"
/dbt_plan                 # if outputs, filters, drilldowns, alerts, or model boundaries changed
/generate_er_diagram      # if relationships or join paths changed

# Rewrite only affected layers
/write_staging   # if raw schema changed
/write_intermediate
/write_mart

/generate_data_dict
/finalize
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
- **Requirement changes and bugs use different paths** — use `/modify` for analytics contract changes, and `/investigate` for wrong numbers, duplicates, freshness, or dashboard discrepancies.
- **No unconfirmed edits** — `/modify` asks before writing KPI Framework changes, and `/dbt_edit_plan` asks before editing dbt code/YAML.
- **Modification work is auditable** — every change or investigation gets a durable folder with the request, plan, SQL run, and metadata.
- **GitHub delivery is explicit** — when a dbt repo has a GitHub remote, `/dbt_edit_plan` and `/finalize` ask before committing, pushing, or opening a PR.
- **Data exploration before framework authoring** — raw table shape is understood before the KPI Framework is built.
- **Layer-by-layer verification** — run and validate each dbt layer before writing the next.
- **PII must not be exposed in artifacts** — `/explore_data` respects consultant-marked PII, avoids raw-value inspection for those columns, may infer additional likely PII heuristically, and never stores sample values for columns marked PII.
- **Finalization is mandatory** — dbt validation, SQLFluff, dbt YAML documentation/test review, and dbt docs generation before every delivery.
- **Delivery is PR-based** — consulting changes ship on a dedicated branch, never direct-pushed to main.
- **NGO data quality is often poor** — staging models must be defensive; document assumptions in `sources.yml` and dbt model `.yml` files.

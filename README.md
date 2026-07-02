# dalgo-consulting

AI-assisted consulting workflow for building dbt data models that transform raw NGO program data into M&E metrics and dashboards. Each engagement moves through four phases: **Discovery → Data Exploration → Framework → Model Development**.

## Repo Structure

```
dalgo-consulting/
├── .claude/
│   ├── agents/              # Specialized AI agents (auto-invoked by context)
│   ├── commands/            # Phase-specific consulting commands
│   └── skills/              # Reusable skills (read_requirements, tal-lens, etc.)
├── secrets/
│   └── my_service_key.json  # Google service account key (gitignored)
└── workdocs/
    └── consulting/
        ├── process.md                  # Full process reference
        ├── artifact-design-plan.md     # Artifact schema designs
        ├── scripts/                    # Python automation scripts
        │   ├── read_requirements.py    # Reads Requirements Sheet → stdout
        │   └── create_sheet.py         # Creates Google Sheet templates
        └── {engagement}/
            ├── discovery/
            │   └── me_goals.md         # Shared context for ALL downstream phases
            ├── data_exploration/
            │   ├── sources.yml         # Optional working copy; /explore_data can also target one or more dbt repo source YAMLs directly
            │   └── er_diagram.md       # Entity-relationship diagram
            └── models/                 # Or inside the client's dbt repo
                ├── staging/
                ├── intermediate/
                └── marts/

Google Sheets (linked from workdocs, not stored as files):
├── Requirements Sheet      ← 4-tab workbook: Instructions / Engagement Context / Data Sources / Metrics
├── KPI Framework Sheet     ← consultant-built technical spec
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
  /curate_metrics         ← reads me_goals.md + sources.yml → metrics.md
  /build_kpi_sheet        ← builds KPI Framework Sheet from me_goals.md + sources.yml
  /generate_er_diagram    ← designs entity model → er_diagram.md

Phase 4: Model Development
  /write_staging          ← stg_* models: rename, cast, deduplicate, null-handling
  /write_intermediate     ← int_* models: joins, cohort construction, derived fields
  /write_mart             ← fct_*/dim_* models: metric calculations per KPI Framework
  /generate_data_dict     ← produces Data Dictionary Sheet for client handoff

Finalization (mandatory)
  /finalize               ← SQLFluff lint, dbt-osmosis docs, open GitHub PR to main
```

### Modification Track

Lightweight path for existing clients adding or changing metrics.

```
  /build_kpi_sheet        ← update existing KPI Framework Sheet rows
  /explore_data           ← only if a new data source was added
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
| `/curate_metrics` | Framework | `me_goals.md`, `sources.yml` | `metrics.md` |
| `/build_kpi_sheet` | Framework | `me_goals.md`, `sources.yml` | KPI Framework Sheet (Google Sheet) |
| `/generate_er_diagram` | Framework | `me_goals.md`, KPI Framework Sheet, `sources.yml` | `er_diagram.md` |
| `/write_staging` | Model Dev | KPI Framework, `sources.yml` | `stg_*.sql` models |
| `/write_intermediate` | Model Dev | KPI Framework, staging models | `int_*.sql` models |
| `/write_mart` | Model Dev | KPI Framework, intermediate models | `fct_*.sql`, `dim_*.sql` models |
| `/generate_data_dict` | Model Dev | Final dbt models, `schema.yml` | Data Dictionary Sheet (Google Sheet) |
| `/finalize` | Finalization | Full dbt model set | SQLFluff clean, dbt-osmosis docs, GitHub PR |

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
/curate_metrics
/build_kpi_sheet
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
# Update KPI Framework Sheet manually or with /build_kpi_sheet
# If new data source:
/explore_data path/to/new_source.yml path/to/other_new_source.yml

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
- **Data exploration before framework authoring** — raw table shape is understood before the KPI Framework is built.
- **Layer-by-layer verification** — run and validate each dbt layer before writing the next.
- **PII must not be exposed in artifacts** — `/explore_data` respects consultant-marked PII, avoids raw-value inspection for those columns, may infer additional likely PII heuristically, and never stores sample values for columns marked PII.
- **Finalization is mandatory** — SQLFluff + dbt-osmosis + GitHub PR before every delivery.
- **Delivery is PR-based** — consulting changes ship on a dedicated branch, never direct-pushed to main.
- **NGO data quality is often poor** — staging models must be defensive; document assumptions in `sources.yml` and `schema.yml`.

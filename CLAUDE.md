# Dalgo Consulting — Claude Code Guide

This repo contains the AI-assisted consulting workflow for building dbt data models that transform raw NGO program data into M&E metrics. Engagements move through four phases: **Discovery → Data Exploration → Framework → Model Development**.

See `docs/process.md` for the full process reference.

---

## What This Repo Is

- **Not** a product codebase — there is no app to run or deploy here.
- **Yes** a workspace for LLM-assisted consulting: generating artifacts, writing dbt SQL, exploring raw data, and managing the engagement lifecycle.
- Client dbt project repos are symlinked or referenced separately; models may live inside those repos, not here.

---

## Repo Structure

```
dalgo-consulting/
├── .claude/
│   ├── agents/
│   └── skills/
├── secrets/
│   └── my_service_key.json       ← Google service account key (gitignored)
├── docs/
│   ├── process.md
│   └── artifact-design-plan.md
├── scripts/
│   ├── read_requirements.py
│   ├── kpi_framework_sheet.py
│   └── data_dictionary_sheet.py
└── workdocs/consulting/
    └── {engagement}/
        ├── discovery/
        │   └── me_goals.md        ← LLM-generated; shared context for ALL downstream phases
        ├── data_exploration/
        │   └── sources.yml
        ├── framework/
        │   ├── kpi_framework.md
        │   ├── kpi_framework.json
        │   ├── dbt_plan.md
        │   ├── er_diagram.md
        │   └── phase3_metadata.json
        ├── models/                ← or inside the client's dbt repo
        │   ├── data_dictionary.md
        │   ├── data_dictionary.json
        │   ├── phase4_metadata.json
        │   ├── staging/
        │   ├── intermediate/
        │   └── marts/
        ├── modifications/
        └── investigations/
```

---

## Two Tracks

**New Engagement** — full four-phase process for a new client or program.
**Modification** — lightweight path for existing clients adding or changing metrics.

Always check which track applies before starting work. Modification is the default for live clients.

---

## Skills

dbt-wizard is the consultant execution surface. It reads `.claude/skills/`, so all workflow logic must live in skills.

| Skill | Phase | What It Does |
|---------|-------|-------------|
| `dalgo-consulting-workflow` | Router | Routes full phase/workflow requests to the right skills |
| `discover-engagement` | Discovery | Interactive setup wizard — collects engagement details, creates folder structure, reads Requirements Sheet, generates `me_goals.md` |
| `explore-data` | Data Exploration | Profiles raw tables across one or more passed `source.yml` / `sources.yml` files, prompts for SSH tunnel readiness, respects pre-marked PII, infers additional likely PII, and rewrites the same YAML files using `me_goals.md` for context |
| `build-kpi-framework` | Framework | Builds or updates the multi-tab KPI Framework Sheet from `me_goals.md` + enriched source YAMLs, then saves `kpi_framework.md` and `kpi_framework.json` |
| `plan-dbt-architecture` | Framework | Builds `dbt_plan.md` for Dalgo dashboards, metrics, charts, alerts, filters, drilldowns, and dbt model layers |
| `generate-er-diagram` | Framework | Designs entity model from KPI Framework + `dbt_plan.md` → `er_diagram.md` |
| `modify-requirements` | Modification | Handles requirement changes for existing engagements, updates KPI Framework only after confirmation, then invokes `dbt-edit-plan` |
| `investigate-issue` | Diagnostics | Diagnoses wrong numbers, duplicates, freshness issues, and dashboard discrepancies with warehouse queries and reproducible findings |
| `dbt-edit-plan` | Modification | Plans scoped dbt edits and implements only after explicit code-edit confirmation |
| `write-dbt-staging` | Model Dev | Writes `stg_*.sql` models |
| `write-dbt-intermediate` | Model Dev | Writes `int_*.sql` models |
| `write-dbt-marts` | Model Dev | Writes chart-ready `marts_*.sql` models for Dalgo outputs |
| `generate-data-dictionary` | Model Dev | Produces Data Dictionary Sheet for client handoff |
| `finalize-dbt-project` | Finalization | dbt validation + SQLFluff lint + dbt YAML documentation/test review + dbt docs generation |

---

## Agents

- **ngo-data-platform-consultant** — evaluates outputs as "Priya", a non-technical NGO program manager. Use to gut-check language, complexity, and client-facing artifacts.
- **dbt-engineer** — writes and reviews dbt SQL across staging, intermediate, and mart layers.

---

## Skills

- **read-requirements** — reads all tabs from the Requirements Sheet (Google Sheets API) and generates `me_goals.md`. Called by `discover-engagement`; also usable standalone to refresh `me_goals.md` mid-engagement.
- **read-kpi-framework** — reads all tabs from the KPI Framework Sheet and writes normalized `kpi_framework.md` and `kpi_framework.json`. Called by `build-kpi-framework`, `plan-dbt-architecture`, and `generate-er-diagram`.
- **read-phase-context** — resolves and reads accepted Phase 3 artifacts, source YAMLs, dbt repo context, and metadata for Phase 4 skills.
- **dbt-edit-plan** — plans scoped dbt edits and implements only after explicit confirmation.
- **investigate-issue** — diagnoses dashboard/KPI/data-quality issues and writes reproducible investigation findings plus SQL.
- **validate-warehouse-access** — shared dbt profile, tunnel, and `dbt debug` validation.
- **apply-kpi-framework-patch** — applies confirmed KPI Framework patches and refreshes local artifacts.
- **github-delivery** — explicit commit, push, and PR confirmation gate.

---

## Key Constraints

- **KPI Framework is the contract** — no dbt model is written without a corresponding KPI row in the Framework Sheet.
- **Analytics outputs are part of the contract** — dashboards, charts, filters, drilldowns, and alerts must be captured in the KPI Framework before the dbt plan is finalized.
- **Marts are chart-ready, not facts/dimensions by default** — final models use `marts_` naming and are shaped around Dalgo output requirements.
- **Requirement changes and bugs use different paths** — use `modify-requirements` for analytics contract changes, and `investigate-issue` for wrong numbers, duplicates, freshness, or dashboard discrepancies.
- **No unconfirmed edits** — `modify-requirements` asks before writing KPI Framework changes, and `dbt-edit-plan` asks before editing dbt code/YAML.
- **GitHub delivery is explicit** — when a dbt repo has a GitHub remote, `dbt-edit-plan` and `finalize-dbt-project` ask before committing, pushing, or opening a PR.
- **Data exploration before framework authoring** — raw table shape must be understood before the KPI Framework is built.
- **Layer-by-layer verification** — run and validate each dbt layer before writing the next.
- **Never expose credentials** — skills may read dbt profiles and environment variables for connectivity, but must never print raw profile files, usernames, passwords, tokens, private keys, or resolved secret values.
- **Do not expose PII in artifacts** — `explore-data` must respect consultant-marked PII columns, avoid querying raw values from them during analysis, and never store sample values for columns marked PII.
- **Preserve source YAML structure** — `source.yml` / `sources.yml` may vary across client repos; generated metadata must be merged into the existing YAML without dropping user-authored dbt fields.
- **NGO data is often messy** — paper-to-digital conversion, inconsistent enumerators, mid-program schema changes. Staging models must be defensive. Document assumptions explicitly.
- **Finalization is mandatory** — dbt validation, SQLFluff, dbt YAML documentation/test review, and dbt docs generation before every delivery, for both tracks.
- **Delivery is PR-based** — consulting changes ship on a dedicated branch, never direct-pushed to main.

---

## Users

The end clients are NGO M&E managers and program staff — non-technical users who filled in a Requirements Sheet in plain English. All client-facing artifacts (KPI Framework Sheet, Data Dictionary Sheet, `me_goals.md`) must be written for this audience: no SQL, no jargon, no unexplained acronyms.

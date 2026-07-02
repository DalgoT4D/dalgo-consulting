# Dalgo Consulting — Claude Code Guide

This repo contains the AI-assisted consulting workflow for building dbt data models that transform raw NGO program data into M&E metrics. Engagements move through four phases: **Discovery → Data Exploration → Framework → Model Development**.

See `workdocs/consulting/process.md` for the full process reference.

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
│   ├── commands/
│   └── skills/
├── secrets/
│   └── my_service_key.json       ← Google service account key (gitignored)
└── workdocs/consulting/
    ├── process.md                 ← full process reference
    ├── artifact-design-plan.md    ← artifact schema designs
    ├── scripts/                   ← Python scripts for consulting automation
    │   ├── read_requirements.py   ← reads Requirements Sheet tabs → stdout
    │   └── create_sheet.py        ← creates Google Sheet templates
    └── {engagement}/
        ├── discovery/
        │   └── me_goals.md        ← LLM-generated; shared context for ALL downstream phases
        ├── data_exploration/
        │   └── er_diagram.md
        └── models/                ← or inside the client's dbt repo
```

---

## Two Tracks

**New Engagement** — full four-phase process for a new client or program.
**Modification** — lightweight path for existing clients adding or changing metrics.

Always check which track applies before starting work. Modification is the default for live clients.

---

## Commands

| Command | Phase | What It Does |
|---------|-------|-------------|
| `/discover` | Discovery | Interactive setup wizard — collects engagement details, creates folder structure, reads Requirements Sheet, generates `me_goals.md` |
| `/explore_data` | Data Exploration | Profiles raw tables in a passed `source.yml` / `sources.yml`, infers likely PII, and rewrites the same YAML using `me_goals.md` for context |
| `/curate_metrics` | Framework | Reads `me_goals.md` + `sources.yml` → `metrics.md` |
| `/build_kpi_sheet` | Framework | Builds or updates the KPI Framework Sheet from `me_goals.md` + `sources.yml` |
| `/generate_er_diagram` | Framework | Designs entity model → `er_diagram.md` |
| `/write_staging` | Model Dev | Writes `stg_*.sql` models |
| `/write_intermediate` | Model Dev | Writes `int_*.sql` models |
| `/write_mart` | Model Dev | Writes `fct_*.sql` / `dim_*.sql` models |
| `/generate_data_dict` | Model Dev | Produces Data Dictionary Sheet for client handoff |
| `/finalize` | Finalization | SQLFluff lint + dbt-osmosis docs + GitHub PR |

---

## Agents

- **ngo-data-platform-consultant** — evaluates outputs as "Priya", a non-technical NGO program manager. Use to gut-check language, complexity, and client-facing artifacts.
- **dbt-engineer** — writes and reviews dbt SQL across staging, intermediate, and mart layers.

---

## Skills

- **tal-lens** — use when evaluating tooling choices or architecture decisions.
- **read_requirements** — reads all tabs from the Requirements Sheet (Google Sheets API) and generates `me_goals.md`. Called by `/discover`; also usable standalone to refresh `me_goals.md` mid-engagement.

---

## Key Constraints

- **KPI Framework is the contract** — no dbt model is written without a corresponding KPI row in the Framework Sheet.
- **Data exploration before framework authoring** — raw table shape must be understood before the KPI Framework is built.
- **Layer-by-layer verification** — run and validate each dbt layer before writing the next.
- **Do not expose PII in artifacts** — `/explore_data` may infer additional likely PII heuristically, but it must not store sample values for columns marked PII.
- **Preserve source YAML structure** — `source.yml` / `sources.yml` may vary across client repos; generated metadata must be merged into the existing YAML without dropping user-authored dbt fields.
- **NGO data is often messy** — paper-to-digital conversion, inconsistent enumerators, mid-program schema changes. Staging models must be defensive. Document assumptions explicitly.
- **Finalization is mandatory** — SQLFluff + dbt-osmosis + GitHub PR before every delivery, for both tracks.
- **Delivery is PR-based** — consulting changes ship on a dedicated branch, never direct-pushed to main.

---

## Users

The end clients are NGO M&E managers and program staff — non-technical users who filled in a Requirements Sheet in plain English. All client-facing artifacts (KPI Framework Sheet, Data Dictionary Sheet, `me_goals.md`) must be written for this audience: no SQL, no jargon, no unexplained acronyms.

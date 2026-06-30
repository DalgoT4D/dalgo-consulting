---
name: read_requirements
description: Read all tabs from a consulting Requirements Sheet (Google Sheet) and generate me_goals.md — the shared context document for all downstream consulting phases. Invoked by /discover and any skill that needs fresh Requirements Sheet data.
---

# Read Requirements Sheet

Read the Requirements Sheet and synthesise `me_goals.md` for the engagement.

## Inputs (passed from the calling command)

- `{spreadsheet_id}` — Google Sheet ID extracted from the sheet URL
- `{sheet_url}` — Full URL of the Requirements Sheet
- `{engagement}` — Folder slug (e.g. `give_do`)
- `{engagement_display}` — Display name (e.g. `GiveDo`)
- `{track}` — `new` or `modification`
- `{dbt_repo_path}` — Local path to the dbt repo

## Step 1 — Fetch Sheet Content

Run the following script:

```bash
python3 scripts/read_requirements.py \
  --sheet-id {spreadsheet_id} \
  --key-file secrets/my_service_key.json
```

The script prints structured markdown to stdout — one section per tab (Engagement Context, Data Sources, Metrics).

If the script exits with a 403 error, stop and show:
> "The sheet could not be read. Make sure it has been shared (Editor access) with the service account: `{client_email}`"
Do not proceed until the user confirms the sheet has been shared and re-run.

## Step 2 — Synthesise me_goals.md

Using the script output, generate `me_goals.md` with the following structure. The file must be a **comprehensive reference document** — not a brief summary. Every downstream skill reads only this file, so it must contain the full content from all tabs.

```markdown
# M&E Goals — {engagement_display}

## Engagement Context
{NGO name, website, program names, overall M&E goals — synthesised from Engagement Context tab}

## Programs & Reporting
| Program | Reporting Cadence | Audience |
|---|---|---|
{One row per program, extracted from Engagement Context tab}

## Key M&E Questions
{Bulleted list of the core questions the data must answer, extracted from Engagement Context tab}

## Data Sources
| Data Source | Table / Form Name | Column Name | Data Type | Description | Example Values |
|---|---|---|---|---|---|
{Full contents of the Data Sources tab — every row verbatim}

## Metrics Required
| # | Metric Name | What is measured | Calculation logic | Data source ref | Audience | Frequency | Breakdown dimensions | Consultant notes |
|---|---|---|---|---|---|---|---|---|
{Full contents of the Metrics tab — every row verbatim, including consultant notes}

## Open Questions & Ambiguities
{List any: blank required fields in the Metrics tab, calculation logic that is unclear or contradictory,
data source references in Metrics that do not match any row in Data Sources,
programs mentioned in Engagement Context but absent from Metrics}

---
_Generated from Requirements Sheet: {sheet_url}_
_Track: {track} | dbt repo: {dbt_repo_path} | Date: {today's date}_
```

## Step 3 — Save

Write the file to:
`workdocs/consulting/{engagement}/discovery/me_goals.md`

Confirm to the caller:
> "`me_goals.md` generated at `workdocs/consulting/{engagement}/discovery/me_goals.md`"

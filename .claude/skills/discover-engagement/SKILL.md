---
name: discover-engagement
description: "Run Phase 1 discovery for a Dalgo consulting engagement: collect engagement context, validate the dbt repo and Google service account, create workdocs folders, read the Requirements Sheet, and generate me_goals.md."
---

# Discover Engagement

Step-by-step setup wizard for a new engagement or modification. Works for both tracks.
Run through each step in order. Do not skip steps. Pause at each input prompt and wait for the user's response before continuing.

---

## Step 0 — Track Selection

Ask the user:
> "Is this a **new engagement** or a **modification** to an existing one? (new / modification)"

Store the answer as `{track}`.

---

## Step 1 — Engagement Name

Ask the user:
> "What is the engagement name? (e.g. 'GiveDo', 'Saajha')"

Derive a safe folder slug from the answer: lowercase, replace spaces with underscores, strip special characters.
Store as `{engagement}` (slug) and `{engagement_display}` (original name).

---

## Step 2 — dbt Repo Path

Ask the user:
> "What is the local path to the dbt repo for this engagement?"

Validate:
- Check that the path exists on disk.
- Check that it contains a `dbt_project.yml` file.

If the path or file is not found, show a warning and ask the user to re-enter.
Store the validated path as `{dbt_repo_path}`.

---

## Step 3 — Service Account Key

Check whether `secrets/my_service_key.json` exists in the repo root.

- **If found:** Read `client_email` from the JSON and show it to the user:
  > "Service account key found. Your Requirements Sheet must be shared (Editor access) with:
  > `{client_email}`"

- **If missing:** Prompt:
  > "Please place the Google service account key at `secrets/my_service_key.json`, then type 'done' to continue."
  > Wait for user confirmation before proceeding.
  > Once confirmed, re-read `client_email` and display it as above.

Store `{client_email}` and the key file path `secrets/my_service_key.json`.

---

## Step 4 — Folder Structure

**For `new` track:**
Create the following directory structure:
```
workdocs/consulting/{engagement}/
├── discovery/
├── data_exploration/
├── framework/
├── modifications/
├── investigations/
└── models/
```
Confirm to the user that the folders have been created.

**For `modification` track:**
Check whether `workdocs/consulting/{engagement}/` exists.
- If it exists: inform the user and skip folder creation.
- If it does not exist: ask:
  > "The folder `workdocs/consulting/{engagement}/` does not exist. Create it now? (yes / no)"
  > If yes, create the full folder structure above.
  > If no, continue without creating it.

---

## Step 5 — Requirements Sheet URL

Ask the user:
> "Paste the link to the filled Requirements Sheet Google Sheet."

Remind them:
> "Make sure the sheet has been shared (Editor access) with `{client_email}` before continuing."

Extract the spreadsheet ID from the URL. Google Sheet URLs follow the pattern:
`https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/...`

Store as `{spreadsheet_id}` and `{sheet_url}`.

---

## Step 6 — Read Requirements Sheet & Generate me_goals.md

Invoke the `read-requirements` skill, passing:
- `{spreadsheet_id}`
- `{sheet_url}`
- `{engagement}` (folder slug)
- `{engagement_display}` (display name)
- `{track}`
- `{dbt_repo_path}`

The skill will read all tabs from the Requirements Sheet and generate:
`workdocs/consulting/{engagement}/discovery/me_goals.md`

---

## Step 7 — Completion Summary

Print a completion summary:

```
✓ Engagement:        {engagement_display}
✓ Track:             {track}
✓ dbt repo:          {dbt_repo_path}
✓ Requirements Sheet: {sheet_url}
✓ me_goals.md:       workdocs/consulting/{engagement}/discovery/me_goals.md
```

Then print the next step guidance:
- **new engagement:** "Next → ingest raw data via Airbyte for all sources listed in me_goals.md, then run the `explore-data` skill with `path/to/source.yml [path/to/other_source.yml ...]`."
- **modification:** "Next → review `me_goals.md` for updated context, then run the `build-kpi-framework` skill with `path/to/source.yml [path/to/other_source.yml ...]`."

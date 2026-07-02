# /explore_data — Raw Warehouse Exploration

Profiles the raw tables listed across one or more passed `source.yml` or `sources.yml` files and enriches those same YAML files in place.
Use this after `/discover`, once the raw data has been ingested and the consultant is ready to understand the real warehouse shape before KPI design.

Treat the text after `/explore_data` as one or more candidate paths to YAML files.
Run through each step in order. Do not skip validation. Stop immediately on blocking errors instead of guessing.

---

## Step 0 — Resolve And Validate The Source YAML Inputs

If the user passed one or more paths after `/explore_data`, treat them as `{sources_paths}`.

If no path was provided, ask:
> "What are the paths to the `source.yml` / `sources.yml` files you want to enrich?"

For every candidate file, validate:
- The file exists on disk.
- The filename may be `source.yml`, `sources.yml`, or any `.yml` / `.yaml` file.
- The YAML parses successfully.
- The root contains a `sources` collection.
- Each source entry has a `schema`.
- Each table entry has a `name`.

Allow these variations without failing:
- optional root keys like `version`
- extra dbt properties such as `meta`, `tags`, `tests`, `database`, `columns`
- table entries with no `identifier` — default to the table `name` in memory
- partial column entries that contain only `name` or `description`
- existing column-level `pii` and `pii_reason` fields that were authored by the consultant

If multiple files were provided:
- remove exact duplicate paths
- preserve the user-provided file order
- stop if the files clearly belong to different dbt repos or different engagements and you cannot reconcile that automatically

If parsing fails or a file structure is missing `sources`, stop and show the exact issue and the file path.
Do not rewrite the file yet.

Store:
- `{sources_paths}`
- `{sources_yamls}`

---

## Step 1 — Confirm SSH Tunnel Readiness

Prompt the user before any warehouse work starts:
> "Before `/explore_data` continues, make sure any required SSH tunnel is already running in another terminal tab. What local port is the tunnel using? Press Enter for `5432`, or type `none` if no tunnel is needed."

If the user indicates the tunnel is not running yet:
> "Start the tunnel in another tab, then type `done` to continue. If the tunnel uses a non-default local port, include that port as well."

Store:
- `{tunnel_port}` with default `5432`
- or `{tunnel_port} = none`

This prompt is only a reminder and port capture. Do not skip the later `dbt debug` check.

---

## Step 2 — Resolve `me_goals.md`

Prefer deriving the engagement context automatically from all passed files.

Try, in this order:

1. **If every path in `{sources_paths}` is inside the same `workdocs/consulting/{engagement}/...`:**
   - Derive `{engagement}` from that shared path.
   - Set `{me_goals_path}` to:
     `workdocs/consulting/{engagement}/discovery/me_goals.md`

2. **If every path in `{sources_paths}` is inside the same dbt repo:**
   - Walk upward from each path until you find a directory containing `dbt_project.yml`.
   - If they all resolve to the same directory, store it as `{candidate_dbt_repo}`.
   - Search `workdocs/consulting/*/discovery/me_goals.md` for a footer line containing:
     `dbt repo: {candidate_dbt_repo}`
   - If exactly one file matches, use it as `{me_goals_path}`.

3. **If neither of the above yields a unique file:**
   - Ask the user:
     > "I could not uniquely determine the engagement context. What is the path to the relevant `me_goals.md` file?"

Validate that `{me_goals_path}` exists, then read it fully before doing any profiling work.

Store:
- `{me_goals_path}`
- `{me_goals_contents}`

---

## Step 3 — Resolve The dbt Repo

Prefer the dbt repo path recorded by `/discover`.

1. Look for the footer line in `{me_goals_contents}`:
   `dbt repo: ...`
2. If present, store that as `{dbt_repo_path}`.
3. If absent, and `{candidate_dbt_repo}` was found in Step 1, use `{candidate_dbt_repo}`.
4. If neither exists, ask the user:
   > "What is the local path to the dbt repo for this engagement?"

Validate:
- `{dbt_repo_path}` exists
- `{dbt_repo_path}/dbt_project.yml` exists

If both `{candidate_dbt_repo}` and the path from `me_goals.md` exist but they do not match, stop and ask the user which one to trust.
If any of the passed YAML paths fall outside `{dbt_repo_path}` and outside `workdocs/consulting/{engagement}/`, stop and ask the user to confirm the intended file set.

Store:
- `{dbt_repo_path}`

---

## Step 4 — Resolve The Profile And Verify Connectivity

Find the profile configuration in this order:

1. `{dbt_repo_path}/profiles.yml`
2. `{dbt_repo_path}/profiles.yaml`
3. `~/.dbt/profiles.yml`

If none exists, stop and show:
> "No dbt profile file was found. Add a repo-local `profiles.yml` or configure `~/.dbt/profiles.yml` first."

Read:
- the dbt profile name from `{dbt_repo_path}/dbt_project.yml`
- the active target and connection details from the chosen profile file

If the profile uses environment variables, resolve them from the current shell environment before continuing.
If required variables are missing, stop and list them explicitly.

If the resolved warehouse host is local (`localhost`, `127.0.0.1`, or equivalent) and `{tunnel_port}` is not `none`:
- compare the resolved profile port with `{tunnel_port}`
- if they do not match, stop and show the mismatch clearly
- tell the user to align the running tunnel and the dbt profile/env vars before re-running `/explore_data`

Run:

```bash
dbt debug \
  --project-dir "{dbt_repo_path}" \
  --profiles-dir "{profiles_dir}" \
  --log-path "/tmp/dalgo-explore-logs"
```

If `dbt debug` fails, stop immediately and show:
- the failing repo path
- the profile file used
- the likely next action: fix tunnel / SSH / network / credentials, then re-run `/explore_data`

For warehouse queries, use the active profile target to build a `psql` connection.
The current Dalgo setup is expected to be Postgres-backed. If the active adapter is not Postgres-compatible, stop and tell the user v1 of `/explore_data` currently supports Postgres-backed repos only.

Store:
- `{profiles_path}`
- `{profiles_dir}`
- `{profile_name}`
- `{profile_target}`
- `{warehouse_connection}`

---

## Step 5 — Profile Each Source Table

For each YAML file in `{sources_yamls}`:
- iterate through each source in that file's `sources` collection
- read the source-level `schema`
- respect an explicit `database` if present

For each table:
- use `identifier` when present; otherwise use `name`
- resolve the physical table as `{schema}.{identifier_or_name}`

Before profiling, confirm the table exists in the warehouse.
If any listed table is missing, stop and report the missing table exactly.

For every table, collect:
- `row_count`
- ordered column list with warehouse data types
- candidate primary keys
- candidate join keys
- date/time columns and detected formats
- anomalies
- short `llm_notes` grounded in `{me_goals_contents}`

For every column, collect:
- `data_type`
- `null_rate`
- `cardinality`
- `join_key_candidate`
- `date_format`
- `notes`

Use warehouse inspection queries to understand:
- column names and types
- distinctness and null patterns
- whether key-like fields have duplicates
- whether date-like columns use consistent formats
- whether there are obvious data quality issues such as blank strings, JSON blobs, repeated Airbyte metadata fields, mixed yes/no encodings, or duplicated records

For sample inspection:
- capture up to 5 distinct non-null sample values for columns that are not marked PII
- do not dump full rows unless needed to understand a table anomaly

### Respect Existing PII Flags

If an input YAML already marks a column as PII:
- treat that mark as authoritative
- preserve the existing `pii` value
- preserve the existing `pii_reason` when present
- do not query raw values from that column during analysis
- do not run `SELECT DISTINCT column`, sample-value queries, or raw `LIMIT` inspection against that column
- you may still compute aggregate-only statistics such as null rate, non-null count, cardinality, and duplicate counts

If an input YAML already sets `pii` on a column, do not replace it heuristically.
Only infer `pii` for columns where the input YAML did not already set that field.

### PII Inference Rules

Infer `pii: true` heuristically from column names, existing descriptions, and limited pattern checks where needed.
Only do this for columns that do not already have a user-authored `pii` value.

Treat these as likely PII by default:
- person names: `name`, `full_name`, `first_name`, `last_name`
- phone/contact fields: `phone`, `mobile`, `contact_number`, `whatsapp`
- email fields
- exact addresses or house-level location details
- government or program IDs tied to a person: `aadhaar`, `pan`, `id_number`, `national_id`, `beneficiary_id` when clearly person-level

Do **not** treat these as PII by default:
- city
- district
- state
- country
- program/site/location codes that are not person-identifying

For every column marked PII, whether explicit or inferred:
- set `pii: true`
- add a short `pii_reason`
- do not store `sample_values`

For every column not marked PII:
- set `pii: false`
- omit `pii_reason` unless needed to explain an edge case

### Heuristics

Use these guidelines when generating table-level outputs:
- `candidate_primary_keys`: non-null or near-non-null columns with very high cardinality, especially names like `id`, `uuid`, `case_id`, `record_id`
- `candidate_join_keys`: columns ending in `_id`, repeated entity keys, or keys reused across listed tables
- `date_columns`: names like `date`, `time`, `timestamp`, `created_at`, `updated_at`, plus columns whose values parse consistently as dates
- `anomalies`: high nulls, duplicate key-like values, mixed date formats, JSON-like text in scalar columns, placeholder values, or schema surprises relevant to downstream modeling
- `llm_notes`: 2-5 short bullets on what the table likely represents, what it can support in KPI work, and any caution for downstream modeling

---

## Step 6 — Merge Enrichment Back Into The Same YAML

Rewrite every file in `{sources_paths}` in place.

Merge rules:
- Preserve all existing user-authored keys at root, source, table, and column level.
- Never overwrite existing `description`, `tests`, `meta`, `tags`, or unknown custom keys.
- Update only generated fields.
- If a table already has a `columns` list, match existing columns by exact `name`.
- If a warehouse column is missing from the YAML, add it in warehouse ordinal order.
- If a previous run left generated fields, replace them with fresh values rather than duplicating them.
- If a column is now marked `pii: true`, remove any previously stored `sample_values`.
- If a column already had a user-authored `pii` or `pii_reason`, preserve that authored value and avoid replacing it with a heuristic one.

Generated table-level fields:
- `row_count`
- `candidate_primary_keys`
- `candidate_join_keys`
- `date_columns`
- `anomalies`
- `llm_notes`

Generated column-level fields:
- `data_type`
- `pii`
- `pii_reason`
- `null_rate`
- `cardinality`
- `sample_values`
- `join_key_candidate`
- `date_format`
- `notes`

Reformatting the YAML is acceptable.
Dropping user-authored content is not.

If structured editing is easier, use an inline `python3 -c` snippet or direct file editing.
Do not create a reusable helper script for this command.

---

## Step 7 — Completion Summary

Print a completion summary:

```text
✓ me_goals.md:      {me_goals_path}
✓ dbt repo:         {dbt_repo_path}
✓ profile file:     {profiles_path}
✓ tunnel port:      {tunnel_port}
✓ source YAML files: {sources_paths}
✓ source files:     {sources_file_count}
✓ sources profiled: {source_count}
✓ tables profiled:  {table_count}
```

Then print:
- "Review the inferred PII flags and data-quality notes in the enriched YAML files."
- "Next → run `/curate_metrics` using `me_goals.md` and the enriched source YAML files."

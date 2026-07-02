# /explore_data — Raw Warehouse Exploration

Profiles the raw tables listed in a passed `source.yml` or `sources.yml` file and enriches that same YAML in place.
Use this after `/discover`, once the raw data has been ingested and the consultant is ready to understand the real warehouse shape before KPI design.

Treat the text after `/explore_data` as the candidate path to the YAML file.
Run through each step in order. Do not skip validation. Stop immediately on blocking errors instead of guessing.

---

## Step 0 — Resolve And Validate The Source YAML

If the user passed a path after `/explore_data`, treat that as `{sources_path}`.

If no path was provided, ask:
> "What is the path to the `source.yml` or `sources.yml` file you want to enrich?"

Validate:
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

If parsing fails or the structure is missing `sources`, stop and show the exact issue.
Do not rewrite the file yet.

Store:
- `{sources_path}`
- `{sources_yaml}`

---

## Step 1 — Resolve `me_goals.md`

Prefer deriving the engagement context automatically.

Try, in this order:

1. **If `{sources_path}` is inside `workdocs/consulting/{engagement}/...`:**
   - Derive `{engagement}` from the path.
   - Set `{me_goals_path}` to:
     `workdocs/consulting/{engagement}/discovery/me_goals.md`

2. **If `{sources_path}` is inside a dbt repo:**
   - Walk upward from `{sources_path}` until you find a directory containing `dbt_project.yml`.
   - Store that directory as `{candidate_dbt_repo}`.
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

## Step 2 — Resolve The dbt Repo

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

Store:
- `{dbt_repo_path}`

---

## Step 3 — Resolve The Profile And Verify Connectivity

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

## Step 4 — Profile Each Source Table

For each source in `{sources_yaml.sources}`:
- Read the source-level `schema`
- Respect an explicit `database` if present

For each table:
- Use `identifier` when present; otherwise use `name`
- Resolve the physical table as `{schema}.{identifier_or_name}`

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
- capture up to 5 distinct non-null sample values for non-PII columns only
- do not dump full rows unless needed to understand a table anomaly

### PII Inference Rules

Infer `pii: true` heuristically from column names, existing descriptions, and limited pattern checks where needed.

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

For every column marked PII:
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

## Step 5 — Merge Enrichment Back Into The Same YAML

Rewrite `{sources_path}` in place.

Merge rules:
- Preserve all existing user-authored keys at root, source, table, and column level.
- Never overwrite existing `description`, `tests`, `meta`, `tags`, or unknown custom keys.
- Update only generated fields.
- If a table already has a `columns` list, match existing columns by exact `name`.
- If a warehouse column is missing from the YAML, add it in warehouse ordinal order.
- If a previous run left generated fields, replace them with fresh values rather than duplicating them.
- If a column is now marked `pii: true`, remove any previously stored `sample_values`.

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

## Step 6 — Completion Summary

Print a completion summary:

```text
✓ me_goals.md:      {me_goals_path}
✓ dbt repo:         {dbt_repo_path}
✓ profile file:     {profiles_path}
✓ source YAML:      {sources_path}
✓ sources profiled: {source_count}
✓ tables profiled:  {table_count}
```

Then print:
- "Review the inferred PII flags and data-quality notes in `{sources_path}`."
- "Next → run `/curate_metrics` using `me_goals.md` and the enriched source YAML."

---
name: validate-warehouse-access
description: "Shared warehouse access validation for Dalgo dbt workflows. Use before profiling, investigation, dbt validation, or any skill that needs warehouse queries through a dbt profile."
---

# Validate Warehouse Access

Use this skill whenever a Dalgo workflow needs to query the warehouse or run dbt operations that depend on a profile.

## Inputs

- `{dbt_repo_path}` — local path to the dbt repo
- `{profiles_path}` — optional explicit dbt profile file
- `{profiles_dir}` — optional explicit profiles directory
- `{tunnel_port}` — optional local tunnel port; default `5432`
- `{allow_no_tunnel}` — optional boolean when the warehouse is not reached through a local tunnel
- `{warehouse_read_confirmed}` — optional boolean from a caller that already asked the required warehouse-read question during the same skill run

## Steps

1. Before reading warehouse schemas/tables, validating physical table access, running schema introspection, or running dbt commands that query the warehouse, confirm `{warehouse_read_confirmed}` is true. If it is not already true, ask the user exactly:
   > "Can I read your database schema tables?"
   Continue only after the user confirms, then set `{warehouse_read_confirmed} = true`. If the user declines or does not answer, stop and report that warehouse access was not approved.
2. Ask the user to confirm any required SSH tunnel is running and capture the local port. Use `5432` as the default; allow `none` when no tunnel is needed.
3. Resolve the dbt profile file in this order:
   - `{dbt_repo_path}/profiles.yml`
   - `{dbt_repo_path}/profiles.yaml`
   - `~/.dbt/profiles.yml`
4. Read the dbt profile name from `{dbt_repo_path}/dbt_project.yml`.
5. Resolve the active target and required environment variables.
6. Run:

```bash
dbt debug --project-dir "{dbt_repo_path}" --profiles-dir "{profiles_dir}" --log-path "/tmp/dalgo-dbt-debug-logs"
```

7. Confirm the active adapter is Postgres-compatible for v1.
8. Return safe connection context to the caller:
   - profile name
   - target name
   - adapter type
   - database
   - schema
   - redacted host and port
   - profile/profiles directory used
   - whether dbt debug passed

## Credential Handling

Never print, copy, summarize, or write raw `profiles.yml` / `profiles.yaml` contents.

Never print resolved passwords, tokens, private keys, usernames, or environment variable values.

If an error message includes credentials, redact it before showing it to the user or writing artifacts.

If the resolved warehouse host is local and `{tunnel_port}` is not `none`, compare the resolved profile port with `{tunnel_port}`. Stop with a clear blocker if they do not match.

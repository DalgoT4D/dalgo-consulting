---
name: github-delivery
description: "Shared explicit GitHub delivery gate for Dalgo consulting and dbt repo changes. Use after successful validation when a repo has a GitHub remote and the user may want a branch, push, or PR."
---

# GitHub Delivery

Use this skill only after implementation and validation have succeeded.

## Inputs

- `{repo_path}` — repository to inspect and optionally deliver
- `{intended_files}` — files that may be staged
- `{branch_name}` — optional proposed branch
- `{commit_message}` — optional proposed commit message
- `{pr_base}` — optional base branch, default `main`

## Steps

1. Run:

```bash
git -C "{repo_path}" status --short --branch
git -C "{repo_path}" remote -v
```

2. If no GitHub remote exists, report that GitHub delivery is unavailable and stop.
3. If there are unrelated dirty changes, do not stage or revert them. Ask the user how to handle them.
4. Ask:

```text
Should I commit and push these changes to GitHub? (yes / no)
```

5. If the answer is not clearly yes, stop and record delivery as skipped.
6. Create or switch to a dedicated branch.
7. Stage only `{intended_files}` plus required generated metadata/artifacts explicitly tied to the work.
8. Commit with a concise message tied to the change request, investigation, or phase.
9. Push the branch.
10. Ask whether to open a PR against `{pr_base}`. Open it only after confirmation.

Never commit, push, or open a PR without explicit user confirmation.
Never stage unrelated files.

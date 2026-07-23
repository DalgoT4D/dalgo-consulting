# /generate_er_diagram — Generate The Entity Relationship Diagram

Creates `er_diagram.md` from `me_goals.md`, the KPI Framework, `dbt_plan.md`, and enriched source YAMLs.
Use this after `/dbt_plan`.

The ER diagram should reflect the planned dbt architecture, not only the raw source shape.

Treat the text after `/generate_er_diagram` as optional source YAML paths.

---

## Step 0 — Resolve Inputs

Resolve `{engagement}` using the same rules as `/dbt_plan`.

Validate:
- `workdocs/consulting/{engagement}/discovery/me_goals.md` exists.
- `workdocs/consulting/{engagement}/framework/dbt_plan.md` exists.
- `workdocs/consulting/{engagement}/framework/phase3_metadata.json` exists or the user can provide a KPI Framework Sheet URL.
- Relevant enriched source YAML files exist.

Invoke the `read_kpi_framework` skill to refresh:

```text
workdocs/consulting/{engagement}/framework/kpi_framework.md
workdocs/consulting/{engagement}/framework/kpi_framework.json
```

Read fully:
- `me_goals.md`
- `kpi_framework.md`
- `kpi_framework.json`
- `dbt_plan.md`
- all source YAML files

---

## Step 1 — Identify Entities And Grains

From the KPI Framework and dbt plan, identify:

- source entities
- staging models
- intermediate entities
- final `marts_` models
- each entity/model grain
- primary keys
- foreign keys
- candidate join keys
- cardinality expectations

Prefer business names where useful, but include model names so the diagram can guide implementation.

---

## Step 2 — Map KPIs And Visuals To Join Paths

For every KPI and major visual, document:

- KPI or visual ID
- model(s) that serve it
- required filter and drilldown columns
- required filters/drilldowns
- join path
- grain assumptions
- risk of fan-out or row loss

If a join path is uncertain, put it in Open Questions rather than drawing it as confirmed.

---

## Step 3 — Write Mermaid ER Diagram

Generate Mermaid in `erDiagram` format for core entity relationships.

Use:
- `||--o{` for one-to-many
- `||--||` for one-to-one
- `}o--o{` only when many-to-many is unavoidable, and explain how dbt will resolve it

Include key columns and important filter/drilldown columns in each entity block.

Do not include raw PII sample values. Column names may be shown when necessary.

---

## Step 4 — Write `er_diagram.md`

Write:

```text
workdocs/consulting/{engagement}/framework/er_diagram.md
```

Use this structure:

```markdown
# ER Diagram — {engagement_display}

## Inputs Reviewed
## Mermaid ER Diagram
## Entity And Grain Notes
## Source-To-Model Mapping
## KPI And Visual Join Paths
## Filter And Drilldown Support
## Cardinality Risks
## Assumptions And Open Questions
```

---

## Step 5 — Update Metadata

Update `workdocs/consulting/{engagement}/framework/phase3_metadata.json` with:

```json
{
  "local_artifacts": {
    "er_diagram": "workdocs/consulting/{engagement}/framework/er_diagram.md"
  }
}
```

Preserve existing keys.

---

## Step 6 — Completion Summary

Print:

```text
✓ KPI Framework:  workdocs/consulting/{engagement}/framework/kpi_framework.md
✓ dbt plan:       workdocs/consulting/{engagement}/framework/dbt_plan.md
✓ ER diagram:     workdocs/consulting/{engagement}/framework/er_diagram.md
✓ open questions: {open_question_count}
```

Then print:
> "Phase 3 is complete once the KPI Framework, dbt plan, and ER diagram have been reviewed."

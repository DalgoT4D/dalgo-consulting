#!/usr/bin/env python3
"""
kpi_framework_sheet.py — Create, write, and read Dalgo KPI Framework Sheets.

Usage:
    python3 scripts/kpi_framework_sheet.py create --title "KPI Framework - GiveDo"
    python3 scripts/kpi_framework_sheet.py write --sheet-id SHEET_ID --input-json kpi_framework.json
    python3 scripts/kpi_framework_sheet.py read --sheet-id SHEET_ID --format markdown

The JSON shape for write/read is:
{
  "KPI Catalog": [{...}],
  "Dashboard Outputs": [{...}],
  ...
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]
DEFAULT_KEY_FILE = Path(__file__).parent.parent / "secrets" / "my_service_key.json"

TABS: dict[str, list[str]] = {
    "KPI Catalog": [
        "kpi_id",
        "kpi_name",
        "program",
        "outcome_area",
        "requirements_alignment",
        "plain_english_definition",
        "calculation_logic",
        "numerator_logic",
        "denominator_logic",
        "source_tables",
        "required_columns",
        "filters_conditions",
        "grain",
        "time_grain",
        "breakdown_dimensions",
        "mart_model",
        "status",
        "change_request_id",
        "change_reason",
        "changed_at",
        "open_questions",
    ],
    "Dashboard Outputs": [
        "dashboard_id",
        "dashboard_name",
        "program",
        "audience",
        "decision_supported",
        "cadence",
        "primary_kpis",
        "required_filters",
        "required_drilldowns",
        "change_request_id",
        "change_reason",
        "changed_at",
        "notes",
    ],
    "Charts & Visuals": [
        "visual_id",
        "dashboard_id",
        "visual_title",
        "visual_type",
        "kpi_ids",
        "program",
        "x_axis_or_grouping",
        "y_metric",
        "series_or_color_dimension",
        "required_dimensions",
        "sort_logic",
        "default_time_window",
        "grain_needed",
        "mart_model",
        "change_request_id",
        "change_reason",
        "changed_at",
        "notes",
    ],
    "Filters & Drilldowns": [
        "filter_or_drilldown_id",
        "label",
        "type",
        "applies_to_dashboards",
        "applies_to_visuals",
        "source_column",
        "canonical_dimension_model",
        "allowed_values_logic",
        "default_value",
        "required_for_all_charts",
        "change_request_id",
        "change_reason",
        "changed_at",
        "notes",
    ],
    "Alerts": [
        "alert_id",
        "kpi_id",
        "program",
        "alert_condition",
        "threshold",
        "comparison_period",
        "recipient_or_audience",
        "cadence",
        "required_grain",
        "mart_model",
        "change_request_id",
        "change_reason",
        "changed_at",
        "notes",
    ],
    "Open Questions": [
        "question_id",
        "related_kpi_or_visual",
        "question",
        "why_it_matters",
        "suggested_default",
        "owner",
        "status",
    ],
}


def get_services(key_file: Path):
    creds = service_account.Credentials.from_service_account_file(str(key_file), scopes=SCOPES)
    sheets = build("sheets", "v4", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    return sheets, drive


def spreadsheet_url(sheet_id: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"


def get_sheet_titles(sheets, sheet_id: str) -> dict[str, int]:
    meta = sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
    return {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta.get("sheets", [])}


def ensure_tabs(sheets, sheet_id: str) -> dict[str, int]:
    titles = get_sheet_titles(sheets, sheet_id)
    requests: list[dict[str, Any]] = []

    first_existing_title = next(iter(titles), None)
    if first_existing_title == "Sheet1" and "KPI Catalog" not in titles:
        requests.append(
            {
                "updateSheetProperties": {
                    "properties": {"sheetId": titles["Sheet1"], "title": "KPI Catalog"},
                    "fields": "title",
                }
            }
        )
        titles["KPI Catalog"] = titles.pop("Sheet1")

    for title in TABS:
        if title not in titles:
            requests.append({"addSheet": {"properties": {"title": title}}})

    if requests:
        sheets.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={"requests": requests},
        ).execute()
        titles = get_sheet_titles(sheets, sheet_id)

    return titles


def format_tabs(sheets, sheet_id: str, sheet_ids: dict[str, int]) -> None:
    requests = []
    for title, headers in TABS.items():
        requests.extend(
            [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_ids[title],
                            "gridProperties": {"frozenRowCount": 1},
                        },
                        "fields": "gridProperties.frozenRowCount",
                    }
                },
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_ids[title],
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": len(headers),
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {"bold": True},
                                "backgroundColor": {"red": 0.89, "green": 0.93, "blue": 1.0},
                            }
                        },
                        "fields": "userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.bold",
                    }
                },
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_ids[title],
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": len(headers),
                        }
                    }
                },
            ]
        )

    sheets.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={"requests": requests}).execute()


def write_headers(sheets, sheet_id: str) -> None:
    data = [{"range": f"'{title}'!A1", "values": [headers]} for title, headers in TABS.items()]
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sheet_id,
        body={"valueInputOption": "RAW", "data": data},
    ).execute()


def create_spreadsheet(sheets, drive, title: str, share_with: list[str], metadata_output: Path | None) -> None:
    spreadsheet = (
        sheets.spreadsheets()
        .create(body={"properties": {"title": title}, "sheets": [{"properties": {"title": "KPI Catalog"}}]})
        .execute()
    )
    sheet_id = spreadsheet["spreadsheetId"]
    sheet_ids = ensure_tabs(sheets, sheet_id)
    write_headers(sheets, sheet_id)
    format_tabs(sheets, sheet_id, sheet_ids)

    for email in share_with:
        if email:
            drive.permissions().create(
                fileId=sheet_id,
                body={"type": "user", "role": "writer", "emailAddress": email},
                fields="id",
                sendNotificationEmail=False,
            ).execute()

    result = {"spreadsheet_id": sheet_id, "url": spreadsheet_url(sheet_id), "tabs": list(TABS)}
    if metadata_output:
        existing = {}
        if metadata_output.exists():
            try:
                existing = json.loads(metadata_output.read_text())
            except json.JSONDecodeError:
                existing = {}
        existing["kpi_framework_sheet"] = {
            "spreadsheet_id": sheet_id,
            "url": spreadsheet_url(sheet_id),
            "tabs": list(TABS),
        }
        metadata_output.parent.mkdir(parents=True, exist_ok=True)
        metadata_output.write_text(json.dumps(existing, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def coerce_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def rows_for_tab(input_data: dict[str, Any], tab: str) -> list[list[str]]:
    headers = TABS[tab]
    rows = input_data.get(tab, [])
    if not isinstance(rows, list):
        raise ValueError(f"{tab} must be a list of row objects")

    values = [headers]
    for row in rows:
        if isinstance(row, dict):
            values.append([coerce_cell(row.get(header, "")) for header in headers])
        elif isinstance(row, list):
            values.append([coerce_cell(v) for v in row])
        else:
            raise ValueError(f"{tab} row must be an object or list")
    return values


def write_spreadsheet(sheets, sheet_id: str, input_json: Path) -> None:
    input_data = json.loads(input_json.read_text())
    ensure_tabs(sheets, sheet_id)

    data = []
    for tab in TABS:
        values = rows_for_tab(input_data, tab)
        end_col = chr(ord("A") + len(TABS[tab]) - 1)
        sheets.spreadsheets().values().clear(spreadsheetId=sheet_id, range=f"'{tab}'!A:ZZ").execute()
        data.append({"range": f"'{tab}'!A1:{end_col}{len(values)}", "values": values})

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sheet_id,
        body={"valueInputOption": "USER_ENTERED", "data": data},
    ).execute()
    format_tabs(sheets, sheet_id, get_sheet_titles(sheets, sheet_id))
    print(json.dumps({"spreadsheet_id": sheet_id, "url": spreadsheet_url(sheet_id), "written_tabs": list(TABS)}, indent=2))


def normalise_rows(values: list[list[str]], tab: str) -> list[dict[str, str]]:
    headers = TABS[tab]
    if values:
        sheet_headers = values[0]
        if sheet_headers:
            headers = sheet_headers

    output = []
    for row in values[1:]:
        padded = row + [""] * (len(headers) - len(row))
        record = {headers[i]: padded[i] for i in range(len(headers))}
        if any(str(value).strip() for value in record.values()):
            output.append(record)
    return output


def read_spreadsheet(sheets, sheet_id: str) -> dict[str, list[dict[str, str]]]:
    output = {}
    for tab in TABS:
        result = (
            sheets.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"'{tab}'", valueRenderOption="FORMATTED_VALUE")
            .execute()
        )
        output[tab] = normalise_rows(result.get("values", []), tab)
    return output


def markdown_table(rows: list[dict[str, str]], headers: list[str]) -> str:
    def clean(value: str) -> str:
        return str(value).replace("\n", "<br>").replace("|", "\\|")

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(clean(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def to_markdown(data: dict[str, list[dict[str, str]]]) -> str:
    sections = ["# KPI Framework"]
    for tab, headers in TABS.items():
        rows = data.get(tab, [])
        sections.append(f"## {tab}\n\n{markdown_table(rows, headers) if rows else '_No rows_'}")
    return "\n\n".join(sections) + "\n"


def read_command(sheets, sheet_id: str, output_format: str, output: Path | None) -> None:
    data = read_spreadsheet(sheets, sheet_id)
    rendered = json.dumps(data, indent=2, ensure_ascii=False) + "\n" if output_format == "json" else to_markdown(data)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered)
    print(rendered, end="")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create, write, and read Dalgo KPI Framework Sheets.")
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a new KPI Framework Sheet.")
    create.add_argument("--title", required=True)
    create.add_argument("--share-with", action="append", default=[])
    create.add_argument("--metadata-output", type=Path)

    write = subparsers.add_parser("write", help="Write KPI Framework JSON rows to an existing sheet.")
    write.add_argument("--sheet-id", required=True)
    write.add_argument("--input-json", type=Path, required=True)

    read = subparsers.add_parser("read", help="Read an existing KPI Framework Sheet.")
    read.add_argument("--sheet-id", required=True)
    read.add_argument("--format", choices=["markdown", "json"], default="markdown")
    read.add_argument("--output", type=Path)

    args = parser.parse_args()

    try:
        sheets, drive = get_services(args.key_file)
        if args.command == "create":
            create_spreadsheet(sheets, drive, args.title, args.share_with, args.metadata_output)
        elif args.command == "write":
            write_spreadsheet(sheets, args.sheet_id, args.input_json)
        elif args.command == "read":
            read_command(sheets, args.sheet_id, args.format, args.output)
    except FileNotFoundError:
        print(f"ERROR: Key file not found at {args.key_file}", file=sys.stderr)
        sys.exit(1)
    except HttpError as exc:
        print(f"ERROR: Google API request failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

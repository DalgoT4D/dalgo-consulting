#!/usr/bin/env python3
"""
read_requirements.py — Read all content tabs from a Dalgo consulting Requirements Sheet.

Prints structured markdown to stdout. The LLM consumes this output to synthesise me_goals.md.

Usage:
    python3 read_requirements.py --sheet-id SPREADSHEET_ID [--key-file PATH]

The sheet must be shared (Editor) with the service account in the key file.
Tabs read: Engagement Context, Data Sources, Metrics (Instructions tab is skipped).
"""

import argparse
import json
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
DEFAULT_KEY_FILE = Path(__file__).parent.parent / "secrets" / "my_service_key.json"

TABS_TO_READ = ["Engagement Context", "Data Sources", "Metrics"]


def get_client_email(key_file: str) -> str:
    with open(key_file) as f:
        return json.load(f).get("client_email", "unknown")


def get_service(key_file: str):
    creds = service_account.Credentials.from_service_account_file(key_file, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def read_tab(service, sheet_id: str, tab_name: str) -> list[list[str]]:
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=tab_name,
        valueRenderOption="FORMATTED_VALUE",
    ).execute()
    return result.get("values", [])


def rows_to_markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return "_No data_"

    # Normalise row widths
    width = max(len(r) for r in rows)
    normalised = [r + [""] * (width - len(r)) for r in rows]

    header = normalised[0]
    separator = ["---"] * width
    body = normalised[1:]

    def fmt_row(cells):
        return "| " + " | ".join(cells) + " |"

    lines = [fmt_row(header), fmt_row(separator)]
    lines += [fmt_row(row) for row in body if any(cell.strip() for cell in row)]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Read Dalgo consulting Requirements Sheet tabs.")
    parser.add_argument("--sheet-id", required=True, help="Google Spreadsheet ID.")
    parser.add_argument(
        "--key-file",
        default=str(DEFAULT_KEY_FILE),
        help="Path to service account JSON key (default: secrets/my_service_key.json).",
    )
    args = parser.parse_args()

    try:
        service = get_service(args.key_file)
    except FileNotFoundError:
        print(f"ERROR: Key file not found at {args.key_file}", file=sys.stderr)
        sys.exit(1)

    output_sections = []

    for tab in TABS_TO_READ:
        try:
            rows = read_tab(service, args.sheet_id, tab)
            table = rows_to_markdown_table(rows)
            output_sections.append(f"## {tab}\n\n{table}")
        except HttpError as e:
            if e.status_code == 403:
                email = get_client_email(args.key_file)
                print(
                    f"ERROR 403: Cannot read sheet. Share it (Editor) with: {email}",
                    file=sys.stderr,
                )
                sys.exit(1)
            elif e.status_code == 400:
                # Tab might not exist yet (e.g. Data Sources not yet filled)
                output_sections.append(f"## {tab}\n\n_Tab not found or empty — may not be filled yet._")
            else:
                print(f"ERROR reading tab '{tab}': {e}", file=sys.stderr)
                sys.exit(1)

    print("\n\n".join(output_sections))


if __name__ == "__main__":
    main()

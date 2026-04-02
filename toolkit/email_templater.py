"""
Email Template Engine — GridGuard AI Python Automation Toolkit

Mail-merge engine: load a template with {{placeholders}}, fill from CSV data,
and output personalized emails to files or stdout. Does NOT send emails.

Usage:
    python -m toolkit.email_templater --template TEMPLATE --data CSV --output DIR
    python -m toolkit.email_templater --template TEMPLATE --data CSV --preview 5
"""

import argparse
import csv
import os
import re
import sys
from typing import Dict, List, Set


PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")


def load_template(path):
    # type: (str) -> str
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_csv_data(path):
    # type: (str) -> List[Dict[str, str]]
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_placeholders(template):
    # type: (str) -> Set[str]
    return set(PLACEHOLDER_RE.findall(template))


def render(template, row, row_index):
    # type: (str, Dict[str, str], int) -> str
    """Replace {{key}} placeholders with values from row dict."""
    def replacer(match):
        key = match.group(1)
        if key in row:
            return row[key]
        sys.stderr.write("  [warn] Row {}: missing value for '{{{{{}}}}}'\n".format(row_index, key))
        return match.group(0)

    return PLACEHOLDER_RE.sub(replacer, template)


def validate_columns(placeholders, columns, template_path):
    # type: (Set[str], List[str], str) -> None
    missing = placeholders - set(columns)
    if missing:
        sys.stderr.write("[warn] Template '{}' uses placeholders not found in CSV: {}\n".format(
            template_path, missing))


def generate_filename(row, index):
    # type: (Dict[str, str], int) -> str
    """Generate a safe filename from the row data."""
    name_fields = ["email", "name", "first_name", "id", "username"]
    for field in name_fields:
        if field in row and row[field].strip():
            safe = re.sub(r'[^\w\-.]', '_', row[field].strip())
            return "{}.txt".format(safe)
    return "email_{:04d}.txt".format(index + 1)


def main():
    parser = argparse.ArgumentParser(
        description="Email template engine with CSV mail-merge (preview only, does NOT send)."
    )
    parser.add_argument("--template", required=True, help="Path to email template file")
    parser.add_argument("--data", required=True, help="Path to CSV file with recipient data")
    parser.add_argument("--output", default=None,
                        help="Output directory for generated emails (omit to print to stdout)")
    parser.add_argument("--preview", type=int, default=0,
                        help="Print first N emails to stdout instead of writing files")

    args = parser.parse_args()

    template = load_template(args.template)
    rows = load_csv_data(args.data)

    if not rows:
        print("[templater] No data rows found in CSV.")
        sys.exit(1)

    placeholders = get_placeholders(template)
    columns = list(rows[0].keys())

    print("[templater] Template: {}".format(args.template))
    print("[templater] Data: {} ({} rows)".format(args.data, len(rows)))
    print("[templater] Placeholders: {}".format(placeholders))

    validate_columns(placeholders, columns, args.template)

    # Preview mode
    if args.preview > 0:
        count = min(args.preview, len(rows))
        print("\n[templater] Previewing {} email(s):\n".format(count))
        for i in range(count):
            rendered = render(template, rows[i], i)
            print("=" * 60)
            print("  Email {} / {}".format(i + 1, len(rows)))
            print("=" * 60)
            print(rendered)
            print()
        return

    # Output mode
    if args.output:
        os.makedirs(args.output, exist_ok=True)
        for i, row in enumerate(rows):
            rendered = render(template, row, i)
            filename = generate_filename(row, i)
            filepath = os.path.join(args.output, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(rendered)
        print("\n[templater] Generated {} email(s) in {}/".format(len(rows), args.output))
    else:
        for i, row in enumerate(rows):
            rendered = render(template, row, i)
            print("=" * 60)
            print("  Email {} / {}".format(i + 1, len(rows)))
            print("=" * 60)
            print(rendered)
            print()
        print("[templater] {} email(s) rendered.".format(len(rows)))


if __name__ == "__main__":
    main()

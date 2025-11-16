#!/usr/bin/env python3
"""
Lightweight JSONL viewer for backlog inspection.

Reads newline-delimited JSON, flattens selected fields (supports dotted paths
like `extraction.method`), and prints an ASCII table to stdout.

Example:
    python examples/view_jsonl.py --file ../backlog.jsonl \
        --fields article_id title domain extraction.method extraction.text_length
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path
from typing import Any, Iterable, List


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    default_file = Path(__file__).resolve().parents[1] / "backlog.jsonl"
    parser = argparse.ArgumentParser(description="Pretty-print JSONL files as a table.")
    parser.add_argument(
        "--file",
        type=Path,
        default=default_file,
        help=f"JSONL file to read (default: {default_file})",
    )
    parser.add_argument(
        "--fields",
        nargs="+",
        default=[
            "article_id",
            "title",
            "domain",
            "extraction.method",
            "extraction.text_length",
            "error",
        ],
        help="Fields (dot paths allowed) to display as columns.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of rows to display (default: 20).",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Skip the first N rows before displaying (default: 0).",
    )
    parser.add_argument(
        "--wrap",
        type=int,
        default=60,
        help="Wrap long text to this many characters per line (default: 60).",
    )
    parser.add_argument(
        "--failed-only",
        action="store_true",
        help="Only show rows where `error` is present or extraction is missing.",
    )
    parser.add_argument(
        "--success-only",
        action="store_true",
        help="Only show rows where extraction succeeded.",
    )
    return parser.parse_args(argv)


def read_jsonl(path: Path) -> List[Any]:
    if not path.exists():
        raise FileNotFoundError(f"JSONL file not found: {path}")
    rows: List[Any] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_no}: {exc}") from exc
    return rows


def extract_field(data: Any, field: str) -> Any:
    current = data
    for part in field.split("."):
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def normalize_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def wrap_value(value: str, width: int) -> str:
    if not width or not value:
        return value
    lines: List[str] = []
    for paragraph in value.splitlines():
        if not paragraph.strip():
            lines.append(paragraph)
            continue
        lines.extend(textwrap.wrap(paragraph, width=width) or [""])
    return "\n".join(lines)


def filter_rows(rows: List[Any], only_failed: bool, only_success: bool) -> List[Any]:
    if only_failed and only_success:
        raise ValueError("Cannot combine --failed-only and --success-only.")
    if not (only_failed or only_success):
        return rows

    filtered: List[Any] = []
    for row in rows:
        extraction = row.get("extraction") if isinstance(row, dict) else None
        error = row.get("error") if isinstance(row, dict) else None
        success = bool(extraction) and not error
        if only_success and success:
            filtered.append(row)
        elif only_failed and not success:
            filtered.append(row)
    return filtered


def compute_widths(table: List[List[str]], headers: List[str]) -> List[int]:
    widths = [len(header) for header in headers]
    for row in table:
        for idx, cell in enumerate(row):
            cell_lines = cell.splitlines() or [""]
            widths[idx] = max(widths[idx], *(len(line) for line in cell_lines))
    return widths


def print_separator(widths: List[int]) -> None:
    segments = ["-" * (w + 2) for w in widths]
    print("+" + "+".join(segments) + "+")


def print_row(row: List[str], widths: List[int]) -> None:
    line_groups = [cell.splitlines() or [""] for cell in row]
    max_lines = max(len(lines) for lines in line_groups)
    for line_idx in range(max_lines):
        rendered_cells = []
        for col_idx, lines in enumerate(line_groups):
            text = lines[line_idx] if line_idx < len(lines) else ""
            rendered_cells.append(text.ljust(widths[col_idx]))
        print("| " + " | ".join(rendered_cells) + " |")


def print_table(table: List[List[str]], headers: List[str]) -> None:
    widths = compute_widths(table, headers)
    print_separator(widths)
    print_row(headers, widths)
    print_separator(widths)
    for row in table:
        print_row(row, widths)
        print_separator(widths)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        rows = read_jsonl(args.file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    filtered_rows = filter_rows(rows, args.failed_only, args.success_only)
    window = filtered_rows[args.offset : args.offset + args.limit]

    if not window:
        print("No rows to display (check filters/offset).")
        return 0

    table: List[List[str]] = []
    for record in window:
        cells = []
        for field in args.fields:
            raw_value = extract_field(record, field)
            normalized = normalize_value(raw_value)
            wrapped = wrap_value(normalized, args.wrap)
            cells.append(wrapped)
        table.append(cells)

    print_table(table, headers=args.fields)

    success_count = sum(1 for row in filtered_rows if row.get("extraction"))
    print(
        f"\nDisplayed {len(window)} / {len(filtered_rows)} rows "
        f"(success={success_count}, failed={len(filtered_rows) - success_count})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

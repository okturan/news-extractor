#!/usr/bin/env python3
"""
Bridge script: reuse the Haber-in Dibi extractor on URLs that already exist
inside the News Gatherer SQLite database so we can inspect full-text results.

Usage (from the haberin-dibi project root, after `poetry install`):

    poetry run python examples/scrape_news_gatherer_backlog.py \
        --db ../news-gatherer/output/news-gatherer.db \
        --limit 25 \
        --format json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if SRC_PATH.exists():
    sys.path.insert(0, str(SRC_PATH))

from haberin_dibi import ArticleExtractor


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Haber-in Dibi on the existing News Gatherer URLs."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "news-gatherer" / "output" / "news-gatherer.db",
        help="Path to news-gatherer SQLite file (default: ../news-gatherer/output/news-gatherer.db).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="How many rows to pull from the articles table (default: 20).",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Start offset when scanning the articles table (default: 0).",
    )
    parser.add_argument(
        "--min-text-length",
        type=int,
        default=100,
        help="Minimum characters to accept an extraction (default: 100).",
    )
    parser.add_argument(
        "--format",
        choices=["json", "pretty"],
        default="pretty",
        help="json = newline-delimited JSON, pretty = human readable (default: pretty).",
    )
    return parser.parse_args(argv)


def fetch_articles(db_path: Path, limit: int, offset: int) -> List[sqlite3.Row]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute(
            """
            SELECT id, url, canonical_url, title, domain, stored_at
            FROM articles
            ORDER BY stored_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def run_extractions(rows: List[sqlite3.Row], min_text_length: int) -> List[Dict[str, Any]]:
    extractor = ArticleExtractor(min_text_length=min_text_length)
    results: List[Dict[str, Any]] = []

    for row in rows:
        payload: Dict[str, Any] = {
            "article_id": row["id"],
            "canonical_url": row["canonical_url"],
            "source_url": row["url"],
            "title": row["title"],
            "domain": row["domain"],
            "stored_at": row["stored_at"],
        }

        article: Optional[Dict[str, Any]] = None
        error: Optional[str] = None
        try:
            article = extractor.extract(row["url"])
        except Exception as exc:  # Surface unexpected extraction failures
            error = f"{type(exc).__name__}: {exc}"

        payload["extraction"] = article
        payload["error"] = error
        results.append(payload)
    return results


def print_pretty(results: List[Dict[str, Any]]) -> None:
    for entry in results:
        print("=" * 100)
        print(f"[{entry['article_id']}] {entry['title']} ({entry['domain']})")
        print(f"URL: {entry['source_url']}")
        print(f"Canonical: {entry['canonical_url']}")
        extraction = entry["extraction"]

        if extraction:
            print(f"Method: {extraction['method']}")
            print(f"Text length: {extraction['text_length']}")
            keywords = ", ".join(extraction.get("keywords") or []) or "N/A"
            print(f"Keywords: {keywords}")
            preview = (extraction.get("text") or "")[:280]
            print("-" * 100)
            print(preview + ("..." if len(preview) == 280 else ""))
        else:
            print("Extraction: ❌")
            if entry["error"]:
                print(f"Error: {entry['error']}")
        print()


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.db.exists():
        print(f"Database not found: {args.db}", file=sys.stderr)
        return 2

    rows = fetch_articles(args.db, args.limit, args.offset)
    if not rows:
        print("No rows returned from the articles table.", file=sys.stderr)
        return 1

    results = run_extractions(rows, args.min_text_length)

    if args.format == "json":
        for entry in results:
            print(json.dumps(entry, ensure_ascii=False))
    else:
        print_pretty(results)

    successes = sum(1 for entry in results if entry["extraction"])
    print(f"\nSummary: {successes}/{len(results)} extractions succeeded "
          f"({successes / len(results) * 100:.1f}% with min_text_length={args.min_text_length}).")
    return 0 if successes else 3


if __name__ == "__main__":
    raise SystemExit(main())

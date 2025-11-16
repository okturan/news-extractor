from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any, Dict, Iterable

from .article_extractor import ArticleExtractor

logger = logging.getLogger(__name__)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Turkish news articles via Newspaper4k → Trafilatura fallback strategy."
    )
    parser.add_argument("urls", nargs="+", help="One or more article URLs to extract.")
    parser.add_argument(
        "--min-text-length",
        type=int,
        default=100,
        help="Minimum number of characters required to accept an extraction (default: 100)."
    )
    parser.add_argument(
        "--format",
        choices=["pretty", "json"],
        default="pretty",
        help="Output format for extracted articles (default: pretty)."
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging verbosity for diagnostics (default: INFO).",
    )
    return parser.parse_args(argv)


def _print_pretty(url: str, article: Dict[str, Any]) -> None:
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Method: {article['method']}")
    print(f"Title: {article['title']}")
    authors = ", ".join(article["authors"]) if article.get("authors") else "N/A"
    print(f"Authors: {authors}")
    print(f"Date: {article.get('date')}")
    keywords = ", ".join(article.get("keywords", [])[:5]) or "N/A"
    print(f"Keywords: {keywords}")
    print(f"Text length: {article['text_length']} chars")
    print("-" * 80)
    preview = (article.get("text") or "")[:300]
    print(preview + ("..." if preview else ""))
    print()


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s:%(name)s:%(message)s",
    )
    extractor = ArticleExtractor(min_text_length=args.min_text_length)

    successes = 0
    for url in args.urls:
        article = extractor.extract(url)
        if article:
            successes += 1
            if args.format == "json":
                print(json.dumps(article, ensure_ascii=False, indent=2))
            else:
                _print_pretty(url, article)
        else:
            logger.error("Extraction failed for url=%s", url)
            print(f"❌ Failed to extract: {url}", file=sys.stderr)

    all_success = successes == len(args.urls)
    return 0 if all_success else 1


if __name__ == "__main__":
    raise SystemExit(main())

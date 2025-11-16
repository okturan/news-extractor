#!/usr/bin/env python3
"""
Script to extract article content from Turkish news sites using newspaper3k library.
"""

import json
import sys
from newspaper import Article


def extract_article(url, output_file):
    """
    Extract article content using newspaper3k and save to JSON.

    Args:
        url: The URL of the article to extract
        output_file: Path to save the JSON result
    """
    print(f"\nProcessing: {url}")
    print("=" * 80)

    try:
        # Create Article object with Turkish language setting
        article = Article(url, language='tr')

        # Download and parse the article
        print("Downloading article...")
        article.download()

        print("Parsing article...")
        article.parse()

        # Extract title and content
        title = article.title
        content = article.text
        char_count = len(content)

        # Assess extraction quality
        extraction_quality = assess_quality(title, content, url)

        # Create result dictionary
        result = {
            "url": url,
            "title": title,
            "content": content,
            "method": "newspaper3k",
            "extraction_quality": extraction_quality,
            "char_count": char_count
        }

        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Print summary
        print(f"\nExtraction Summary:")
        print(f"  Title: {title[:100]}..." if len(title) > 100 else f"  Title: {title}")
        print(f"  Content length: {char_count} characters")
        print(f"  Quality: {extraction_quality}")
        print(f"  Saved to: {output_file}")

        return result

    except Exception as e:
        print(f"\nERROR: Failed to extract article")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")

        # Save error result
        result = {
            "url": url,
            "title": "",
            "content": "",
            "method": "newspaper3k",
            "extraction_quality": "failed",
            "char_count": 0,
            "error": str(e)
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result


def assess_quality(title, content, url):
    """
    Assess the quality of extraction based on title and content.

    Returns:
        "good", "partial", or "failed"
    """
    # Check if it's a homepage URL
    if url.endswith('.com.tr/') or url.endswith('.com/'):
        if not content or len(content) < 100:
            return "failed - homepage (no article)"
        else:
            return "partial - homepage"

    # Check for minimal content
    if not title and not content:
        return "failed"

    if not title or len(title) < 10:
        return "partial - missing title"

    if not content or len(content) < 100:
        return "partial - insufficient content"

    # Check content quality
    if len(content) < 500:
        return "partial - short content"

    # Good extraction
    return "good"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_article.py <url> <output_file>")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2]

    extract_article(url, output_file)

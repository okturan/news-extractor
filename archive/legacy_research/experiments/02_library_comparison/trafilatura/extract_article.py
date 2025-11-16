#!/usr/bin/env python3
"""
Trafilatura Article Extractor for Turkish News Sites
Extracts article title and content from URLs and saves to JSON files.
"""

import json
import sys
from pathlib import Path
import trafilatura


def extract_article(url):
    """
    Extract article content using Trafilatura.

    Args:
        url (str): The URL to extract content from

    Returns:
        dict: Extracted article data including title, content, and metadata
    """
    print(f"\nExtracting content from: {url}")

    try:
        # Download the webpage
        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return {
                "url": url,
                "title": None,
                "content": None,
                "method": "trafilatura",
                "extraction_quality": "failed",
                "char_count": 0,
                "error": "Failed to download webpage"
            }

        # Extract content with metadata
        result = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            with_metadata=True,
            output_format='json'
        )

        if not result:
            return {
                "url": url,
                "title": None,
                "content": None,
                "method": "trafilatura",
                "extraction_quality": "failed",
                "char_count": 0,
                "error": "Extraction returned no results"
            }

        # Parse the JSON result
        parsed_result = json.loads(result)

        # Extract title and content
        title = parsed_result.get('title', '')
        content = parsed_result.get('text', '')

        # Assess extraction quality
        if not title and not content:
            quality = "failed"
        elif not title or not content:
            quality = "partial"
        elif len(content) < 100:
            quality = "partial"
        else:
            quality = "good"

        return {
            "url": url,
            "title": title,
            "content": content,
            "method": "trafilatura",
            "extraction_quality": quality,
            "char_count": len(content) if content else 0,
            "metadata": {
                "author": parsed_result.get('author'),
                "date": parsed_result.get('date'),
                "description": parsed_result.get('description'),
                "source": parsed_result.get('source'),
                "categories": parsed_result.get('categories'),
                "tags": parsed_result.get('tags')
            }
        }

    except Exception as e:
        print(f"Error during extraction: {str(e)}")
        return {
            "url": url,
            "title": None,
            "content": None,
            "method": "trafilatura",
            "extraction_quality": "failed",
            "char_count": 0,
            "error": str(e)
        }


def save_to_json(data, output_file):
    """
    Save extracted data to a JSON file.

    Args:
        data (dict): The data to save
        output_file (str): Output file path
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Results saved to: {output_file}")


def main():
    """Main function to test extraction on Turkish news sites."""

    # Define test URLs and their output files
    test_cases = [
        {
            "url": "https://www.hurriyet.com.tr/gundem/arnavutkoyde-feci-kaza-tir-devrildi-surucu-agir-yarali-43010201",
            "output": "/Users/okan/code/haberin-dibi/trafilatura/hurriyet_result.json"
        },
        {
            "url": "https://www.odatv.com/guncel/sucuk-ekmek-kabusa-dondu-80-kisi-hastanelik-120122349",
            "output": "/Users/okan/code/haberin-dibi/trafilatura/odatv_result.json"
        },
        {
            "url": "https://www.milliyet.com.tr/",
            "output": "/Users/okan/code/haberin-dibi/trafilatura/milliyet_result.json"
        }
    ]

    print("=" * 70)
    print("Trafilatura Content Extraction Test for Turkish News Sites")
    print("=" * 70)

    results_summary = []

    for test_case in test_cases:
        url = test_case["url"]
        output_file = test_case["output"]

        # Extract article content
        result = extract_article(url)

        # Save to JSON
        save_to_json(result, output_file)

        # Add to summary
        results_summary.append({
            "site": url.split('/')[2],
            "url": url,
            "quality": result["extraction_quality"],
            "char_count": result["char_count"],
            "title_extracted": bool(result.get("title")),
            "content_extracted": bool(result.get("content"))
        })

        print(f"  - Title: {result.get('title', 'N/A')[:60]}...")
        print(f"  - Quality: {result['extraction_quality']}")
        print(f"  - Char count: {result['char_count']}")
        if "error" in result:
            print(f"  - Error: {result['error']}")

    # Print summary
    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)

    for summary in results_summary:
        print(f"\n{summary['site']}:")
        print(f"  Quality: {summary['quality']}")
        print(f"  Characters: {summary['char_count']}")
        print(f"  Title: {'Yes' if summary['title_extracted'] else 'No'}")
        print(f"  Content: {'Yes' if summary['content_extracted'] else 'No'}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()

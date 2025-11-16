#!/usr/bin/env python3
"""
Article extraction using Mozilla's Readability algorithm via readability-lxml
"""

import json
import sys
import requests
from readability import Document


def extract_article(url):
    """
    Extract article content from URL using Readability

    Args:
        url: URL of the article to extract

    Returns:
        dict: Extracted article data with title, content, and metadata
    """
    try:
        # Create request with proper headers to avoid blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Fetch the page using requests (better SSL handling)
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=30, verify=True)
        response.raise_for_status()
        html = response.text  # Use text instead of content to get string

        # Apply Readability
        print("Applying Readability extraction...")
        doc = Document(html)

        # Extract title and content
        title = doc.title()
        content = doc.summary()

        # Calculate character count (HTML included)
        char_count = len(content)

        # Try to extract text-only version for better char count
        from lxml import html as lxml_html
        tree = lxml_html.fromstring(content)
        text_content = tree.text_content()
        text_char_count = len(text_content.strip())

        # Assess quality based on content length
        if text_char_count > 500:
            quality = "good"
        elif text_char_count > 100:
            quality = "partial"
        else:
            quality = "failed"

        result = {
            "url": url,
            "title": title,
            "content": content,
            "text_only": text_content.strip(),
            "method": "readability",
            "extraction_quality": quality,
            "char_count": char_count,
            "text_char_count": text_char_count
        }

        print(f"Success! Title: {title}")
        print(f"Character count (HTML): {char_count}")
        print(f"Character count (text): {text_char_count}")
        print(f"Quality assessment: {quality}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {str(e)}")
        return {
            "url": url,
            "title": "",
            "content": "",
            "text_only": "",
            "method": "readability",
            "extraction_quality": "failed",
            "char_count": 0,
            "text_char_count": 0,
            "error": f"Request Error: {str(e)}"
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "url": url,
            "title": "",
            "content": "",
            "text_only": "",
            "method": "readability",
            "extraction_quality": "failed",
            "char_count": 0,
            "text_char_count": 0,
            "error": str(e)
        }


def main():
    """Main function to test Readability on Turkish news sites"""

    # Test URLs
    test_urls = [
        ("https://www.hurriyet.com.tr/gundem/arnavutkoyde-feci-kaza-tir-devrildi-surucu-agir-yarali-43010201", "hurriyet_result.json"),
        ("https://www.odatv.com/guncel/sucuk-ekmek-kabusa-dondu-80-kisi-hastanelik-120122349", "odatv_result.json"),
        ("https://www.milliyet.com.tr/", "milliyet_result.json")
    ]

    results = []

    for url, filename in test_urls:
        print("\n" + "="*80)
        print(f"Testing: {url}")
        print("="*80)

        result = extract_article(url)

        # Save to JSON file
        output_path = f"/Users/okan/code/news-extractor/readability/{filename}"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"Saved to: {output_path}")
        results.append(result)

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for i, (url, filename) in enumerate(test_urls):
        result = results[i]
        print(f"\n{filename}:")
        print(f"  Quality: {result['extraction_quality']}")
        print(f"  Text chars: {result['text_char_count']}")
        print(f"  Title: {result['title'][:60]}..." if len(result['title']) > 60 else f"  Title: {result['title']}")
        if 'error' in result:
            print(f"  Error: {result['error']}")


if __name__ == "__main__":
    main()

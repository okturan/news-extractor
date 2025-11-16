#!/usr/bin/env python3
"""
Test extruct for extracting structured metadata (Schema.org, JSON-LD, OpenGraph)
Expert recommendation: Newspaper4k + extruct = tags without fallback
"""

import requests
from newspaper import Article, Config
import extruct
import json
from pprint import pprint

# Test URLs
test_urls = [
    {
        'name': 'bianet_1',
        'url': 'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281'
    },
    {
        'name': 'bianet_2',
        'url': 'https://bianet.org/haber/iklim-agindan-turkiyeye-emisyonlari-azaltmadan-iklim-kriziyle-mucadele-edilemez-313275'
    },
]

print("=" * 80)
print("EXTRUCT METADATA EXTRACTION TEST")
print("=" * 80)
print("Testing Expert 1's recommendation: Newspaper4k + extruct for tags")
print()

for test in test_urls:
    name = test['name']
    url = test['url']

    print(f"\n{'=' * 80}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print("=" * 80)

    # Download HTML once
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = response.text

    # ========================================================================
    # 1. Newspaper4k (baseline - article extraction)
    # ========================================================================

    print("\n1. NEWSPAPER4K (article extraction)")
    print("-" * 80)

    try:
        config = Config()
        config.language = 'tr'
        article = Article(url, config=config)
        article.download()
        article.parse()

        print(f"✅ Success")
        print(f"   Title: {article.title}")
        print(f"   Authors: {article.authors}")
        print(f"   Date: {article.publish_date}")
        print(f"   Text length: {len(article.text)} chars")
        print(f"   Meta keywords: {article.meta_keywords}")  # Check if N4K extracts keywords
        print(f"   Meta description: {article.meta_description[:100] if article.meta_description else 'None'}...")

    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")

    # ========================================================================
    # 2. extruct (metadata extraction)
    # ========================================================================

    print("\n2. EXTRUCT (structured metadata)")
    print("-" * 80)

    try:
        # Extract all structured data
        metadata = extruct.extract(
            html,
            base_url=url,
            syntaxes=['json-ld', 'opengraph', 'microdata', 'microformat']
        )

        print(f"✅ Extracted structured data")
        print()

        # Check JSON-LD
        if metadata.get('json-ld'):
            print("📄 JSON-LD data:")
            for item in metadata['json-ld']:
                if isinstance(item, dict):
                    print(f"   Type: {item.get('@type', 'Unknown')}")

                    # Extract relevant fields
                    fields_to_check = [
                        'headline', 'name', 'keywords', 'articleSection',
                        'author', 'datePublished', 'image', 'description',
                        'articleBody'
                    ]

                    for field in fields_to_check:
                        if field in item:
                            value = item[field]
                            if isinstance(value, str) and len(value) > 100:
                                print(f"   {field}: {value[:100]}...")
                            elif isinstance(value, list):
                                print(f"   {field}: {value}")
                            else:
                                print(f"   {field}: {value}")
                    print()

        # Check OpenGraph
        if metadata.get('opengraph'):
            print("📊 OpenGraph data:")
            for item in metadata['opengraph']:
                print(f"   Type: {item.get('@type', item.get('og:type', 'Unknown'))}")

                fields_to_show = [
                    'og:title', 'og:description', 'og:image',
                    'og:type', 'article:published_time', 'article:author',
                    'article:tag', 'article:section'
                ]

                # Check both namespace and properties
                for field in fields_to_show:
                    if field in item:
                        value = item[field]
                        if isinstance(value, str) and len(value) > 100:
                            print(f"   {field}: {value[:100]}...")
                        else:
                            print(f"   {field}: {value}")

                # Also check 'properties' dict if present
                if 'properties' in item:
                    for key, value in item['properties'].items():
                        if 'tag' in key.lower() or 'section' in key.lower() or 'keyword' in key.lower():
                            print(f"   {key}: {value}")
                print()

        # Check Microdata
        if metadata.get('microdata'):
            print("🏷️  Microdata:")
            for item in metadata['microdata']:
                if isinstance(item, dict):
                    print(f"   Type: {item.get('type', 'Unknown')}")
                    if 'properties' in item:
                        for key, value in item['properties'].items():
                            if key in ['headline', 'keywords', 'articleSection', 'author', 'datePublished']:
                                print(f"   {key}: {value}")
                    print()

        # Summary of extracted tags/categories
        print("\n🎯 EXTRACTED TAGS/CATEGORIES:")
        print("-" * 80)

        tags_found = []
        categories_found = []

        # Extract from JSON-LD
        if metadata.get('json-ld'):
            for item in metadata['json-ld']:
                if isinstance(item, dict):
                    if 'keywords' in item:
                        keywords = item['keywords']
                        if isinstance(keywords, str):
                            tags_found.extend(keywords.split(','))
                        elif isinstance(keywords, list):
                            tags_found.extend(keywords)

                    if 'articleSection' in item:
                        section = item['articleSection']
                        if isinstance(section, str):
                            categories_found.append(section)
                        elif isinstance(section, list):
                            categories_found.extend(section)

        # Extract from OpenGraph
        if metadata.get('opengraph'):
            for item in metadata['opengraph']:
                if 'properties' in item:
                    props = item['properties']
                    if 'article:tag' in props:
                        article_tags = props['article:tag']
                        if isinstance(article_tags, list):
                            tags_found.extend(article_tags)
                        else:
                            tags_found.append(article_tags)

                    if 'article:section' in props:
                        article_section = props['article:section']
                        if isinstance(article_section, list):
                            categories_found.extend(article_section)
                        else:
                            categories_found.append(article_section)

        # Clean and display
        tags_found = [t.strip() for t in tags_found if t and t.strip()]
        categories_found = [c.strip() for c in categories_found if c and c.strip()]

        if tags_found:
            print(f"   Tags: {', '.join(tags_found)}")
        else:
            print(f"   Tags: ❌ None found")

        if categories_found:
            print(f"   Categories: {', '.join(categories_found)}")
        else:
            print(f"   Categories: ❌ None found")

    except Exception as e:
        print(f"❌ Extruct failed: {str(e)[:200]}")

    print()


# ============================================================================
# Summary and Recommendation
# ============================================================================

print("\n" + "=" * 80)
print("VERDICT: Is extruct the solution?")
print("=" * 80)
print()

print("Question: Can we get tags/categories without Trafilatura fallback?")
print()
print("Expert 1's suggestion:")
print("  'Keep Newspaper4k primary and add a zero-HTTP pass with extruct")
print("   to harvest Schema.org JSON-LD/Microdata/OpenGraph for keywords/articleSection'")
print()
print("Analysis:")
print("  - If extruct found tags/categories above: ✅ Expert is RIGHT")
print("  - If extruct found nothing: ❌ Still need Trafilatura for tags")
print()
print("Decision matrix:")
print("  1. Newspaper4k + extruct works → Use this (one HTTP call, zero cost)")
print("  2. extruct fails → Keep Newspaper4k + Trafilatura fallback")
print()
print("=" * 80)

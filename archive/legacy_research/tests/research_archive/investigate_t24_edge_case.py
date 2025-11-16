#!/usr/bin/env python3
"""
Investigate the T24 edge case where Newspaper4k extracted 0 chars
"""

from newspaper import Article, Config
import trafilatura
import requests
from bs4 import BeautifulSoup

url = "https://t24.com.tr/haber/victor-osimhen-sampiyonlar-ligi-nde-haftanin-11-ine-secildi,1274139"

print("=" * 80)
print("INVESTIGATING T24 EDGE CASE")
print("=" * 80)
print(f"URL: {url}")
print()

# 1. Fetch raw HTML
print("1. Fetching raw HTML...")
print("-" * 80)
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(f"Status code: {response.status_code}")
print(f"Content length: {len(response.text)} chars")
print(f"Encoding: {response.encoding}")

# 2. Parse with BeautifulSoup to see structure
print("\n2. Analyzing HTML structure...")
print("-" * 80)
soup = BeautifulSoup(response.text, 'html.parser')

# Look for article content
article_tags = soup.find_all('article')
print(f"<article> tags found: {len(article_tags)}")

# Look for common content containers
content_divs = soup.find_all('div', class_=lambda x: x and 'content' in x.lower() if x else False)
print(f"Content divs found: {len(content_divs)}")

# Look for paragraphs
paragraphs = soup.find_all('p')
print(f"<p> tags found: {len(paragraphs)}")

# Show first few paragraphs
print("\nFirst 5 paragraphs content:")
for i, p in enumerate(paragraphs[:5], 1):
    text = p.get_text().strip()
    if text:
        print(f"  {i}. {text[:100]}...")

# 3. Extract with Newspaper4k (detailed)
print("\n3. Newspaper4k Extraction (detailed)...")
print("-" * 80)

config = Config()
config.language = 'tr'
config.request_timeout = 10
config.browser_user_agent = 'Mozilla/5.0'

article = Article(url, config=config)

print("Downloading...")
article.download()
print(f"  HTML length after download: {len(article.html) if article.html else 0}")

print("Parsing...")
article.parse()

print("\nExtraction Results:")
print(f"  Title: {article.title}")
print(f"  Authors: {article.authors}")
print(f"  Publish date: {article.publish_date}")
print(f"  Text length: {len(article.text)}")
print(f"  Top image: {article.top_image}")
print(f"  Meta description: {article.meta_description[:100] if article.meta_description else None}...")

if article.text:
    print(f"\nExtracted text preview:")
    print(f"  {article.text[:500]}...")
else:
    print("\n⚠️ NO TEXT EXTRACTED!")

# Check what HTML Newspaper4k is working with
print("\n4. Inspecting Newspaper4k's internal HTML...")
print("-" * 80)
if article.html:
    soup_n4k = BeautifulSoup(article.html, 'html.parser')

    # Check for common article selectors
    selectors_to_check = [
        ('article', None),
        ('div', {'class': 'article-content'}),
        ('div', {'class': 'content'}),
        ('div', {'itemprop': 'articleBody'}),
        ('p', None),
    ]

    for tag, attrs in selectors_to_check:
        if attrs:
            found = soup_n4k.find_all(tag, attrs)
        else:
            found = soup_n4k.find_all(tag)
        print(f"  {tag}{f' {attrs}' if attrs else ''}: {len(found)} found")

# 5. Extract with Trafilatura (detailed)
print("\n5. Trafilatura Extraction (detailed)...")
print("-" * 80)

downloaded = trafilatura.fetch_url(url)
print(f"Downloaded HTML length: {len(downloaded) if downloaded else 0}")

metadata = trafilatura.extract_metadata(downloaded)
text = trafilatura.extract(
    downloaded,
    include_comments=False,
    include_tables=True,
    with_metadata=False
)

print("\nExtraction Results:")
print(f"  Title: {metadata.title if metadata else None}")
print(f"  Author: {metadata.author if metadata else None}")
print(f"  Date: {metadata.date if metadata else None}")
print(f"  Text length: {len(text) if text else 0}")

if text:
    print(f"\nExtracted text preview:")
    print(f"  {text[:500]}...")

# 6. Compare the two extractions
print("\n6. Comparison Summary...")
print("=" * 80)

print("\n📊 Results:")
print(f"  Newspaper4k text length: {len(article.text)}")
print(f"  Trafilatura text length: {len(text) if text else 0}")
print(f"  Difference: {abs(len(article.text) - (len(text) if text else 0))} chars")

print("\n🔍 Possible Reasons for Newspaper4k Failure:")
if len(article.text) == 0 and text and len(text) > 0:
    print("  ✓ HTML structure is unusual for this T24 article")
    print("  ✓ Newspaper4k's heuristics failed to identify article content")
    print("  ✓ Trafilatura's algorithm is more robust for this specific structure")
    print("  ✓ This is likely a site-specific edge case")

print("\n💡 Recommendation:")
print("  Use hybrid approach: try Newspaper4k first, fallback to Trafilatura if text_length == 0")
print("=" * 80)

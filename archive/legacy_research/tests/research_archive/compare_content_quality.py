#!/usr/bin/env python3
"""
Compare actual content quality between Newspaper4k, Trafilatura, and Crawl4AI
on the same Bianet article
"""

import asyncio
from newspaper import Article, Config
import trafilatura
import requests
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

url = "https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281"

print("=" * 80)
print("CONTENT QUALITY COMPARISON")
print("=" * 80)
print(f"URL: {url}")
print()

# 1. Newspaper4k
print("1. NEWSPAPER4K")
print("-" * 80)

config = Config()
config.language = 'tr'

article = Article(url, config=config)
article.download()
article.parse()

n4k_text = article.text
n4k_length = len(n4k_text)

print(f"Length: {n4k_length} chars")
print(f"Title: {article.title}")
print(f"Authors: {article.authors}")
print(f"Date: {article.publish_date}")
print(f"\nFirst 500 chars:")
print(n4k_text[:500])
print(f"\n...content continues...")

# 2. Trafilatura (manual download to avoid blocking)
print("\n\n2. TRAFILATURA")
print("-" * 80)

response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
html = response.text

traf_metadata = trafilatura.extract_metadata(html)
traf_text = trafilatura.extract(
    html,
    include_comments=False,
    include_tables=True,
    with_metadata=False
)

traf_length = len(traf_text) if traf_text else 0

print(f"Length: {traf_length} chars")
if traf_metadata:
    print(f"Title: {traf_metadata.title}")
    print(f"Author: {traf_metadata.author}")
    print(f"Date: {traf_metadata.date}")
else:
    print("No metadata extracted")

if traf_text:
    print(f"\nFirst 500 chars:")
    print(traf_text[:500])
    print(f"\n...content continues...")
else:
    print("\n❌ No text extracted")

# 3. Crawl4AI
print("\n\n3. CRAWL4AI")
print("-" * 80)


async def get_crawl4ai():
    browser_config = BrowserConfig(headless=True, verbose=False)
    crawler_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, wait_until="networkidle")

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)
        return result


result = asyncio.run(get_crawl4ai())

if result.success:
    crawl_text = result.markdown
    crawl_length = len(crawl_text) if crawl_text else 0

    print(f"Length: {crawl_length} chars")
    print(f"Title: {result.metadata.get('title') if result.metadata else 'N/A'}")
    print(f"Author: {result.metadata.get('author') if result.metadata else 'N/A'}")

    if crawl_text:
        print(f"\nFirst 500 chars:")
        print(crawl_text[:500])
        print(f"\n...content continues...")

        # Check for noise
        print(f"\nChecking for navigation/noise:")
        noise_indicators = ['Facebook', 'Twitter', 'Instagram', 'Youtube', 'Bluesky']
        for indicator in noise_indicators:
            count = crawl_text.count(indicator)
            if count > 0:
                print(f"  - '{indicator}': {count} occurrences")
else:
    print(f"❌ Failed: {result.error_message}")
    crawl_length = 0
    crawl_text = None

# Comparison
print("\n\n" + "=" * 80)
print("COMPARISON ANALYSIS")
print("=" * 80)

print(f"\nText Lengths:")
print(f"  Newspaper4k:  {n4k_length:6} chars")
print(f"  Trafilatura:  {traf_length:6} chars ({'+' if traf_length > n4k_length else ''}{traf_length - n4k_length})")
print(f"  Crawl4AI:     {crawl_length:6} chars ({'+' if crawl_length > n4k_length else ''}{crawl_length - n4k_length})")

# Content purity check
print(f"\nContent Purity (less is better):")

if n4k_text:
    n4k_social = sum(n4k_text.count(word) for word in ['Facebook', 'Twitter', 'Instagram'])
    print(f"  Newspaper4k:  {n4k_social} social media mentions")

if traf_text:
    traf_social = sum(traf_text.count(word) for word in ['Facebook', 'Twitter', 'Instagram'])
    print(f"  Trafilatura:  {traf_social} social media mentions")

if crawl_text:
    crawl_social = sum(crawl_text.count(word) for word in ['Facebook', 'Twitter', 'Instagram'])
    print(f"  Crawl4AI:     {crawl_social} social media mentions")

# Article content check
print(f"\nArticle Text Check (looking for actual article content):")
article_keywords = ['Erdoğan', 'Özel', 'tazminat', 'dava']

for keyword in article_keywords:
    n4k_count = n4k_text.count(keyword) if n4k_text else 0
    traf_count = traf_text.count(keyword) if traf_text else 0
    crawl_count = crawl_text.count(keyword) if crawl_text else 0

    print(f"  '{keyword}':")
    print(f"    N4K: {n4k_count}, Traf: {traf_count}, Crawl: {crawl_count}")

# Verdict
print("\n" + "=" * 80)
print("VERDICT")
print("=" * 80)

print("\n📊 Content Quality:")

# Determine winner based on multiple factors
scores = {
    'Newspaper4k': 0,
    'Trafilatura': 0,
    'Crawl4AI': 0
}

# Reasonable length (not too short, not bloated with nav)
if 800 < n4k_length < 2000:
    scores['Newspaper4k'] += 2
if 800 < traf_length < 2000:
    scores['Trafilatura'] += 2
if 800 < crawl_length < 2000:
    scores['Crawl4AI'] += 2

# Low noise
if n4k_text and n4k_social < 5:
    scores['Newspaper4k'] += 1
if traf_text and traf_social < 5:
    scores['Trafilatura'] += 1
if crawl_text and crawl_social < 5:
    scores['Crawl4AI'] += 1

# Has content
if n4k_length > 0:
    scores['Newspaper4k'] += 1
if traf_length > 0:
    scores['Trafilatura'] += 1
if crawl_length > 0:
    scores['Crawl4AI'] += 1

print(f"\nQuality Scores:")
for lib, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
    print(f"  {lib}: {score}/4 {'⭐' * score}")

winner = max(scores, key=scores.get)
print(f"\n🏆 Best Content Quality: {winner}")

print("\n💡 Notes:")
if crawl_length > n4k_length * 10:
    print("  - Crawl4AI includes significant navigation/boilerplate")
if crawl_length > 0 and n4k_length > 0:
    ratio = crawl_length / n4k_length
    print(f"  - Crawl4AI is {ratio:.1f}x the size of Newspaper4k")
    if ratio > 20:
        print("  - This suggests Crawl4AI captures entire page, not just article")

print("=" * 80)

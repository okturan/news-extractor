#!/usr/bin/env python3
"""
Debug script to understand why discovery finds different numbers of articles
"""

from newspaper import build, Config
import requests
from bs4 import BeautifulSoup


def debug_site_discovery(base_url, site_name):
    """Deep dive into what newspaper4k is discovering"""

    print(f"\n{'='*80}")
    print(f"DEBUG: {site_name}")
    print(f"{'='*80}")

    # Method 1: Newspaper4k discovery
    print(f"\n1️⃣ Newspaper4k Discovery:")
    print("-" * 80)

    config = Config()
    config.browser_user_agent = 'Mozilla/5.0'
    config.request_timeout = 10
    config.memoize_articles = False
    config.language = 'tr'

    site = build(base_url, config=config)

    print(f"Total discovered by Newspaper4k: {site.size()}")
    print(f"\nFirst 10 URLs discovered:")
    for i, article in enumerate(site.articles[:10], 1):
        print(f"  {i}. {article.url}")

    # Method 2: Manual link analysis
    print(f"\n2️⃣ Manual Link Analysis:")
    print("-" * 80)

    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all links
        all_links = soup.find_all('a', href=True)
        print(f"Total <a> tags on page: {len(all_links)}")

        # Filter for article-like links
        article_links = []
        for link in all_links:
            href = link['href']

            # Make absolute
            if href.startswith('/'):
                from urllib.parse import urljoin
                href = urljoin(base_url, href)

            # Filter criteria
            if href.startswith(base_url) and not any(skip in href.lower() for skip in
                ['javascript:', '#', 'facebook', 'twitter', 'instagram',
                 'kategori', 'tag', 'etiket', 'yazar', 'author']):
                article_links.append(href)

        # Deduplicate
        unique_links = list(set(article_links))

        print(f"Unique internal links: {len(unique_links)}")
        print(f"\nSample internal links (first 10):")
        for i, link in enumerate(unique_links[:10], 1):
            print(f"  {i}. {link}")

        # Check for RSS feeds
        print(f"\n3️⃣ RSS Feed Check:")
        print("-" * 80)

        rss_links = soup.find_all('link', type='application/rss+xml')
        if rss_links:
            print(f"Found {len(rss_links)} RSS feed(s):")
            for rss in rss_links:
                print(f"  • {rss.get('href')}")
        else:
            print("No RSS feeds found in HTML")

        # Check for sitemaps
        print(f"\n4️⃣ Sitemap Check:")
        print("-" * 80)

        sitemap_urls = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml",
            f"{base_url}/news-sitemap.xml"
        ]

        for sitemap_url in sitemap_urls:
            try:
                sitemap_response = requests.head(sitemap_url, timeout=5)
                if sitemap_response.status_code == 200:
                    print(f"✓ Found: {sitemap_url}")
                else:
                    print(f"✗ Not found: {sitemap_url} ({sitemap_response.status_code})")
            except:
                print(f"✗ Error checking: {sitemap_url}")

        # Analyze page structure
        print(f"\n5️⃣ Page Structure Analysis:")
        print("-" * 80)

        # Common article containers
        containers = {
            'article': soup.find_all('article'),
            'div.article': soup.find_all('div', class_=lambda x: x and 'article' in x.lower() if x else False),
            'div.news': soup.find_all('div', class_=lambda x: x and 'news' in x.lower() if x else False),
            'div.haber': soup.find_all('div', class_=lambda x: x and 'haber' in x.lower() if x else False),
        }

        for selector, elements in containers.items():
            print(f"  {selector}: {len(elements)} elements")

    except Exception as e:
        print(f"Error during manual analysis: {e}")

    print()


# Test sites with extreme differences
sites = [
    ('https://bianet.org', 'Bianet (only 1!)'),
    ('https://www.hurriyet.com.tr', 'Hurriyet (only 12)'),
    ('https://www.cumhuriyet.com.tr', 'Cumhuriyet (416!)'),
]

for url, name in sites:
    debug_site_discovery(url, name)

print("\n" + "=" * 80)
print("ANALYSIS SUMMARY")
print("=" * 80)
print("""
Newspaper4k discovers articles by:
1. Looking for <a> tags that point to article URLs
2. Filtering based on URL patterns (avoids categories, tags, authors)
3. Using heuristics to identify article pages vs navigation

Sites with MORE articles discovered likely:
- Have many article links on their homepage
- Use URL structures that newspaper4k recognizes as articles
- Have article listings/archives linked from homepage

Sites with FEWER articles discovered likely:
- Show limited articles on homepage (maybe use infinite scroll)
- Use URL patterns newspaper4k doesn't recognize
- Have more navigation/category links than direct article links
""")

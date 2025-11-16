#!/usr/bin/env python3
"""
Test if Trafilatura can extract links from homepages
"""

import trafilatura
from trafilatura import feeds

# Test homepage link extraction
sites = [
    'https://www.hurriyet.com.tr/',
    'https://www.odatv.com/',
    'https://bianet.org/',
    'https://www.sozcu.com.tr/',
]

print("Testing Trafilatura's link extraction capabilities\n")
print("=" * 80)

for site in sites:
    print(f"\n🔍 Testing: {site}")
    print("-" * 80)

    try:
        # Method 1: feeds.find_feed_urls (finds RSS/Atom feeds)
        print("\n1️⃣ Finding RSS feeds...")
        feed_urls = feeds.find_feed_urls(site)
        if feed_urls:
            print(f"   ✅ Found {len(feed_urls)} feed(s):")
            for feed_url in feed_urls:
                print(f"      • {feed_url}")
        else:
            print("   ❌ No feeds found")

        # Method 2: sitemaps.sitemap_search (finds sitemaps)
        print("\n2️⃣ Finding sitemaps...")
        from trafilatura import sitemaps
        sitemap_urls = sitemaps.sitemap_search(site)
        if sitemap_urls:
            print(f"   ✅ Found sitemap URLs (showing first 10):")
            for url in list(sitemap_urls)[:10]:
                print(f"      • {url}")
        else:
            print("   ❌ No sitemaps found")

        # Method 3: Extract all links from homepage
        print("\n3️⃣ Extracting links from HTML...")
        downloaded = trafilatura.fetch_url(site)

        # Use trafilatura's link extraction
        from trafilatura.external import try_justext
        from trafilatura.htmlprocessing import tree_cleaning
        from lxml import html

        if downloaded:
            tree = html.fromstring(downloaded)
            links = tree.xpath('//a/@href')

            # Filter for article-like URLs
            article_links = []
            for link in links:
                if link and ('http' in link or link.startswith('/')):
                    # Filter out common non-article patterns
                    skip_patterns = ['javascript:', 'mailto:', '#', 'facebook', 'twitter',
                                   'instagram', 'youtube', '/kategori/', '/tag/', '/etiket/']

                    if not any(pattern in link.lower() for pattern in skip_patterns):
                        # Make absolute
                        if link.startswith('/'):
                            from urllib.parse import urljoin
                            link = urljoin(site, link)

                        article_links.append(link)

            # Deduplicate
            article_links = list(set(article_links))

            print(f"   ✅ Found {len(article_links)} potential article links")
            print(f"   📋 Sample (first 5):")
            for link in article_links[:5]:
                print(f"      • {link}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

print("\n" + "=" * 80)
print("Summary:")
print("  • Trafilatura CAN find RSS feeds automatically")
print("  • Trafilatura CAN find sitemaps automatically")
print("  • For link extraction, we still need HTML parsing")
print("=" * 80)

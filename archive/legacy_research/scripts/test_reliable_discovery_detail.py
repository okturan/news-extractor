#!/usr/bin/env python3
"""
Show exactly how reliable_discovery.py filters links
Demonstrates the filtering process step by step
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def analyze_discovery_filtering(base_url, site_name):
    """Show the filtering process in detail"""

    print(f"\n{'='*80}")
    print(f"DETAILED FILTERING ANALYSIS: {site_name}")
    print(f"{'='*80}")

    # Fetch homepage
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(base_url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get all links
    all_links = soup.find_all('a', href=True)
    print(f"\n1. Total <a> tags found: {len(all_links)}")

    # Show some raw examples
    print(f"\n2. Sample raw links (first 20):")
    print("-" * 80)
    for i, link in enumerate(all_links[:20], 1):
        href = link['href'][:80]
        print(f"   {i:2}. {href}")

    # Filter step by step
    skip_patterns = [
        'javascript:', 'mailto:', '#', 'tel:',
        '/kategori/', '/category/', '/tag/', '/etiket/',
        '/yazar/', '/author/', '/yazarlar/',
        '/arsiv/', '/archive/',
        'facebook.com', 'twitter.com', 'instagram.com', 'youtube.com',
        'whatsapp.com', 'telegram.org',
        '/hakkimizda', '/about', '/iletisim', '/contact',
        '/reklam', '/advertise', '/ilan',
        '.pdf', '.jpg', '.png', '.mp4',
    ]

    include_patterns = [
        '/haber/', '/gundem/', '/ekonomi/', '/spor/', '/dunya/',
        '/politika/', '/kultur/', '/saglik/', '/teknoloji/',
        '/turkiye/', '/yasam/', '/galeri/', '/video/',
    ]

    # Track filtering stats
    stats = {
        'total': len(all_links),
        'not_http': 0,
        'external': 0,
        'skipped_pattern': 0,
        'no_article_indicators': 0,
        'final_articles': 0
    }

    article_urls = set()
    skipped_examples = {'not_http': [], 'external': [], 'skipped_pattern': [], 'no_article_indicators': []}

    for link in all_links:
        href = link['href'].strip()

        # Make absolute URL
        if href.startswith('/'):
            href = urljoin(base_url, href)
        elif not href.startswith('http'):
            stats['not_http'] += 1
            if len(skipped_examples['not_http']) < 5:
                skipped_examples['not_http'].append(href[:60])
            continue

        # Must be from same domain
        if not href.startswith(base_url):
            stats['external'] += 1
            if len(skipped_examples['external']) < 5:
                skipped_examples['external'].append(href[:60])
            continue

        # Skip if contains skip patterns
        if any(pattern in href.lower() for pattern in skip_patterns):
            stats['skipped_pattern'] += 1
            if len(skipped_examples['skipped_pattern']) < 5:
                skipped_examples['skipped_pattern'].append(href[:80])
            continue

        # Check if URL looks like an article
        is_article = False

        # Has include pattern?
        if any(pattern in href.lower() for pattern in include_patterns):
            is_article = True
        # Has numbers (often article IDs or dates)?
        elif any(char.isdigit() for char in href):
            is_article = True
        # Has multiple path segments (deeper than homepage)?
        path = urlparse(href).path
        if path.count('/') >= 2:
            is_article = True

        if is_article:
            article_urls.add(href)
            stats['final_articles'] += 1
        else:
            stats['no_article_indicators'] += 1
            if len(skipped_examples['no_article_indicators']) < 5:
                skipped_examples['no_article_indicators'].append(href[:80])

    # Print filtering results
    print(f"\n3. Filtering Results:")
    print("-" * 80)
    print(f"   Total links:                    {stats['total']}")
    print(f"   ❌ Not HTTP links:              {stats['not_http']:4} (javascript:, #, etc.)")
    print(f"   ❌ External domains:            {stats['external']:4} (facebook, twitter, etc.)")
    print(f"   ❌ Skip patterns matched:       {stats['skipped_pattern']:4} (/kategori/, /yazar/, etc.)")
    print(f"   ❌ No article indicators:       {stats['no_article_indicators']:4} (no numbers, shallow paths)")
    print("-" * 80)
    print(f"   ✅ FINAL ARTICLE URLs:          {stats['final_articles']}")

    # Show examples of what was filtered out
    print(f"\n4. Examples of FILTERED OUT links:")
    print("-" * 80)

    if skipped_examples['not_http']:
        print(f"\n   Not HTTP (javascript:, #, etc.):")
        for ex in skipped_examples['not_http']:
            print(f"      • {ex}")

    if skipped_examples['external']:
        print(f"\n   External domains:")
        for ex in skipped_examples['external']:
            print(f"      • {ex}")

    if skipped_examples['skipped_pattern']:
        print(f"\n   Skip patterns (/kategori/, /yazar/, etc.):")
        for ex in skipped_examples['skipped_pattern']:
            print(f"      • {ex}")

    if skipped_examples['no_article_indicators']:
        print(f"\n   No article indicators (homepage-level links):")
        for ex in skipped_examples['no_article_indicators']:
            print(f"      • {ex}")

    # Show examples of what was KEPT
    print(f"\n5. Examples of KEPT article URLs (first 10):")
    print("-" * 80)
    for i, url in enumerate(sorted(article_urls)[:10], 1):
        print(f"   {i:2}. {url}")

    print(f"\n{'='*80}")
    print(f"SUMMARY: {stats['total']} links → {stats['final_articles']} articles")
    print(f"{'='*80}\n")

    return stats


# Test on Bianet (small site, easy to analyze)
print("Testing filtering logic on Bianet...")
analyze_discovery_filtering('https://bianet.org', 'Bianet')

#!/usr/bin/env python3
"""
Reliable Article Discovery - Manual link extraction
Uses BeautifulSoup to find ALL article links (more reliable than newspaper4k)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime


def discover_articles_reliable(base_url, site_name):
    """
    Discover article URLs using manual HTML parsing
    More reliable than newspaper4k's automatic discovery
    """

    print(f"\n{'='*80}")
    print(f"Discovering: {site_name}")
    print(f"{'='*80}")

    try:
        # Fetch homepage
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all links
        all_links = soup.find_all('a', href=True)
        print(f"Total links found: {len(all_links)}")

        # Filter for article URLs
        article_urls = set()

        # Skip patterns (navigation, categories, etc.)
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

        # Include patterns (likely article URLs)
        include_patterns = [
            '/haber/', '/gundem/', '/ekonomi/', '/spor/', '/dunya/',
            '/politika/', '/kultur/', '/saglik/', '/teknoloji/',
            '/turkiye/', '/yasam/', '/galeri/', '/video/',
        ]

        for link in all_links:
            href = link['href'].strip()

            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif not href.startswith('http'):
                continue

            # Must be from same domain
            if not href.startswith(base_url):
                continue

            # Skip if contains skip patterns
            if any(pattern in href.lower() for pattern in skip_patterns):
                continue

            # Check if URL looks like an article
            # Articles usually have: numbers, hyphens, or include patterns
            is_article = False

            # Has include pattern?
            if any(pattern in href.lower() for pattern in include_patterns):
                is_article = True

            # Has numbers (often article IDs or dates)?
            elif any(char.isdigit() for char in href):
                # URLs with numbers are likely articles
                is_article = True

            # Has multiple path segments (deeper than homepage)?
            path = urlparse(href).path
            if path.count('/') >= 2:  # e.g., /section/article-title
                is_article = True

            if is_article:
                article_urls.add(href)

        # Convert to list with metadata
        articles = []
        for i, url in enumerate(sorted(article_urls), 1):
            articles.append({
                'index': i,
                'source': site_name,
                'url': url,
                'discovered_at': datetime.now().isoformat()
            })

        print(f"✅ Discovered {len(articles)} article URLs")

        return articles

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def main():
    """Discover articles from Turkish news sites"""

    sites = [
        ('https://www.hurriyet.com.tr', 'Hurriyet'),
        ('https://www.odatv.com', 'OdaTV'),
        ('https://bianet.org', 'Bianet'),
        ('https://www.sozcu.com.tr', 'Sozcu'),
        ('https://www.cumhuriyet.com.tr', 'Cumhuriyet'),
        ('https://www.milliyet.com.tr', 'Milliyet'),
        ('https://t24.com.tr', 'T24'),
        ('https://www.diken.com.tr', 'Diken'),
    ]

    all_discoveries = {
        'discovery_date': datetime.now().isoformat(),
        'method': 'manual_html_parsing',
        'total_sites': len(sites),
        'sites': {}
    }

    for url, name in sites:
        articles = discover_articles_reliable(url, name)

        all_discoveries['sites'][name] = {
            'base_url': url,
            'total_discovered': len(articles),
            'articles': articles
        }

    # Calculate totals
    total_articles = sum(site['total_discovered'] for site in all_discoveries['sites'].values())
    all_discoveries['total_articles_discovered'] = total_articles

    # Save results
    output_file = f'reliable_discovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_discoveries, f, ensure_ascii=False, indent=2)

    # Print summary
    print("\n" + "=" * 80)
    print("DISCOVERY SUMMARY (Reliable Method)")
    print("=" * 80)

    for site_name, data in all_discoveries['sites'].items():
        print(f"✓ {site_name:20} {data['total_discovered']:4} articles")

    print("-" * 80)
    print(f"  TOTAL:              {total_articles:4} articles")
    print("=" * 80)

    print(f"\n📁 Results saved to: {output_file}")

    # Show samples
    print("\n📋 Sample URLs:")
    print("-" * 80)
    for site_name, data in all_discoveries['sites'].items():
        if data['articles']:
            print(f"\n{site_name}:")
            for article in data['articles'][:3]:
                print(f"  • {article['url']}")

    return all_discoveries


if __name__ == '__main__':
    results = main()

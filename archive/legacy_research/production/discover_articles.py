#!/usr/bin/env python3
"""
Article URL Discovery - NO content fetching
Just discovers article URLs and metadata from news sites
"""

from newspaper import build, Config
import json
from datetime import datetime


def discover_articles(base_url, site_name, limit=None):
    """
    Discover all article URLs from a news site without fetching content

    Args:
        base_url: Base URL of the news site
        site_name: Name for identification
        limit: Maximum articles to discover (None = all)

    Returns:
        List of article metadata (URLs, titles, etc.)
    """

    print(f"\n{'='*80}")
    print(f"Discovering articles from: {site_name}")
    print(f"{'='*80}")

    # Configure newspaper
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0'
    config.request_timeout = 10
    config.memoize_articles = False
    config.language = 'tr'

    # Build the news source (this discovers URLs automatically)
    print(f"🔍 Analyzing {base_url}...")
    site = build(base_url, config=config)

    total_discovered = site.size()
    print(f"✅ Discovered {total_discovered} article URLs")

    articles = []

    # Get article URLs and basic metadata (NO downloading/parsing)
    articles_to_process = site.articles if limit is None else site.articles[:limit]

    for i, article in enumerate(articles_to_process, 1):
        # Don't download or parse - just get URL
        article_data = {
            'index': i,
            'source': site_name,
            'url': article.url,
            'discovered_at': datetime.now().isoformat()
        }

        articles.append(article_data)

        # Progress indicator
        if i % 50 == 0 or i == len(articles_to_process):
            print(f"  Collected {i}/{len(articles_to_process)} URLs...")

    print(f"\n{'='*80}")
    print(f"✓ Collected {len(articles)} article URLs from {site_name}")
    print(f"{'='*80}\n")

    return articles


def main():
    """Discover articles from multiple Turkish news sites"""

    sites = [
        ('https://www.hurriyet.com.tr', 'Hurriyet'),
        ('https://www.odatv.com', 'OdaTV'),
        ('https://bianet.org', 'Bianet'),
        ('https://www.sozcu.com.tr', 'Sozcu'),
        ('https://www.cumhuriyet.com.tr', 'Cumhuriyet'),
    ]

    all_discoveries = {
        'discovery_date': datetime.now().isoformat(),
        'total_sites': len(sites),
        'sites': {}
    }

    for url, name in sites:
        try:
            articles = discover_articles(url, name, limit=None)  # Get ALL

            all_discoveries['sites'][name] = {
                'base_url': url,
                'total_discovered': len(articles),
                'articles': articles
            }

        except Exception as e:
            print(f"❌ Error with {name}: {e}\n")
            all_discoveries['sites'][name] = {
                'base_url': url,
                'error': str(e),
                'total_discovered': 0,
                'articles': []
            }

    # Calculate totals
    total_articles = sum(site['total_discovered'] for site in all_discoveries['sites'].values())
    all_discoveries['total_articles_discovered'] = total_articles

    # Save results
    output_file = f'article_discovery_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_discoveries, f, ensure_ascii=False, indent=2)

    # Print summary
    print("\n" + "=" * 80)
    print("DISCOVERY SUMMARY")
    print("=" * 80)

    for site_name, data in all_discoveries['sites'].items():
        status = "✓" if data['total_discovered'] > 0 else "✗"
        print(f"{status} {site_name:20} {data['total_discovered']:4} articles")

    print("-" * 80)
    print(f"  TOTAL:              {total_articles:4} articles discovered")
    print("=" * 80)

    print(f"\n📁 Results saved to: {output_file}")

    # Show sample URLs
    print("\n📋 Sample URLs from each site:")
    print("-" * 80)
    for site_name, data in all_discoveries['sites'].items():
        if data['articles']:
            print(f"\n{site_name}:")
            for article in data['articles'][:3]:  # First 3
                print(f"  • {article['url']}")

    return all_discoveries


if __name__ == '__main__':
    results = main()

#!/usr/bin/env python3
"""
Smart News Scraper - NO manual selectors needed!
Uses Newspaper4k for automatic article discovery
"""

from newspaper import build, Config
import trafilatura

def smart_scrape(base_url, site_name, limit=10):
    """
    Scrape any news site with ZERO manual configuration

    How it works:
    1. Newspaper4k uses ML to find article links (no selectors!)
    2. Trafilatura extracts clean content
    3. Completely resilient to HTML changes
    """

    print(f"\n{'='*60}")
    print(f"Scraping: {site_name}")
    print(f"{'='*60}")

    # Configure newspaper
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0'
    config.request_timeout = 10
    config.memoize_articles = False  # Don't cache
    config.language = 'tr'  # Turkish

    # Build the news source (automatically finds article URLs)
    print(f"🔍 Discovering articles on {base_url}...")
    site = build(base_url, config=config)

    print(f"✅ Found {site.size()} article URLs automatically!")

    articles = []

    # Process articles
    for i, article in enumerate(site.articles[:limit], 1):
        try:
            print(f"\n[{i}/{limit}] Processing: {article.url[:60]}...")

            # Download and parse with newspaper
            article.download()
            article.parse()

            # Also get content with Trafilatura for comparison
            traf_content = trafilatura.extract(
                trafilatura.fetch_url(article.url)
            )

            result = {
                'source': site_name,
                'url': article.url,
                'title': article.title,
                'authors': article.authors,
                'publish_date': str(article.publish_date) if article.publish_date else None,
                'newspaper_content': article.text[:500] + '...' if len(article.text) > 500 else article.text,
                'trafilatura_content': traf_content[:500] + '...' if traf_content and len(traf_content) > 500 else traf_content,
                'top_image': article.top_image,
            }

            articles.append(result)

            print(f"  ✓ Title: {result['title'][:60]}...")
            print(f"  ✓ Content: {len(article.text)} chars")

        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"Successfully scraped {len(articles)} articles from {site_name}")
    print(f"{'='*60}\n")

    return articles


# Test on Turkish news sites
if __name__ == '__main__':
    sites = [
        ('https://www.hurriyet.com.tr', 'Hurriyet'),
        ('https://www.odatv.com', 'OdaTV'),
        ('https://bianet.org', 'Bianet'),
    ]

    all_articles = []

    for url, name in sites:
        articles = smart_scrape(url, name, limit=5)
        all_articles.extend(articles)

    # Save results
    import json
    from datetime import datetime

    output_file = f'smart_scrape_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Total articles scraped: {len(all_articles)}")
    print(f"📁 Results saved to: {output_file}")

    # Show sample
    if all_articles:
        print("\n📰 Sample Article:")
        print("-" * 60)
        sample = all_articles[0]
        print(f"Source: {sample['source']}")
        print(f"Title: {sample['title']}")
        print(f"URL: {sample['url']}")
        print(f"Content preview: {sample['newspaper_content'][:200]}...")

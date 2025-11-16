#!/usr/bin/env python3
"""
Test Crawl4AI with CSS selector targeting (lightweight approach)
"""

import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

url = "https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281"

print("=" * 80)
print("CRAWL4AI CSS SELECTOR TEST")
print("=" * 80)
print(f"URL: {url}")
print()


async def test_selector(selector_name, css_selector):
    """Test with specific CSS selector"""
    print(f"\nTesting: {selector_name}")
    print(f"Selector: {css_selector}")
    print("-" * 80)

    browser_config = BrowserConfig(headless=True, verbose=False)
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until="domcontentloaded",  # Faster than networkidle
        css_selector=css_selector,
        word_count_threshold=5,  # Only chunks with 5+ words
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

        if result.success:
            markdown = result.markdown
            print(f"✅ Success - {len(markdown)} chars")
            print(f"Preview: {markdown[:300]}...")
            return markdown
        else:
            print(f"❌ Failed")
            return None


async def main():
    # Test different CSS selectors
    selectors = {
        "Article tag": "article",
        "Main tag": "main",
        "Body (whole page)": "body",
        "Article content class": ".article-content, .haber-icerik, .post-content",
        "Paragraph only": "article p, main p, .article-content p",
    }

    results = {}

    for name, selector in selectors.items():
        try:
            result = await test_selector(name, selector)
            results[name] = result
            await asyncio.sleep(1)  # Be polite
        except Exception as e:
            print(f"❌ Exception: {str(e)[:100]}")
            results[name] = None

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\nResults:")
    for name, content in results.items():
        length = len(content) if content else 0
        status = "✅" if length > 0 else "❌"
        print(f"  {name:30} {status} {length:6} chars")

    # Find best (closest to 1000-2000 chars - article size)
    valid_results = {k: v for k, v in results.items() if v and 500 < len(v) < 5000}

    if valid_results:
        best = min(valid_results.items(), key=lambda x: abs(len(x[1]) - 1500))
        print(f"\n🏆 Best selector: {best[0]} ({len(best[1])} chars)")
        print(f"\nComparison with Newspaper4k (1027 chars):")
        print(f"  Crawl4AI best: {len(best[1])} chars ({len(best[1])/1027:.1f}x)")
    else:
        print(f"\n⚠️  No selector produced article-sized content (500-5000 chars)")
        print(f"   Crawl4AI may not be suitable for this use case")

    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())

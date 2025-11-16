#!/usr/bin/env python3
"""
Test Crawl4AI on Turkish news articles
Focus on Bianet failures and T24 edge case
"""

import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import json
from datetime import datetime

# Test URLs - focusing on problem cases
test_urls = {
    'bianet_1': 'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281',
    'bianet_2': 'https://bianet.org/haber/iklim-agindan-turkiyeye-emisyonlari-azaltmadan-iklim-kriziyle-mucadele-edilemez-313275',
    'bianet_3': 'https://bianet.org/haber/gazetecilere-operasyon-yalcin-cakir-oghan-sevinc-ve-colak-serbest-313253',
    't24_edge': 'https://t24.com.tr/haber/victor-osimhen-sampiyonlar-ligi-nde-haftanin-11-ine-secildi,1274139',
    'hurriyet': 'https://www.hurriyet.com.tr/haberleri/18-30-yas-arasi-toki-basvuru-sartlari',
    'odatv': 'https://www.odatv.com/guncel/akran-zorbaligi-davasinda-karar-cikti-120122351',
}


async def test_crawl4ai(url, name):
    """Test Crawl4AI extraction"""
    try:
        # Configure browser
        browser_config = BrowserConfig(
            headless=True,
            verbose=False,
        )

        # Configure crawler
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,  # Don't cache for testing
            wait_until="networkidle",  # Wait for network to be idle
        )

        print(f"\n[{name}] Crawling: {url[:60]}...")

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=crawler_config
            )

            if result.success:
                # Extract content
                markdown = result.markdown  # Main content as markdown
                html = result.html  # Full HTML
                cleaned_html = result.cleaned_html  # Cleaned HTML

                # Metadata
                metadata = result.metadata

                print(f"  ✅ SUCCESS")
                print(f"     Markdown length: {len(markdown) if markdown else 0} chars")
                print(f"     HTML length: {len(html) if html else 0} chars")
                print(f"     Title: {metadata.get('title', 'N/A') if metadata else 'N/A'}")

                # Preview
                if markdown:
                    preview = markdown[:200].replace('\n', ' ')
                    print(f"     Preview: {preview}...")

                return {
                    'name': name,
                    'url': url,
                    'success': True,
                    'markdown': markdown,
                    'markdown_length': len(markdown) if markdown else 0,
                    'title': metadata.get('title', None) if metadata else None,
                    'metadata': metadata,
                }
            else:
                print(f"  ❌ FAILED: {result.error_message}")
                return {
                    'name': name,
                    'url': url,
                    'success': False,
                    'error': result.error_message,
                    'markdown_length': 0,
                }

    except Exception as e:
        print(f"  ❌ EXCEPTION: {str(e)[:100]}")
        return {
            'name': name,
            'url': url,
            'success': False,
            'error': str(e),
            'markdown_length': 0,
        }


async def main():
    print("=" * 80)
    print("CRAWL4AI TEST - AI-POWERED EXTRACTION")
    print("=" * 80)
    print("Testing on problem URLs: Bianet (failed with Trafilatura) and T24 edge case")
    print()

    results = []

    for name, url in test_urls.items():
        result = await test_crawl4ai(url, name)
        results.append(result)
        await asyncio.sleep(1)  # Be polite

    # Summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"\nOverall: {successful}/{total} ({successful/total*100:.1f}%)")

    # Bianet specific
    bianet_results = [r for r in results if r['name'].startswith('bianet')]
    bianet_success = sum(1 for r in bianet_results if r['success'])

    print(f"\nBianet: {bianet_success}/3 ({bianet_success/3*100:.1f}%)")
    if bianet_success == 3:
        print("  🎉 SUCCESS! Crawl4AI works on all Bianet articles!")
    elif bianet_success > 0:
        print(f"  ⚠️  Partial - {bianet_success} out of 3 worked")
    else:
        print("  ❌ Failed on all Bianet articles")

    # T24 edge case
    t24_result = next((r for r in results if r['name'] == 't24_edge'), None)
    if t24_result:
        print(f"\nT24 Edge Case: {'✅ SUCCESS' if t24_result['success'] and t24_result['markdown_length'] > 0 else '❌ FAILED'}")
        if t24_result['success']:
            print(f"  Text length: {t24_result['markdown_length']} chars")
            print(f"  (Newspaper4k got 0 chars on this URL)")

    # Comparison
    print("\n" + "=" * 80)
    print("COMPARISON WITH OTHER LIBRARIES")
    print("=" * 80)
    print("\nBianet.org:")
    print(f"  Newspaper4k:    3/3 (100%) ✅")
    print(f"  Trafilatura 2.0: 0/3 (0%)   ❌")
    print(f"  Crawl4AI:       {bianet_success}/3 ({bianet_success/3*100:.0f}%) {'✅' if bianet_success == 3 else '❌'}")

    print("\nT24 Edge Case:")
    print(f"  Newspaper4k:    0 chars ❌")
    print(f"  Trafilatura 2.0: 664 chars ✅")
    if t24_result and t24_result['success']:
        print(f"  Crawl4AI:       {t24_result['markdown_length']} chars {'✅' if t24_result['markdown_length'] > 0 else '❌'}")

    # Save results
    output_file = f'crawl4ai_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

    # Remove markdown content from save (too large)
    save_results = []
    for r in results:
        save_r = r.copy()
        if 'markdown' in save_r:
            save_r['markdown_preview'] = save_r['markdown'][:500] if save_r.get('markdown') else None
            del save_r['markdown']
        save_results.append(save_r)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'total': total,
            'successful': successful,
            'success_rate': successful/total*100,
            'results': save_results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n📁 Results saved to: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())

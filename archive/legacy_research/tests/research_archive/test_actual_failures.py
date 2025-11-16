#!/usr/bin/env python3
"""
Test the URLs that ACTUALLY failed with other tools
- T24 edge case (failed with Crawl4AI timeout)
- Hurriyet (failed with Crawl4AI timeout)
- OdaTV (failed with Crawl4AI timeout)

Plus real edge cases:
- Paywalled content
- Video-heavy articles
- Embedded social media
"""

from newspaper import Article, Config
import requests
import time

# URLs that failed with Crawl4AI
test_urls = [
    {
        'name': 'Bianet (baseline - known to work)',
        'url': 'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281',
        'source': 'bianet',
        'issue': 'none'
    },
    {
        'name': 'T24 - Victor Osimhen news',
        'url': 'https://t24.com.tr/haber/victor-osimhen-sampiyonlar-ligi-nde-haftanin-11-ine-secildi,1274139',
        'source': 't24',
        'issue': 'Crawl4AI timeout (60s)'
    },
    {
        'name': 'Hürriyet - TOKİ haberleri page',
        'url': 'https://www.hurriyet.com.tr/haberleri/18-30-yas-arasi-toki-basvuru-sartlari',
        'source': 'hurriyet',
        'issue': 'Crawl4AI timeout (60s)'
    },
    {
        'name': 'OdaTV - Court decision',
        'url': 'https://www.odatv.com/guncel/akran-zorbaligi-davasinda-karar-cikti-120122351',
        'source': 'odatv',
        'issue': 'Crawl4AI timeout (60s)'
    },
    {
        'name': 'Sözcü - Ruşen Çakır news',
        'url': 'https://www.sozcu.com.tr/2025/gundem/son-dakika-haberi-rusen-cakir-gozaltina-alindi-8423910/',
        'source': 'sozcu',
        'issue': 'embedded tweets, ads'
    },
    {
        'name': 'Cumhuriyet - Vize article',
        'url': 'https://www.cumhuriyet.com.tr/turkiye/turkiye-vize-kolayligi-getirilen-ulkeler-listesi-listede-hangi-ulkeler-var-2261093',
        'source': 'cumhuriyet',
        'issue': 'potential paywall'
    },
    {
        'name': 'NTV - Breaking news',
        'url': 'https://www.ntv.com.tr/galeri/turkiye/son-dakika-gaziantepte-deprem-kandilli-ve-afad-son-depremler-listesi,9kQ8R0F5pESlN-Nn6_jYxg',
        'source': 'ntv',
        'issue': 'gallery/slideshow format'
    },
]

print("=" * 80)
print("TESTING ACTUAL PROBLEM URLS")
print("=" * 80)
print("Testing Newspaper4k on URLs that failed with other tools")
print()

results = []

for test in test_urls:
    name = test['name']
    url = test['url']
    source = test['source']
    issue = test['issue']

    print(f"\n{'=' * 80}")
    print(f"{name}")
    print(f"URL: {url}")
    print(f"Known issue: {issue}")
    print("-" * 80)

    result = {
        'name': name,
        'url': url,
        'source': source,
        'issue': issue
    }

    start_time = time.time()

    try:
        config = Config()
        config.language = 'tr'
        config.request_timeout = 30  # 30 second timeout

        article = Article(url, config=config)
        article.download()
        article.parse()

        elapsed = time.time() - start_time

        text_length = len(article.text)
        has_meaningful_text = text_length > 100

        # Check for common issues
        text_lower = article.text.lower() if article.text else ''

        paywall_words = ['üye ol', 'abone ol', 'giriş yap', 'premium üye']
        has_paywall = any(word in text_lower for word in paywall_words)

        social_artifacts = article.text.count('twitter.com') + article.text.count('instagram.com')

        result.update({
            'success': True,
            'time': elapsed,
            'title': article.title,
            'text_length': text_length,
            'has_text': has_meaningful_text,
            'authors': article.authors,
            'date': str(article.publish_date) if article.publish_date else None,
            'keywords': article.meta_keywords,
            'top_image': article.top_image,
            'paywall_detected': has_paywall,
            'social_artifacts': social_artifacts
        })

        print(f"✅ SUCCESS ({elapsed:.2f}s)")
        print(f"   Title: {article.title}")
        print(f"   Text: {text_length} chars {'✅' if has_meaningful_text else '❌ TOO SHORT'}")
        print(f"   Authors: {article.authors}")
        print(f"   Date: {article.publish_date}")
        print(f"   Keywords: {article.meta_keywords}")

        if has_paywall:
            print(f"   ⚠️  Paywall keywords detected")

        if social_artifacts > 0:
            print(f"   ⚠️  {social_artifacts} social media URLs in text")

        if text_length > 0:
            print(f"\n   Preview:")
            print(f"   {article.text[:250]}...")

    except Exception as e:
        elapsed = time.time() - start_time
        result.update({
            'success': False,
            'time': elapsed,
            'error': str(e)[:300]
        })
        print(f"❌ FAILED ({elapsed:.2f}s)")
        print(f"   Error: {str(e)[:300]}")

    results.append(result)

# Summary
print("\n\n" + "=" * 80)
print("SUMMARY: Newspaper4k vs Failed URLs")
print("=" * 80)
print()

successful = sum(1 for r in results if r.get('success'))
total = len(results)

print(f"Overall success rate: {successful}/{total} ({successful/total*100:.1f}%)")
print()

# Group by source
print("Success by source:")
print("-" * 80)

sources = {}
for r in results:
    src = r['source']
    if src not in sources:
        sources[src] = {'success': 0, 'total': 0}
    sources[src]['total'] += 1
    if r.get('success'):
        sources[src]['success'] += 1

for src, stats in sorted(sources.items()):
    rate = stats['success'] / stats['total'] * 100
    status = "✅" if rate == 100 else "⚠️" if rate > 0 else "❌"
    print(f"   {status} {src:15} {stats['success']}/{stats['total']} ({rate:.0f}%)")

print()

# Performance comparison
print("Performance comparison:")
print("-" * 80)

successful_results = [r for r in results if r.get('success')]
if successful_results:
    avg_time = sum(r['time'] for r in successful_results) / len(successful_results)
    max_time = max(r['time'] for r in successful_results)
    min_time = min(r['time'] for r in successful_results)

    print(f"   Average time: {avg_time:.2f}s")
    print(f"   Min time: {min_time:.2f}s")
    print(f"   Max time: {max_time:.2f}s")
    print()
    print(f"   Compare to Crawl4AI:")
    print(f"   - Crawl4AI: 4+ seconds (when it worked)")
    print(f"   - Crawl4AI: 60s timeout (T24, Hurriyet, OdaTV)")
    print(f"   - Newspaper4k: {avg_time:.2f}s average ✅")

print()

# Detailed issue analysis
print("=" * 80)
print("ISSUE-BY-ISSUE ANALYSIS")
print("=" * 80)
print()

# URLs that timed out with Crawl4AI
crawl_timeouts = [r for r in results if 'timeout' in r['issue'].lower()]
if crawl_timeouts:
    timeout_successes = [r for r in crawl_timeouts if r.get('success')]
    print(f"URLs that timed out with Crawl4AI (60s):")
    print(f"   Newspaper4k: {len(timeout_successes)}/{len(crawl_timeouts)} succeeded")

    if timeout_successes:
        avg = sum(r['time'] for r in timeout_successes) / len(timeout_successes)
        print(f"   Average time: {avg:.2f}s (vs 60s+ timeout)")
        print(f"   ✅ Newspaper4k handles these sites much faster!")
    print()

# Paywalled content
paywall_tests = [r for r in results if 'paywall' in r['issue'].lower()]
if paywall_tests:
    print(f"Potential paywalled content:")
    for r in paywall_tests:
        if r.get('success'):
            if r.get('paywall_detected'):
                print(f"   ⚠️  {r['source']}: Paywall keywords detected")
                print(f"      Text length: {r['text_length']} chars (may be paywall message)")
            else:
                print(f"   ✅ {r['source']}: Full text extracted ({r['text_length']} chars)")
        else:
            print(f"   ❌ {r['source']}: Extraction failed")
    print()

# Social media embeds
social_tests = [r for r in results if r.get('social_artifacts', 0) > 0]
if social_tests:
    print(f"Articles with embedded social media:")
    for r in social_tests:
        print(f"   ⚠️  {r['source']}: {r['social_artifacts']} social media URLs in text")
        print(f"      Recommendation: Post-process to remove URLs")
    print()

# Gallery/slideshow format
gallery_tests = [r for r in results if 'gallery' in r['issue'].lower() or 'slideshow' in r['issue'].lower()]
if gallery_tests:
    print(f"Gallery/slideshow format:")
    for r in gallery_tests:
        if r.get('success'):
            print(f"   {'✅' if r['has_text'] else '⚠️ '} {r['source']}: {r['text_length']} chars")
            if not r['has_text']:
                print(f"      May be image-first content with minimal text")
        else:
            print(f"   ❌ {r['source']}: Failed")
    print()

print("=" * 80)
print("FINAL VERDICT")
print("=" * 80)
print()

if successful == total:
    print("🎉 PERFECT SCORE!")
    print(f"   Newspaper4k: {successful}/{total} (100%)")
    print(f"   Crawl4AI: 3/6 (50%) on same URLs")
    print()
    print("   Newspaper4k handles ALL the URLs that Crawl4AI struggled with!")
    print()

elif successful >= total * 0.8:
    print(f"✅ STRONG PERFORMANCE")
    print(f"   Newspaper4k: {successful}/{total} ({successful/total*100:.0f}%)")
    print()
    failed = [r for r in results if not r.get('success')]
    print(f"   Failed on:")
    for r in failed:
        print(f"   - {r['source']}: {r['name']}")
    print()
    print("   Recommendation: Use Trafilatura as fallback for these sources")

else:
    print(f"⚠️  MODERATE PERFORMANCE")
    print(f"   Newspaper4k: {successful}/{total} ({successful/total*100:.0f}%)")
    print()
    print("   May need multi-tier fallback strategy")

print("=" * 80)

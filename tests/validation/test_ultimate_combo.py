#!/usr/bin/env python3
"""
Test the ACTUAL proposed solution:
Newspaper4k (primary) + Trafilatura JSON (fallback)

On the URLs that showed problems
"""

import requests
from newspaper import Article, Config
import trafilatura
import json
import time

# URLs that had issues with Newspaper4k alone
problem_urls = [
    {
        'name': 'T24 - Empty extraction',
        'url': 'https://t24.com.tr/haber/victor-osimhen-sampiyonlar-ligi-nde-haftanin-11-ine-secildi,1274139',
        'newspaper4k_issue': '0 chars extracted'
    },
    {
        'name': 'Sözcü - 404 error',
        'url': 'https://www.sozcu.com.tr/2025/gundem/son-dakika-haberi-rusen-cakir-gozaltina-alindi-8423910/',
        'newspaper4k_issue': '404 error'
    },
    {
        'name': 'NTV Gallery - 404 error',
        'url': 'https://www.ntv.com.tr/galeri/turkiye/son-dakika-gaziantepte-deprem-kandilli-ve-afad-son-depremler-listesi,9kQ8R0F5pESlN-Nn6_jYxg',
        'newspaper4k_issue': '404 error (gallery format)'
    },
    {
        'name': 'Cumhuriyet - Wrong article',
        'url': 'https://www.cumhuriyet.com.tr/turkiye/turkiye-vize-kolayligi-getirilen-ulkeler-listesi-listede-hangi-ulkeler-var-2261093',
        'newspaper4k_issue': 'Extracted different article'
    },
]

# Also test on known-good URLs
good_urls = [
    {
        'name': 'Bianet (baseline)',
        'url': 'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281',
        'newspaper4k_issue': 'none'
    },
    {
        'name': 'OdaTV (good)',
        'url': 'https://www.odatv.com/guncel/akran-zorbaligi-davasinda-karar-cikti-120122351',
        'newspaper4k_issue': 'none'
    },
]

test_urls = problem_urls + good_urls

print("=" * 80)
print("ULTIMATE COMBO TEST")
print("=" * 80)
print("Newspaper4k (primary) → Trafilatura JSON (fallback)")
print()

results = []

for test in test_urls:
    name = test['name']
    url = test['url']
    issue = test['newspaper4k_issue']

    print(f"\n{'=' * 80}")
    print(f"{name}")
    print(f"URL: {url}")
    print(f"Newspaper4k issue: {issue}")
    print("-" * 80)

    result = {
        'name': name,
        'url': url,
        'n4k_issue': issue
    }

    # ========================================================================
    # STEP 1: Try Newspaper4k (primary)
    # ========================================================================

    print("\n1️⃣  NEWSPAPER4K (primary)")

    n4k_success = False
    n4k_time = 0

    try:
        start = time.time()

        config = Config()
        config.language = 'tr'
        config.request_timeout = 10

        article = Article(url, config=config)
        article.download()
        article.parse()

        n4k_time = time.time() - start

        # Consider successful if we got meaningful text
        has_text = len(article.text) > 100

        if has_text:
            n4k_success = True
            result.update({
                'method': 'newspaper4k',
                'success': True,
                'time': n4k_time,
                'title': article.title,
                'text_length': len(article.text),
                'authors': article.authors,
                'date': str(article.publish_date) if article.publish_date else None,
                'keywords': article.meta_keywords,
            })

            print(f"   ✅ SUCCESS ({n4k_time:.2f}s)")
            print(f"      Title: {article.title}")
            print(f"      Text: {len(article.text)} chars")
            print(f"      Keywords: {article.meta_keywords}")
            print(f"   → Using Newspaper4k result (no fallback needed)")

        else:
            print(f"   ⚠️  Downloaded but empty text ({n4k_time:.2f}s)")
            print(f"      Title: {article.title}")
            print(f"      Text: {len(article.text)} chars (too short)")
            print(f"   → Falling back to Trafilatura...")

    except Exception as e:
        n4k_time = time.time() - start if 'start' in locals() else 0
        print(f"   ❌ FAILED ({n4k_time:.2f}s)")
        print(f"      Error: {str(e)[:150]}")
        print(f"   → Falling back to Trafilatura...")

    # ========================================================================
    # STEP 2: Try Trafilatura (fallback) if Newspaper4k failed
    # ========================================================================

    if not n4k_success:
        print("\n2️⃣  TRAFILATURA JSON (fallback)")

        try:
            start = time.time()

            # Download with user-agent
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            html = response.text

            # Extract with Trafilatura
            traf_json_str = trafilatura.extract(
                html,
                output_format='json',
                include_comments=False,
                include_tables=True,
                with_metadata=True
            )

            traf_time = time.time() - start

            if traf_json_str:
                traf_data = json.loads(traf_json_str)
                text_length = len(traf_data.get('text', ''))

                if text_length > 100:
                    result.update({
                        'method': 'trafilatura',
                        'success': True,
                        'time': n4k_time + traf_time,
                        'title': traf_data.get('title'),
                        'text_length': text_length,
                        'authors': [traf_data.get('author')] if traf_data.get('author') else [],
                        'date': traf_data.get('date'),
                        'keywords': traf_data.get('tags', '').split(',') if traf_data.get('tags') else [],
                        'categories': traf_data.get('categories'),
                    })

                    print(f"   ✅ SUCCESS ({traf_time:.2f}s)")
                    print(f"      Title: {traf_data.get('title')}")
                    print(f"      Text: {text_length} chars")
                    print(f"      Tags: {traf_data.get('tags')}")
                    print(f"      Categories: {traf_data.get('categories')}")
                    print(f"   → Trafilatura rescued the extraction! ✨")

                else:
                    print(f"   ⚠️  Extracted but too short ({traf_time:.2f}s)")
                    print(f"      Text: {text_length} chars")
                    result.update({
                        'method': 'trafilatura',
                        'success': False,
                        'time': n4k_time + traf_time,
                        'error': f'Text too short: {text_length} chars'
                    })
            else:
                print(f"   ❌ No content extracted ({traf_time:.2f}s)")
                result.update({
                    'method': 'trafilatura',
                    'success': False,
                    'time': n4k_time + traf_time,
                    'error': 'No content extracted'
                })

        except Exception as e:
            traf_time = time.time() - start if 'start' in locals() else 0
            print(f"   ❌ FAILED ({traf_time:.2f}s)")
            print(f"      Error: {str(e)[:150]}")
            result.update({
                'method': 'trafilatura',
                'success': False,
                'time': n4k_time + traf_time,
                'error': str(e)[:200]
            })

    # ========================================================================
    # FINAL RESULT
    # ========================================================================

    if not result.get('success'):
        result['success'] = False
        result['method'] = 'both_failed'
        print("\n   ❌ BOTH methods failed")

    results.append(result)

# ============================================================================
# SUMMARY
# ============================================================================

print("\n\n" + "=" * 80)
print("ULTIMATE COMBO SUMMARY")
print("=" * 80)
print()

successful = sum(1 for r in results if r.get('success'))
total = len(results)

print(f"Overall success rate: {successful}/{total} ({successful/total*100:.1f}%)")
print()

# Method breakdown
print("Method used for successful extractions:")
print("-" * 80)

n4k_wins = sum(1 for r in results if r.get('method') == 'newspaper4k')
traf_wins = sum(1 for r in results if r.get('method') == 'trafilatura')
both_failed = sum(1 for r in results if r.get('method') == 'both_failed')

print(f"   Newspaper4k (primary):     {n4k_wins}/{total} ({n4k_wins/total*100:.0f}%)")
print(f"   Trafilatura (fallback):    {traf_wins}/{total} ({traf_wins/total*100:.0f}%)")
print(f"   Both failed:               {both_failed}/{total} ({both_failed/total*100:.0f}%)")
print()

if traf_wins > 0:
    print(f"🎯 Trafilatura fallback rescued {traf_wins} extraction{'s' if traf_wins != 1 else ''}!")
    print()

# Performance
print("Performance:")
print("-" * 80)

successful_results = [r for r in results if r.get('success')]
if successful_results:
    avg_time = sum(r['time'] for r in successful_results) / len(successful_results)
    print(f"   Average time: {avg_time:.2f}s")

    n4k_times = [r['time'] for r in successful_results if r.get('method') == 'newspaper4k']
    traf_times = [r['time'] for r in successful_results if r.get('method') == 'trafilatura']

    if n4k_times:
        print(f"   Newspaper4k avg: {sum(n4k_times)/len(n4k_times):.2f}s")
    if traf_times:
        print(f"   With fallback avg: {sum(traf_times)/len(traf_times):.2f}s")

print()

# URL-by-URL results
print("Detailed results:")
print("-" * 80)

for r in results:
    status = "✅" if r.get('success') else "❌"
    method = r.get('method', 'unknown')

    print(f"\n{status} {r['name']}")
    print(f"   Original issue: {r['n4k_issue']}")

    if r.get('success'):
        print(f"   Solved by: {method}")
        print(f"   Time: {r['time']:.2f}s")
        print(f"   Text: {r['text_length']} chars")
    else:
        print(f"   Method tried: {method}")
        if r.get('error'):
            print(f"   Error: {r['error'][:100]}")

# ============================================================================
# FINAL VERDICT
# ============================================================================

print("\n\n" + "=" * 80)
print("FINAL VERDICT: ULTIMATE COMBO")
print("=" * 80)
print()

if successful == total:
    print("🏆 PERFECT SCORE!")
    print(f"   {successful}/{total} URLs extracted successfully")
    print()
    print("   The two-tier approach handles ALL edge cases!")

elif successful >= total * 0.8:
    print("✅ EXCELLENT!")
    print(f"   {successful}/{total} URLs extracted successfully ({successful/total*100:.0f}%)")
    print()
    if traf_wins > 0:
        print(f"   Trafilatura fallback saved {traf_wins} extraction(s)")
    print()
    print("   Recommendation: Deploy this combo in production")

else:
    print(f"⚠️  GOOD but not perfect")
    print(f"   {successful}/{total} URLs extracted ({successful/total*100:.0f}%)")
    print()
    failed = [r for r in results if not r.get('success')]
    print(f"   Still failed on:")
    for r in failed:
        print(f"   - {r['name']}")

print()
print("=" * 80)
print("PRODUCTION RECOMMENDATION")
print("=" * 80)
print()

print("Use this extraction strategy:")
print()
print("```python")
print("def extract_article(url):")
print("    # Try Newspaper4k first (fast, clean)")
print("    try:")
print("        article = newspaper4k.extract(url)")
print("        if len(article.text) > 100:")
print("            return article")
print("    except:")
print("        pass")
print()
print("    # Fallback to Trafilatura (slower but more robust)")
print("    html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text")
print("    return trafilatura.extract(html, output_format='json')")
print("```")
print()
print(f"Expected success rate: {successful/total*100:.0f}%")
print(f"Primary method (Newspaper4k): {n4k_wins/total*100:.0f}% of cases")
print(f"Fallback needed: {traf_wins/total*100:.0f}% of cases")
print()
print("=" * 80)

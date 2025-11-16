#!/usr/bin/env python3
"""
Test Trafilatura JSON with user-agent bypass
Compare structured output with Newspaper4k
"""

import requests
import trafilatura
from newspaper import Article, Config
import json

# Test URLs
test_urls = [
    {
        'name': 'bianet_1',
        'url': 'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281'
    },
    {
        'name': 'bianet_2',
        'url': 'https://bianet.org/haber/iklim-agindan-turkiyeye-emisyonlari-azaltmadan-iklim-kriziyle-mucadele-edilemez-313275'
    },
    {
        'name': 'bianet_3',
        'url': 'https://bianet.org/haber/gazetecilere-operasyon-yalcin-cakir-oghan-sevinc-ve-colak-serbest-313253'
    },
]

print("=" * 80)
print("TRAFILATURA JSON WITH USER-AGENT BYPASS TEST")
print("=" * 80)
print()

results = []

for test in test_urls:
    name = test['name']
    url = test['url']

    print(f"Testing: {name}")
    print(f"URL: {url}")
    print("-" * 80)

    result = {
        'name': name,
        'url': url
    }

    # ========================================================================
    # Method 1: Newspaper4k (baseline)
    # ========================================================================

    print("\n1. NEWSPAPER4K")
    try:
        config = Config()
        config.language = 'tr'
        article = Article(url, config=config)
        article.download()
        article.parse()

        n4k_data = {
            'title': article.title,
            'authors': article.authors,
            'date': str(article.publish_date) if article.publish_date else None,
            'text': article.text,
            'text_length': len(article.text),
            'top_image': article.top_image,
        }

        print(f"   ✅ Success")
        print(f"   Title: {n4k_data['title']}")
        print(f"   Authors: {n4k_data['authors']}")
        print(f"   Date: {n4k_data['date']}")
        print(f"   Text length: {n4k_data['text_length']} chars")
        print(f"   Image: {n4k_data['top_image'][:60] if n4k_data['top_image'] else 'None'}...")

        result['newspaper4k'] = n4k_data

    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        result['newspaper4k'] = None

    # ========================================================================
    # Method 2: Trafilatura JSON with user-agent bypass
    # ========================================================================

    print("\n2. TRAFILATURA JSON (with user-agent bypass)")
    try:
        # Download with proper user-agent
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = response.text

        # Extract with Trafilatura JSON
        traf_json_str = trafilatura.extract(
            html,
            output_format='json',
            include_comments=False,
            include_tables=True,
            with_metadata=True
        )

        if traf_json_str:
            traf_data = json.loads(traf_json_str)

            print(f"   ✅ Success")
            print(f"   Title: {traf_data.get('title')}")
            print(f"   Author: {traf_data.get('author')}")
            print(f"   Date: {traf_data.get('date')}")
            print(f"   Text length: {len(traf_data.get('text', ''))} chars")
            print(f"   Image: {traf_data.get('image', 'None')[:60] if traf_data.get('image') else 'None'}...")
            print(f"   Tags: {traf_data.get('tags')}")
            print(f"   Categories: {traf_data.get('categories')}")

            result['trafilatura'] = traf_data
        else:
            print(f"   ❌ No content extracted")
            result['trafilatura'] = None

    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")
        result['trafilatura'] = None

    # ========================================================================
    # Comparison
    # ========================================================================

    print("\n3. COMPARISON")

    if result.get('newspaper4k') and result.get('trafilatura'):
        n4k = result['newspaper4k']
        traf = result['trafilatura']

        print(f"   Title match: {n4k['title'] == traf.get('title')}")
        print(f"   Text length: N4K={n4k['text_length']} vs Traf={len(traf.get('text', ''))}")

        # Check content overlap
        n4k_words = set(n4k['text'].split())
        traf_words = set(traf.get('text', '').split())
        overlap = len(n4k_words & traf_words)
        similarity = (overlap / len(n4k_words) * 100) if n4k_words else 0

        print(f"   Content similarity: {similarity:.1f}% word overlap")

        if abs(n4k['text_length'] - len(traf.get('text', ''))) < 100:
            print(f"   ✅ Very similar content")
        elif similarity > 80:
            print(f"   ✅ High content overlap")
        else:
            print(f"   ⚠️  Content differs significantly")

    elif result.get('newspaper4k'):
        print(f"   Newspaper4k works, Trafilatura failed")
    elif result.get('trafilatura'):
        print(f"   Trafilatura works, Newspaper4k failed")
    else:
        print(f"   Both methods failed")

    results.append(result)
    print("\n" + "=" * 80 + "\n")


# ============================================================================
# Summary
# ============================================================================

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

n4k_success = sum(1 for r in results if r.get('newspaper4k'))
traf_success = sum(1 for r in results if r.get('trafilatura'))

print(f"Success Rates:")
print(f"  Newspaper4k:     {n4k_success}/{len(results)} ({n4k_success/len(results)*100:.1f}%)")
print(f"  Trafilatura JSON: {traf_success}/{len(results)} ({traf_success/len(results)*100:.1f}%)")
print()

print("Structured Output Comparison:")
print("-" * 80)

for r in results:
    print(f"\n{r['name']}:")

    if r.get('newspaper4k'):
        n4k = r['newspaper4k']
        print(f"  Newspaper4k:")
        print(f"    - title: ✅")
        print(f"    - authors: {'✅' if n4k['authors'] else '❌'}")
        print(f"    - date: {'✅' if n4k['date'] else '❌'}")
        print(f"    - text: ✅ ({n4k['text_length']} chars)")
        print(f"    - image: {'✅' if n4k['top_image'] else '❌'}")
    else:
        print(f"  Newspaper4k: ❌ Failed")

    if r.get('trafilatura'):
        traf = r['trafilatura']
        print(f"  Trafilatura JSON:")
        print(f"    - title: ✅")
        print(f"    - author: {'✅' if traf.get('author') else '❌'}")
        print(f"    - date: {'✅' if traf.get('date') else '❌'}")
        print(f"    - text: ✅ ({len(traf.get('text', ''))} chars)")
        print(f"    - image: {'✅' if traf.get('image') else '❌'}")
        print(f"    - tags: {'✅' if traf.get('tags') else '❌'}")
        print(f"    - categories: {'✅' if traf.get('categories') else '❌'}")
    else:
        print(f"  Trafilatura JSON: ❌ Failed")


print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)
print()

if traf_success == len(results) and n4k_success == len(results):
    print("✅ BOTH methods work with user-agent bypass!")
    print()
    print("Recommendation:")
    print("  - Use Newspaper4k for simplicity (default library)")
    print("  - Use Trafilatura JSON for richer metadata (tags, categories)")
    print("  - NO need for LLM hybrid approach")
    print()
    print("Trafilatura JSON advantages:")
    print("  ✅ Tags and categories")
    print("  ✅ Excerpt/description")
    print("  ✅ Multiple text formats (text, raw_text)")
    print("  ✅ More metadata fields")

elif traf_success > n4k_success:
    print("✅ Trafilatura JSON works better with user-agent bypass!")
    print()
    print("Recommendation:")
    print("  - Use Trafilatura JSON as primary")
    print("  - Fallback to Newspaper4k if needed")

elif n4k_success == len(results):
    print("✅ Newspaper4k is still the winner!")
    print()
    if traf_success == 0:
        print("Trafilatura JSON failed even with user-agent bypass")
    else:
        print(f"Trafilatura JSON only worked on {traf_success}/{len(results)} URLs")
    print()
    print("Recommendation:")
    print("  - Stick with Newspaper4k (proven 100% success)")

else:
    print("⚠️  Mixed results")
    print()
    print("Recommendation:")
    print("  - Use Newspaper4k as primary")
    print("  - Consider fallback chain if needed")

print("=" * 80)

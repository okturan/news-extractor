#!/usr/bin/env python3
"""
Test edge cases that Expert 2 raised:
1. Paywalled content
2. Live blogs / continuously updating content
3. Embedded social media (Twitter, Instagram)
4. Video-first articles
"""

import requests
from newspaper import Article, Config
from bs4 import BeautifulSoup

# Edge case test URLs
test_cases = [
    {
        'name': 'Regular article (baseline)',
        'url': 'https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281',
        'edge_case': 'none',
        'expected': 'Should extract cleanly'
    },
    {
        'name': 'Article with embedded tweets',
        'url': 'https://www.sozcu.com.tr/2025/gundem/son-dakika-haberi-rusen-cakir-gozaltina-alindi-8423910/',
        'edge_case': 'embedded_social_media',
        'expected': 'Should skip Twitter embeds, extract text'
    },
    {
        'name': 'Cumhuriyet article (potential paywall)',
        'url': 'https://www.cumhuriyet.com.tr/turkiye/turkiye-vize-kolayligi-getirilen-ulkeler-listesi-listede-hangi-ulkeler-var-2261093',
        'edge_case': 'potential_paywall',
        'expected': 'Check if paywall blocks extraction'
    },
    {
        'name': 'Video-heavy article',
        'url': 'https://www.hurriyet.com.tr/galeri/trabzonspor-fenerbahceden-ryan-kent-transferini-acikladi-42246515',
        'edge_case': 'video_gallery',
        'expected': 'Should extract text around video/gallery'
    },
    {
        'name': 'Live blog / minute-by-minute',
        'url': 'https://www.ntv.com.tr/canli-yayin',
        'edge_case': 'live_content',
        'expected': 'May fail or extract partial content'
    },
]

print("=" * 80)
print("EDGE CASE TESTING")
print("=" * 80)
print("Testing Newspaper4k against real-world edge cases")
print()

results = []

for test in test_cases:
    name = test['name']
    url = test['url']
    edge_case = test['edge_case']
    expected = test['expected']

    print(f"\n{'=' * 80}")
    print(f"Test: {name}")
    print(f"URL: {url}")
    print(f"Edge case: {edge_case}")
    print(f"Expected: {expected}")
    print("-" * 80)

    result = {
        'name': name,
        'url': url,
        'edge_case': edge_case
    }

    # Test with Newspaper4k
    try:
        config = Config()
        config.language = 'tr'
        article = Article(url, config=config)
        article.download()
        article.parse()

        text_length = len(article.text)
        has_text = text_length > 100

        # Check for edge case indicators in extracted text
        text_lower = article.text.lower()

        # Check for paywall indicators
        paywall_indicators = ['üye ol', 'abone ol', 'giriş yap', 'premium', 'devamını oku']
        has_paywall = any(indicator in text_lower for indicator in paywall_indicators)

        # Check for embedded content artifacts
        embed_artifacts = ['twitter.com', 'instagram.com', 'youtube.com', 'iframe']
        has_embeds = any(artifact in text_lower for artifact in embed_artifacts)

        # Check for video indicators
        video_indicators = ['video', 'izle', 'oynat']
        has_video_refs = any(indicator in text_lower for indicator in video_indicators)

        result.update({
            'success': True,
            'title': article.title,
            'text_length': text_length,
            'has_meaningful_text': has_text,
            'paywall_detected': has_paywall,
            'embed_artifacts': has_embeds,
            'video_references': has_video_refs,
            'meta_keywords': article.meta_keywords,
        })

        print(f"✅ Extraction successful")
        print(f"   Title: {article.title}")
        print(f"   Text length: {text_length} chars")
        print(f"   Has meaningful text: {'✅' if has_text else '❌ TOO SHORT'}")

        if has_paywall:
            print(f"   ⚠️  Paywall indicators detected in text")

        if has_embeds:
            print(f"   ⚠️  Social media embed artifacts in text")

        if has_video_refs:
            print(f"   ℹ️  Video references found")

        print(f"   Meta keywords: {article.meta_keywords}")

        # Show preview
        if text_length > 0:
            print(f"\n   Preview (first 300 chars):")
            print(f"   {article.text[:300]}...")

    except Exception as e:
        result.update({
            'success': False,
            'error': str(e)[:200]
        })
        print(f"❌ Failed: {str(e)[:200]}")

    results.append(result)

# Summary
print("\n\n" + "=" * 80)
print("EDGE CASE SUMMARY")
print("=" * 80)
print()

successful = sum(1 for r in results if r.get('success'))
print(f"Success rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
print()

print("Results by edge case:")
print("-" * 80)

for r in results:
    status = "✅" if r.get('success') else "❌"
    edge = r['edge_case']

    print(f"\n{status} {r['name']}")
    print(f"   Edge case: {edge}")

    if r.get('success'):
        has_text = r.get('has_meaningful_text', False)
        text_len = r.get('text_length', 0)

        print(f"   Extracted: {text_len} chars {'✅' if has_text else '❌ TOO SHORT'}")

        # Edge case specific analysis
        if edge == 'potential_paywall':
            if r.get('paywall_detected'):
                print(f"   ⚠️  Paywall: Paywall indicators found in text")
                print(f"      → May have extracted paywall message instead of article")
            else:
                print(f"   ✅ Paywall: No paywall detected, full text extracted")

        elif edge == 'embedded_social_media':
            if r.get('embed_artifacts'):
                print(f"   ⚠️  Embeds: Social media URLs in extracted text")
                print(f"      → May need cleaning to remove embed artifacts")
            else:
                print(f"   ✅ Embeds: Clean extraction, no embed artifacts")

        elif edge == 'video_gallery':
            if text_len < 200:
                print(f"   ⚠️  Video-first: Very short text ({text_len} chars)")
                print(f"      → May be primarily video content")
            else:
                print(f"   ✅ Video-first: Adequate text extracted alongside video")

        elif edge == 'live_content':
            if text_len > 500:
                print(f"   ✅ Live content: Extracted snapshot ({text_len} chars)")
            else:
                print(f"   ⚠️  Live content: Minimal text ({text_len} chars)")
    else:
        print(f"   Error: {r.get('error', 'Unknown')[:100]}")

# Recommendations
print("\n\n" + "=" * 80)
print("EDGE CASE RECOMMENDATIONS")
print("=" * 80)
print()

paywall_tests = [r for r in results if r['edge_case'] == 'potential_paywall' and r.get('success')]
if paywall_tests:
    if any(r.get('paywall_detected') for r in paywall_tests):
        print("⚠️  PAYWALLS:")
        print("   - Paywall indicators detected in extracted text")
        print("   - Recommendation: Check text for 'üye ol', 'abone ol' keywords")
        print("   - May need premium account or different extraction method")
    else:
        print("✅ PAYWALLS: No issues detected")
    print()

embed_tests = [r for r in results if r['edge_case'] == 'embedded_social_media' and r.get('success')]
if embed_tests:
    if any(r.get('embed_artifacts') for r in embed_tests):
        print("⚠️  EMBEDDED SOCIAL MEDIA:")
        print("   - Social media URLs appear in extracted text")
        print("   - Recommendation: Post-process to remove 'twitter.com', 'instagram.com' artifacts")
    else:
        print("✅ EMBEDDED SOCIAL MEDIA: Cleanly filtered out")
    print()

video_tests = [r for r in results if r['edge_case'] == 'video_gallery' and r.get('success')]
if video_tests:
    short_videos = [r for r in video_tests if r.get('text_length', 0) < 200]
    if short_videos:
        print("⚠️  VIDEO-FIRST ARTICLES:")
        print("   - Very short text extracted from video-heavy pages")
        print("   - Recommendation: May need video metadata extraction, not just text")
    else:
        print("✅ VIDEO-FIRST ARTICLES: Text extracted alongside videos")
    print()

live_tests = [r for r in results if r['edge_case'] == 'live_content' and r.get('success')]
if live_tests:
    print("ℹ️  LIVE CONTENT:")
    print("   - Live blogs return snapshot of current state")
    print("   - Recommendation: Re-fetch periodically for updates if needed")
    print()

print("=" * 80)
print("FINAL VERDICT ON EDGE CASES")
print("=" * 80)
print()

if successful == len(results):
    print("✅ All edge cases handled!")
    print("   Newspaper4k extracts content from all tested scenarios.")
    print()
    print("   Minor cleanup may be needed for:")
    print("   - Social media embed artifacts")
    print("   - Paywall detection (check for keywords)")
    print("   - Video-first articles (may be short text)")
else:
    failed = len(results) - successful
    print(f"⚠️  {failed}/{len(results)} edge cases failed")
    print()
    print("   May need:")
    print("   - Alternative extraction method for failed cases")
    print("   - Fallback to Trafilatura or browser-based extraction")

print("=" * 80)

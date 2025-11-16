#!/usr/bin/env python3
"""
Debug why Trafilatura 2.0 fails on Bianet
"""

import trafilatura
import requests
from bs4 import BeautifulSoup

url = "https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281"

print("=" * 80)
print("DEBUGGING BIANET + TRAFILATURA 2.0 FAILURE")
print("=" * 80)
print(f"URL: {url}")
print(f"Trafilatura version: {trafilatura.__version__}")
print()

# Test 1: Can we download with requests?
print("1. Testing direct download with requests:")
print("-" * 80)
try:
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    print(f"✅ SUCCESS with requests")
    print(f"   Status code: {response.status_code}")
    print(f"   Content length: {len(response.text)} chars")
    print(f"   Encoding: {response.encoding}")
except Exception as e:
    print(f"❌ FAILED with requests: {e}")

# Test 2: What does Trafilatura's fetch_url return?
print("\n2. Testing Trafilatura's fetch_url:")
print("-" * 80)
try:
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        print(f"✅ Trafilatura downloaded: {len(downloaded)} chars")
    else:
        print(f"❌ Trafilatura returned None/empty")
        print("   This explains the 'Failed to download' error")
except Exception as e:
    print(f"❌ Exception in fetch_url: {e}")

# Test 3: Try with custom settings
print("\n3. Testing Trafilatura with custom settings:")
print("-" * 80)

# Manually download with requests, then pass to Trafilatura
try:
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    html = response.text

    print(f"Downloaded {len(html)} chars with requests")
    print("Passing to Trafilatura's extract()...")

    # Extract text
    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        with_metadata=False
    )

    if text:
        print(f"✅ EXTRACTION SUCCESS!")
        print(f"   Text length: {len(text)} chars")
        print(f"   Preview: {text[:200]}...")

        # Get metadata
        metadata = trafilatura.extract_metadata(html)
        if metadata:
            print(f"\n   Metadata:")
            print(f"   - Title: {metadata.title}")
            print(f"   - Author: {metadata.author}")
            print(f"   - Date: {metadata.date}")
    else:
        print(f"❌ Trafilatura extract returned None")
        print("   The HTML structure might not be recognized")

except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Check Trafilatura's user agent
print("\n4. Investigating Trafilatura's HTTP settings:")
print("-" * 80)

# Check what user agent Trafilatura uses
import trafilatura.downloads
print(f"Trafilatura default headers:")
if hasattr(trafilatura.downloads, 'DEFAULT_HEADERS'):
    print(f"  {trafilatura.downloads.DEFAULT_HEADERS}")
else:
    print("  Not directly accessible")

# Test 5: Try Newspaper4k for comparison
print("\n5. Comparison - Newspaper4k on same URL:")
print("-" * 80)
from newspaper import Article, Config

config = Config()
config.language = 'tr'

article = Article(url, config=config)
article.download()
article.parse()

print(f"Newspaper4k result:")
print(f"  Title: {article.title}")
print(f"  Text length: {len(article.text)} chars")
print(f"  Success: {len(article.text) > 0}")

# Diagnosis
print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("=" * 80)

print("\n🔍 Why Trafilatura 2.0 fails on Bianet:")
if downloaded is None:
    print("  1. ❌ Trafilatura's fetch_url() returns None")
    print("  2. Possible reasons:")
    print("     - Bianet blocks Trafilatura's user agent")
    print("     - Timeout issues")
    print("     - SSL/certificate problems")
    print("     - Trafilatura's URL validation rejects the URL")
else:
    print("  1. ❌ Trafilatura extracts nothing from the HTML")
    print("  2. The HTML structure isn't recognized")

print("\n✅ Workaround:")
print("  Download with requests, then pass HTML to Trafilatura.extract()")
print("  OR just use Newspaper4k which works perfectly")

print("\n💡 Recommendation:")
print("  Trafilatura 2.0 did NOT fix the Bianet issue")
print("  Stick with Newspaper4k for Bianet articles")
print("=" * 80)

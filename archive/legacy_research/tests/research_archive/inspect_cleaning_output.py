#!/usr/bin/env python3
"""
Inspect what Trafilatura and Readability actually output
"""

import requests
from readability import Document
import trafilatura
from bs4 import BeautifulSoup

url = "https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281"

print("=" * 80)
print("INSPECT PRE-CLEANING OUTPUT")
print("=" * 80)
print()

# Download
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
html = response.text

# ============================================================================
# 1. Readability Output
# ============================================================================

print("1. MOZILLA READABILITY OUTPUT")
print("=" * 80)

doc = Document(html)
readability_html = doc.summary()
readability_title = doc.title()

print(f"Title: {readability_title}")
print(f"Length: {len(readability_html)} bytes")
print()
print("Full output:")
print("-" * 80)
print(readability_html)
print()

# ============================================================================
# 2. Trafilatura XML Output
# ============================================================================

print("\n" + "=" * 80)
print("2. TRAFILATURA XML OUTPUT")
print("=" * 80)

traf_xml = trafilatura.extract(
    html,
    output_format='xml',
    include_comments=False,
    include_tables=True,
    with_metadata=True
)

print(f"Length: {len(traf_xml)} bytes")
print()
print("Full output:")
print("-" * 80)
print(traf_xml)
print()

# ============================================================================
# 3. Trafilatura Plain Text (what we used before)
# ============================================================================

print("\n" + "=" * 80)
print("3. TRAFILATURA PLAIN TEXT (what we used before)")
print("=" * 80)

traf_text = trafilatura.extract(
    html,
    include_comments=False,
    include_tables=True,
    with_metadata=False
)

print(f"Length: {len(traf_text)} bytes")
print()
print("Full output:")
print("-" * 80)
print(traf_text)
print()

# ============================================================================
# 4. Trafilatura JSON Output
# ============================================================================

print("\n" + "=" * 80)
print("4. TRAFILATURA JSON OUTPUT")
print("=" * 80)

traf_json = trafilatura.extract(
    html,
    output_format='json',
    include_comments=False,
    include_tables=True,
    with_metadata=True
)

print(f"Length: {len(traf_json)} bytes")
print()
print("Full output:")
print("-" * 80)
print(traf_json)
print()

# ============================================================================
# Analysis
# ============================================================================

print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)
print()

print("What does each method produce?")
print("-" * 80)

print("\n1. Readability:")
print("   - Produces: Cleaned HTML (still has tags like <p>, <a>, <div>)")
print("   - Structure: HTML fragments")
print("   - Metadata: Just title")
print("   - Use case: Needs further parsing OR send to LLM to extract structured data")

print("\n2. Trafilatura XML:")
print("   - Produces: XML with article structure")
print("   - Has metadata tags: <doc>, <title>, <author>, <date>")
print("   - Content: Text with some structure preserved")
print("   - Use case: Semi-structured, still needs parsing OR LLM extraction")

print("\n3. Trafilatura Plain Text:")
print("   - Produces: Clean plain text")
print("   - NO HTML tags")
print("   - NO metadata")
print("   - Use case: Already extracted! This is what Newspaper4k gives us")

print("\n4. Trafilatura JSON:")
print("   - Produces: Structured JSON")
print("   - Has: title, author, date, text, url, etc.")
print("   - Use case: Already structured! Similar to Newspaper4k output")

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()

print("❓ Do we need LLM if Trafilatura JSON already gives structured output?")
print()
print("Answer: It depends!")
print()
print("If Trafilatura JSON works reliably:")
print("  ✅ Use Trafilatura JSON (free, fast)")
print("  ❌ No need for LLM")
print()
print("If Trafilatura JSON has issues (like it did with Bianet user-agent):")
print("  ✅ Use Readability/Trafilatura XML → LLM")
print("  ✅ LLM can handle edge cases, weird HTML structures")
print("  ✅ Cost: ~$0.0002 per article (affordable)")
print()
print("The hybrid approach makes sense when:")
print("  - Trafilatura/Newspaper4k fail on specific sites")
print("  - You need better metadata extraction")
print("  - You want to handle weird HTML edge cases")
print("  - You're willing to pay $0.0002-0.001 per article for robustness")

print("=" * 80)

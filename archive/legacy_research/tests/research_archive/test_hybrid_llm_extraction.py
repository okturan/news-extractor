#!/usr/bin/env python3
"""
Hybrid LLM Extraction: Pre-clean HTML → LLM for precise extraction
Test if this is cost-effective and better than Newspaper4k
"""

import requests
from newspaper import Article, Config
import trafilatura
from readability import Document
from bs4 import BeautifulSoup
import anthropic
import os
import json
import tiktoken

url = "https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281"

print("=" * 80)
print("HYBRID LLM EXTRACTION TEST")
print("=" * 80)
print(f"URL: {url}")
print()

# Download HTML once
print("Downloading HTML...")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
raw_html = response.text
raw_html_size = len(raw_html)

print(f"✅ Raw HTML: {raw_html_size:,} bytes")
print()


# ============================================================================
# STEP 1: Test different pre-cleaning methods
# ============================================================================

print("=" * 80)
print("STEP 1: PRE-CLEANING METHODS")
print("=" * 80)
print()

cleaning_results = {}

# Method 1: Mozilla Readability
print("1. MOZILLA READABILITY")
print("-" * 80)
try:
    doc = Document(raw_html)
    readability_html = doc.summary()
    readability_title = doc.title()

    # Remove scripts, styles from readability output
    soup = BeautifulSoup(readability_html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    readability_cleaned = str(soup)

    readability_size = len(readability_cleaned)
    reduction = (1 - readability_size / raw_html_size) * 100

    print(f"✅ Success")
    print(f"   Size: {readability_size:,} bytes ({reduction:.1f}% reduction)")
    print(f"   Title: {readability_title}")
    print(f"   Preview: {readability_cleaned[:200]}...")

    cleaning_results['readability'] = {
        'html': readability_cleaned,
        'size': readability_size,
        'title': readability_title
    }
except Exception as e:
    print(f"❌ Failed: {str(e)[:100]}")
    cleaning_results['readability'] = None

print()

# Method 2: Trafilatura (XML output)
print("2. TRAFILATURA (XML/HTML OUTPUT)")
print("-" * 80)
try:
    # Trafilatura can output clean HTML/XML
    traf_html = trafilatura.extract(
        raw_html,
        output_format='xml',
        include_comments=False,
        include_tables=True,
        with_metadata=True
    )

    traf_size = len(traf_html) if traf_html else 0
    reduction = (1 - traf_size / raw_html_size) * 100 if traf_html else 0

    if traf_html:
        print(f"✅ Success")
        print(f"   Size: {traf_size:,} bytes ({reduction:.1f}% reduction)")
        print(f"   Preview: {traf_html[:200]}...")

        cleaning_results['trafilatura'] = {
            'html': traf_html,
            'size': traf_size
        }
    else:
        print(f"❌ No content extracted")
        cleaning_results['trafilatura'] = None

except Exception as e:
    print(f"❌ Failed: {str(e)[:100]}")
    cleaning_results['trafilatura'] = None

print()

# Method 3: Custom BeautifulSoup cleaning
print("3. CUSTOM BEAUTIFULSOUP CLEANING")
print("-" * 80)
try:
    soup = BeautifulSoup(raw_html, 'html.parser')

    # Remove noise tags
    for tag in soup(['script', 'style', 'noscript', 'iframe', 'nav', 'footer', 'aside', 'header']):
        tag.decompose()

    # Remove comment nodes
    for comment in soup.findAll(text=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
        comment.extract()

    # Try to find main content area
    main_content = soup.find('article') or soup.find('main') or soup.find('div', class_=['article-content', 'content', 'post-content'])

    if main_content:
        custom_html = str(main_content)
    else:
        # Fallback: just cleaned body
        custom_html = str(soup.body) if soup.body else str(soup)

    custom_size = len(custom_html)
    reduction = (1 - custom_size / raw_html_size) * 100

    print(f"✅ Success")
    print(f"   Size: {custom_size:,} bytes ({reduction:.1f}% reduction)")
    print(f"   Preview: {custom_html[:200]}...")

    cleaning_results['custom'] = {
        'html': custom_html,
        'size': custom_size
    }
except Exception as e:
    print(f"❌ Failed: {str(e)[:100]}")
    cleaning_results['custom'] = None

print()


# ============================================================================
# STEP 2: Token counting for each method
# ============================================================================

print("=" * 80)
print("STEP 2: TOKEN ANALYSIS")
print("=" * 80)
print()

# Use tiktoken to estimate tokens (Claude uses similar tokenization)
try:
    encoding = tiktoken.get_encoding("cl100k_base")  # Similar to Claude

    print("Token counts:")
    print("-" * 80)

    for method, result in cleaning_results.items():
        if result:
            tokens = len(encoding.encode(result['html']))
            print(f"{method:15} {tokens:6,} tokens  ({result['size']:,} bytes)")
            result['tokens'] = tokens
        else:
            print(f"{method:15} FAILED")

    # Raw HTML for comparison
    raw_tokens = len(encoding.encode(raw_html))
    print(f"{'raw_html':15} {raw_tokens:6,} tokens  ({raw_html_size:,} bytes)")

    print()
    print("Token reduction:")
    print("-" * 80)
    for method, result in cleaning_results.items():
        if result:
            reduction = (1 - result['tokens'] / raw_tokens) * 100
            print(f"{method:15} {reduction:5.1f}% reduction")

except Exception as e:
    print(f"⚠️  Token counting failed: {str(e)[:100]}")
    print("   Continuing without token counts...")

print()


# ============================================================================
# STEP 3: LLM Extraction (use best pre-cleaning method)
# ============================================================================

print("=" * 80)
print("STEP 3: LLM EXTRACTION")
print("=" * 80)
print()

# Find best cleaning method (smallest size that succeeded)
valid_methods = {k: v for k, v in cleaning_results.items() if v is not None}

if not valid_methods:
    print("❌ No cleaning method succeeded. Cannot test LLM extraction.")
    exit(1)

best_method = min(valid_methods.items(), key=lambda x: x[1]['size'])
method_name, method_result = best_method

print(f"Using: {method_name.upper()} ({method_result['size']:,} bytes, {method_result.get('tokens', 'N/A')} tokens)")
print()

# Check for Anthropic API key
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("⚠️  ANTHROPIC_API_KEY not found in environment")
    print("   Please set it to test LLM extraction:")
    print("   export ANTHROPIC_API_KEY='your-key-here'")
    print()
    print("   Skipping LLM extraction test.")
    llm_result = None
else:
    print("Testing LLM extraction with Claude Haiku...")
    print("-" * 80)

    try:
        client = anthropic.Anthropic(api_key=api_key)

        # Construct prompt
        prompt = f"""You are extracting structured data from a Turkish news article HTML.

Extract the following fields and return ONLY a JSON object:
- title: Article title
- author: Author name(s) (or null if not found)
- publish_date: Publication date in ISO format (or null if not found)
- content: The main article text only (no navigation, ads, related articles)

HTML to extract from:
{method_result['html']}

Return ONLY valid JSON, nothing else."""

        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        response_text = message.content[0].text

        # Get usage stats
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens

        # Calculate cost (Claude Haiku pricing)
        # Input: $0.25 per 1M tokens, Output: $1.25 per 1M tokens
        input_cost = (input_tokens / 1_000_000) * 0.25
        output_cost = (output_tokens / 1_000_000) * 1.25
        total_cost = input_cost + output_cost

        print(f"✅ LLM extraction successful")
        print(f"   Input tokens:  {input_tokens:,}")
        print(f"   Output tokens: {output_tokens:,}")
        print(f"   Cost: ${total_cost:.6f} per article")
        print()
        print("Extracted JSON:")
        print("-" * 80)

        # Try to pretty-print JSON
        try:
            json_data = json.loads(response_text)
            print(json.dumps(json_data, indent=2, ensure_ascii=False))

            llm_result = {
                'data': json_data,
                'tokens': {'input': input_tokens, 'output': output_tokens},
                'cost': total_cost
            }
        except json.JSONDecodeError:
            print(response_text)
            print()
            print("⚠️  Response is not valid JSON")
            llm_result = {
                'raw': response_text,
                'tokens': {'input': input_tokens, 'output': output_tokens},
                'cost': total_cost
            }

    except Exception as e:
        print(f"❌ LLM extraction failed: {str(e)[:200]}")
        llm_result = None

print()


# ============================================================================
# STEP 4: Comparison with Newspaper4k
# ============================================================================

print("=" * 80)
print("STEP 4: COMPARISON WITH NEWSPAPER4K")
print("=" * 80)
print()

print("Getting Newspaper4k result...")
print("-" * 80)

config = Config()
config.language = 'tr'
article = Article(url, config=config)
article.download()
article.parse()

n4k_text = article.text
n4k_title = article.title
n4k_authors = article.authors
n4k_date = article.publish_date

print(f"✅ Newspaper4k")
print(f"   Title: {n4k_title}")
print(f"   Authors: {n4k_authors}")
print(f"   Date: {n4k_date}")
print(f"   Content length: {len(n4k_text)} chars")
print(f"   Cost: $0 (free)")

print()


# ============================================================================
# FINAL COMPARISON
# ============================================================================

print("=" * 80)
print("FINAL VERDICT")
print("=" * 80)
print()

print("Extraction Quality:")
print("-" * 80)

if llm_result and 'data' in llm_result:
    llm_content = llm_result['data'].get('content', '')
    llm_title = llm_result['data'].get('title', '')

    print(f"  Newspaper4k content: {len(n4k_text):,} chars")
    print(f"  LLM content:         {len(llm_content):,} chars")
    print()

    # Check if LLM captured the same article
    overlap = len(set(n4k_text.split()) & set(llm_content.split()))
    n4k_words = len(n4k_text.split())
    similarity = (overlap / n4k_words * 100) if n4k_words > 0 else 0

    print(f"  Content similarity: {similarity:.1f}% word overlap")

print()

print("Cost Analysis:")
print("-" * 80)

if llm_result:
    cost_per_article = llm_result['cost']
    print(f"  Per article:      ${cost_per_article:.6f}")
    print(f"  Per 1,000:        ${cost_per_article * 1000:.4f}")
    print(f"  Per 100,000:      ${cost_per_article * 100000:.2f}")
    print()

    if cost_per_article < 0.001:
        print("  ✅ Very affordable (<$0.001 per article)")
    elif cost_per_article < 0.01:
        print("  ✅ Affordable (<$0.01 per article)")
    else:
        print("  ⚠️  Expensive for high-volume scraping")
else:
    print("  N/A (LLM extraction not tested)")

print()

print("Recommendation:")
print("-" * 80)

if llm_result and 'data' in llm_result and cost_per_article < 0.01:
    llm_content_len = len(llm_result['data'].get('content', ''))

    if abs(llm_content_len - len(n4k_text)) < len(n4k_text) * 0.2:
        print("  ✅ Hybrid LLM approach is viable!")
        print(f"     - Similar quality to Newspaper4k")
        print(f"     - Cost: ${cost_per_article:.6f} per article")
        print(f"     - May handle edge cases better")
    else:
        print("  ⚠️  Quality differs significantly from Newspaper4k")
        print(f"     - Newspaper4k: {len(n4k_text)} chars")
        print(f"     - LLM: {llm_content_len} chars")
        print("     - Need manual review to determine which is better")
elif not llm_result:
    print("  ℹ️  Set ANTHROPIC_API_KEY to test LLM extraction")
else:
    print("  ✅ Stick with Newspaper4k (free, proven)")

print("=" * 80)

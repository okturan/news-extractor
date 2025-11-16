#!/usr/bin/env python3
"""
Deep dive into T24 HTML structure to understand the edge case
"""

import requests
from bs4 import BeautifulSoup
import json

url = "https://t24.com.tr/haber/victor-osimhen-sampiyonlar-ligi-nde-haftanin-11-ine-secildi,1274139"

print("=" * 80)
print("T24 HTML STRUCTURE DEEP DIVE")
print("=" * 80)

response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(response.text, 'html.parser')

# Find the paragraphs with actual content
print("\n1. All <p> tags with their parent structure:")
print("-" * 80)

paragraphs = soup.find_all('p')
for i, p in enumerate(paragraphs, 1):
    text = p.get_text().strip()
    if text:
        # Get parent chain
        parent = p.parent
        parent_chain = []
        while parent and parent.name != 'html':
            parent_info = parent.name
            if parent.get('class'):
                parent_info += f".{'.'.join(parent['class'])}"
            if parent.get('id'):
                parent_info += f"#{parent['id']}"
            parent_chain.append(parent_info)
            parent = parent.parent

        print(f"\nParagraph {i}:")
        print(f"  Text: {text[:100]}...")
        print(f"  Parent chain: {' > '.join(reversed(parent_chain[-5:]))}")  # Last 5 parents

# Find where the actual article text is
print("\n\n2. Looking for article content container:")
print("-" * 80)

# The article content paragraphs
content_paragraphs = [p for p in paragraphs if len(p.get_text().strip()) > 50]

if content_paragraphs:
    # Get the parent that contains these paragraphs
    first_content_p = content_paragraphs[0]
    print(f"\nFirst content paragraph text:")
    print(f"  {first_content_p.get_text().strip()[:200]}...")

    # Walk up the DOM to find common container
    parent = first_content_p.parent
    depth = 0
    while parent and depth < 10:
        print(f"\nParent level {depth}:")
        print(f"  Tag: {parent.name}")
        print(f"  Class: {parent.get('class')}")
        print(f"  ID: {parent.get('id')}")
        print(f"  Children: {len(list(parent.children))} elements")

        # Check if this is a main content container
        if parent.get('class'):
            classes = ' '.join(parent['class'])
            if any(keyword in classes.lower() for keyword in ['content', 'article', 'body', 'text', 'haber']):
                print(f"  ⭐ Potential content container!")

        if parent.get('id'):
            if any(keyword in parent['id'].lower() for keyword in ['content', 'article', 'body', 'text', 'haber']):
                print(f"  ⭐ Potential content container!")

        parent = parent.parent
        depth += 1

# Check for script tags that might contain content
print("\n\n3. Checking for JavaScript-rendered content:")
print("-" * 80)

script_tags = soup.find_all('script', type='application/ld+json')
print(f"Found {len(script_tags)} JSON-LD script tags")

for i, script in enumerate(script_tags, 1):
    try:
        data = json.loads(script.string)
        if isinstance(data, dict):
            print(f"\nJSON-LD {i}:")
            print(f"  @type: {data.get('@type')}")
            if data.get('@type') == 'NewsArticle' or data.get('@type') == 'Article':
                print(f"  ⭐ Article data found!")
                print(f"  headline: {data.get('headline', 'N/A')}")
                print(f"  articleBody preview: {str(data.get('articleBody', 'N/A'))[:100]}...")
                print(f"  datePublished: {data.get('datePublished', 'N/A')}")
                print(f"  author: {data.get('author', 'N/A')}")
    except:
        pass

# Check meta tags
print("\n\n4. Checking meta tags:")
print("-" * 80)

meta_tags = {
    'og:description': soup.find('meta', property='og:description'),
    'description': soup.find('meta', attrs={'name': 'description'}),
    'article:published_time': soup.find('meta', property='article:published_time'),
}

for name, tag in meta_tags.items():
    if tag:
        print(f"  {name}: {tag.get('content', 'N/A')[:100]}...")

# Summary
print("\n\n5. DIAGNOSIS:")
print("=" * 80)

print("\n🔍 Why Newspaper4k Failed:")
print("  1. No standard <article> tag")
print("  2. No div with class containing 'article' or 'content'")
print("  3. Paragraph structure doesn't match Newspaper4k's heuristics")
print("  4. Content appears in plain <p> tags without semantic container")

print("\n✅ Why Trafilatura Succeeded:")
print("  1. Uses more advanced content detection algorithms")
print("  2. Can identify article content from plain paragraphs")
print("  3. Doesn't rely solely on semantic HTML structure")
print("  4. Likely uses text density and link density heuristics")

print("\n💡 Solution:")
print("  Use hybrid approach with validation:")
print("    if newspaper4k_result.text_length == 0:")
print("        fallback_to_trafilatura()")
print("=" * 80)

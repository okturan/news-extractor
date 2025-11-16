#!/usr/bin/env python3
"""Debug script to check what's actually at the OdaTV URL"""

import requests
from bs4 import BeautifulSoup

url = "https://www.odatv.com/guncel/sucuk-ekmek-kabusa-dondu-80-kisi-hastanelik-120122349"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.content, 'lxml')

# Check title
title = soup.find('title')
print(f"Title tag: {title.get_text() if title else 'Not found'}")

# Check og:title
og_title = soup.find('meta', property='og:title')
print(f"OG Title: {og_title['content'] if og_title else 'Not found'}")

# Check h1
h1 = soup.find('h1')
print(f"H1: {h1.get_text(strip=True) if h1 else 'Not found'}")

# Check for article content
articles = soup.find_all('article')
print(f"\nFound {len(articles)} article tags")

# Look for content divs
content_divs = soup.find_all('div', class_=lambda x: x and ('content' in str(x).lower() or 'article' in str(x).lower()))
print(f"Found {len(content_divs)} content-related divs")

# Check for food poisoning related keywords
text = soup.get_text()
keywords = ['sucuk', 'ekmek', 'zehirlen', 'hastane', '80 kisi']
print(f"\nKeyword search:")
for keyword in keywords:
    count = text.lower().count(keyword.lower())
    print(f"  '{keyword}': {count} occurrences")

# Check final URL after redirects
print(f"\nFinal URL: {response.url}")
print(f"Status Code: {response.status_code}")

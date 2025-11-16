#!/usr/bin/env python3
"""
BeautifulSoup Article Extractor with Custom Heuristics
Designed for Turkish news sites with focus on content density and text blocks
"""

import requests
import json
from bs4 import BeautifulSoup
from collections import defaultdict
import re


class ArticleExtractor:
    """Extract article content using custom heuristics"""

    def __init__(self, url):
        self.url = url
        self.soup = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_page(self):
        """Fetch HTML content from URL"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'lxml')
            return True
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            return False

    def remove_unwanted_elements(self):
        """Remove navigation, ads, scripts, styles, comments, etc."""
        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer', 'aside',
                        'iframe', 'noscript', 'form', 'button']
        unwanted_classes = ['nav', 'menu', 'sidebar', 'footer', 'header', 'ad',
                           'advertisement', 'comment', 'social', 'share', 'related',
                           'widget', 'banner', 'promo', 'subscription', 'newsletter',
                           'reklam', 'haber-listesi', 'galeri', 'video-container']
        unwanted_ids = ['nav', 'menu', 'sidebar', 'footer', 'header', 'comments',
                       'related-articles', 'advertisement']

        # Remove by tag name
        for tag in unwanted_tags:
            for element in self.soup.find_all(tag):
                element.decompose()

        # Remove by class name (partial match)
        for element in self.soup.find_all(class_=True):
            try:
                classes = ' '.join(element.get('class', [])).lower()
                if any(unwanted in classes for unwanted in unwanted_classes):
                    element.decompose()
            except (AttributeError, TypeError):
                continue

        # Remove by id (partial match)
        for element in self.soup.find_all(id=True):
            try:
                element_id = element.get('id', '').lower()
                if any(unwanted in element_id for unwanted in unwanted_ids):
                    element.decompose()
            except (AttributeError, TypeError):
                continue

    def extract_title(self):
        """Extract article title using multiple strategies"""
        # Strategy 1: Look for h1 tag
        h1 = self.soup.find('h1')
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)

        # Strategy 2: Look for article title in meta tags
        meta_tags = [
            ('property', 'og:title'),
            ('name', 'twitter:title'),
            ('property', 'twitter:title'),
        ]
        for attr, value in meta_tags:
            meta = self.soup.find('meta', attrs={attr: value})
            if meta and meta.get('content'):
                return meta['content'].strip()

        # Strategy 3: Look for title tag
        title_tag = self.soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Clean common suffixes
            title = re.split(r'\s*[-|]\s*', title)[0]
            return title

        return "Title not found"

    def calculate_text_density(self, element):
        """Calculate text density: ratio of text to tag count"""
        text = element.get_text(strip=True)
        text_length = len(text)

        # Count meaningful tags
        tags = element.find_all(['p', 'div', 'span', 'a', 'strong', 'em', 'b', 'i'])
        tag_count = len(tags) if tags else 1

        # Count paragraphs (higher weight)
        paragraph_count = len(element.find_all('p'))

        # Calculate density score
        density = text_length / tag_count
        paragraph_bonus = paragraph_count * 100

        return density + paragraph_bonus

    def get_text_block_score(self, element):
        """Score an element based on multiple heuristics"""
        score = 0

        # Count paragraphs (strong signal)
        paragraphs = element.find_all('p')
        score += len(paragraphs) * 50

        # Text length (normalized)
        text = element.get_text(strip=True)
        score += len(text) / 10

        # Average paragraph length (prefer longer paragraphs)
        if paragraphs:
            avg_p_length = sum(len(p.get_text(strip=True)) for p in paragraphs) / len(paragraphs)
            if avg_p_length > 50:  # Meaningful paragraphs
                score += avg_p_length / 2

        # Penalize if too many links (likely navigation)
        links = element.find_all('a')
        link_ratio = len(links) / (len(paragraphs) + 1)
        if link_ratio > 0.5:
            score -= 200

        # Bonus for article-related classes/ids
        article_indicators = ['article', 'content', 'main', 'body', 'text', 'entry',
                             'post', 'story', 'haber', 'icerik', 'detay']
        element_class = ' '.join(element.get('class', [])).lower()
        element_id = element.get('id', '').lower()
        if any(indicator in element_class or indicator in element_id for indicator in article_indicators):
            score += 100

        return score

    def extract_content(self):
        """Extract main article content using heuristics"""
        # Remove unwanted elements first
        self.remove_unwanted_elements()

        # Find all potential content containers
        candidates = []

        # Look for article tags first (semantic HTML5)
        for article in self.soup.find_all('article'):
            score = self.get_text_block_score(article)
            candidates.append((score, article))

        # Look for divs with high content density
        for div in self.soup.find_all('div'):
            paragraphs = div.find_all('p', recursive=False)
            # Only consider divs with direct paragraph children
            if len(paragraphs) >= 2:
                score = self.get_text_block_score(div)
                candidates.append((score, div))

        # Look for sections
        for section in self.soup.find_all('section'):
            score = self.get_text_block_score(section)
            candidates.append((score, section))

        if not candidates:
            return "Content not found"

        # Sort by score and get the best candidate
        candidates.sort(reverse=True, key=lambda x: x[0])
        best_element = candidates[0][1]

        # Extract text from paragraphs
        paragraphs = best_element.find_all('p')
        content_parts = []

        for p in paragraphs:
            text = p.get_text(strip=True)
            # Filter out very short paragraphs (likely noise)
            if len(text) > 30:
                content_parts.append(text)

        # If no good paragraphs found, try to get all text
        if not content_parts:
            content = best_element.get_text(separator='\n', strip=True)
            # Clean up multiple newlines
            content = re.sub(r'\n\s*\n', '\n\n', content)
            return content

        return '\n\n'.join(content_parts)

    def assess_quality(self, title, content):
        """Assess extraction quality based on heuristics"""
        if content == "Content not found" or title == "Title not found":
            return "failed"

        if len(content) < 200:
            return "failed"

        if len(content) < 500:
            return "partial"

        # Check if content has good structure
        paragraph_count = content.count('\n\n')
        if paragraph_count < 2:
            return "partial"

        # Check title quality
        if len(title) < 10 or title.startswith("http"):
            return "partial"

        return "good"

    def extract(self):
        """Main extraction method"""
        if not self.fetch_page():
            return {
                "url": self.url,
                "title": "Error fetching page",
                "content": "Failed to fetch page",
                "method": "beautifulsoup-heuristics",
                "extraction_quality": "failed",
                "char_count": 0
            }

        title = self.extract_title()
        content = self.extract_content()
        quality = self.assess_quality(title, content)

        return {
            "url": self.url,
            "title": title,
            "content": content,
            "method": "beautifulsoup-heuristics",
            "extraction_quality": quality,
            "char_count": len(content)
        }


def main():
    """Test on three Turkish news sites"""
    test_urls = [
        ("https://www.hurriyet.com.tr/gundem/arnavutkoyde-feci-kaza-tir-devrildi-surucu-agir-yarali-43010201",
         "hurriyet_result.json"),
        ("https://www.odatv.com/guncel/sucuk-ekmek-kabusa-dondu-80-kisi-hastanelik-120122349",
         "odatv_result.json"),
        ("https://www.milliyet.com.tr/",
         "milliyet_result.json"),
    ]

    results_summary = []

    for url, output_file in test_urls:
        print(f"\n{'='*80}")
        print(f"Processing: {url}")
        print(f"{'='*80}")

        extractor = ArticleExtractor(url)
        result = extractor.extract()

        # Save to JSON file
        output_path = f"/Users/okan/code/news-extractor/beautifulsoup-heuristics/{output_file}"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Print summary
        print(f"Title: {result['title'][:100]}...")
        print(f"Quality: {result['extraction_quality']}")
        print(f"Character count: {result['char_count']}")
        print(f"Content preview: {result['content'][:200]}...")
        print(f"Saved to: {output_path}")

        results_summary.append({
            "url": url,
            "file": output_file,
            "quality": result['extraction_quality'],
            "char_count": result['char_count'],
            "title": result['title']
        })

    # Print overall summary
    print(f"\n\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")
    for item in results_summary:
        print(f"\nSite: {item['url']}")
        print(f"  Quality: {item['quality']}")
        print(f"  Chars: {item['char_count']}")
        print(f"  Saved: {item['file']}")


if __name__ == "__main__":
    main()

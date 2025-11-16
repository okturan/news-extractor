#!/usr/bin/env python3
"""
BeautifulSoup Article Extractor with Enhanced Heuristics
Improved version with better content detection for Turkish news sites
"""

import requests
import json
from bs4 import BeautifulSoup, Comment
import re


class ArticleExtractor:
    """Extract article content using custom heuristics"""

    def __init__(self, url):
        self.url = url
        self.soup = None
        self.original_soup = None  # Keep original for debugging
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_page(self):
        """Fetch HTML content from URL"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'lxml')
            self.original_soup = BeautifulSoup(response.content, 'lxml')
            return True
        except Exception as e:
            print(f"Error fetching {self.url}: {e}")
            return False

    def remove_unwanted_elements(self, soup=None):
        """Remove navigation, ads, scripts, styles, comments, etc."""
        if soup is None:
            soup = self.soup

        # Remove HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        unwanted_tags = ['script', 'style', 'nav', 'header', 'footer',
                        'iframe', 'noscript', 'form', 'button', 'svg', 'path']

        # Remove by tag name
        for tag in unwanted_tags:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove specific unwanted patterns
        unwanted_patterns = [
            'nav', 'menu', 'sidebar', 'footer', 'header', 'advertisement',
            'comment', 'social', 'share', 'related', 'widget', 'banner',
            'reklam', 'yorum', 'paylas', 'diger-haber', 'manset', 'galeri',
            'video-list', 'haberleri', 'listesi'
        ]

        for element in soup.find_all(True):
            try:
                # Check class
                element_classes = ' '.join(element.get('class', [])).lower()
                # Check id
                element_id = str(element.get('id', '')).lower()

                # Remove if matches unwanted pattern
                if any(pattern in element_classes or pattern in element_id
                       for pattern in unwanted_patterns):
                    element.decompose()
            except (AttributeError, TypeError):
                continue

    def extract_title(self):
        """Extract article title using multiple strategies"""
        # Strategy 1: Look for og:title meta tag
        meta_og = self.original_soup.find('meta', property='og:title')
        if meta_og and meta_og.get('content'):
            return meta_og['content'].strip()

        # Strategy 2: Look for h1 tag
        h1 = self.original_soup.find('h1')
        if h1 and h1.get_text(strip=True):
            return h1.get_text(strip=True)

        # Strategy 3: Twitter title
        meta_twitter = self.original_soup.find('meta', attrs={'name': 'twitter:title'})
        if meta_twitter and meta_twitter.get('content'):
            return meta_twitter['content'].strip()

        # Strategy 4: Title tag
        title_tag = self.original_soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            # Clean common suffixes
            title = re.split(r'\s*[-|]\s*', title)[0]
            return title

        return "Title not found"

    def get_text_block_score(self, element):
        """Score an element based on multiple heuristics"""
        score = 0

        # Get all text
        text = element.get_text(strip=True)
        text_length = len(text)

        # Must have meaningful text
        if text_length < 100:
            return 0

        # Count paragraphs (very strong signal)
        paragraphs = element.find_all('p')
        paragraph_count = len(paragraphs)
        score += paragraph_count * 100

        # Average paragraph length
        if paragraphs:
            valid_paragraphs = [p for p in paragraphs if len(p.get_text(strip=True)) > 40]
            if valid_paragraphs:
                avg_length = sum(len(p.get_text(strip=True)) for p in valid_paragraphs) / len(valid_paragraphs)
                score += avg_length
            else:
                score -= 500  # Penalty for short paragraphs

        # Text density: favor high text/tag ratio
        all_tags = element.find_all(True)
        if all_tags:
            density = text_length / len(all_tags)
            score += density * 2

        # Penalty for too many links
        links = element.find_all('a')
        if paragraph_count > 0:
            link_density = len(links) / paragraph_count
            if link_density > 1:
                score -= 300

        # Bonus for article-related attributes
        article_indicators = ['article', 'content', 'main', 'body', 'text', 'entry',
                             'post', 'story', 'haber', 'icerik', 'detay', 'news', 'spot']

        try:
            element_class = ' '.join(element.get('class', [])).lower()
            element_id = str(element.get('id', '')).lower()
            element_name = element.name.lower()

            for indicator in article_indicators:
                if indicator in element_class:
                    score += 200
                if indicator in element_id:
                    score += 200
                if indicator == element_name:
                    score += 150
        except (AttributeError, TypeError):
            pass

        return score

    def extract_paragraphs_from_element(self, element):
        """Extract meaningful paragraphs from an element"""
        paragraphs = element.find_all('p')
        content_parts = []

        for p in paragraphs:
            text = p.get_text(strip=True)
            # Filter out very short paragraphs
            if len(text) > 40:
                content_parts.append(text)

        return content_parts

    def extract_content(self):
        """Extract main article content using heuristics"""
        # Work with a copy
        soup_copy = BeautifulSoup(str(self.original_soup), 'lxml')
        self.remove_unwanted_elements(soup_copy)

        candidates = []

        # Strategy 1: Look for article tags (semantic HTML5)
        for article in soup_copy.find_all('article'):
            score = self.get_text_block_score(article)
            if score > 0:
                candidates.append((score, article, 'article'))

        # Strategy 2: Look for divs with article-like class/id
        article_keywords = ['article', 'content', 'main', 'body', 'haber', 'detay', 'icerik', 'news', 'story', 'post']
        for div in soup_copy.find_all('div'):
            try:
                div_class = ' '.join(div.get('class', [])).lower()
                div_id = str(div.get('id', '')).lower()

                # Check if div looks like article container
                if any(keyword in div_class or keyword in div_id for keyword in article_keywords):
                    score = self.get_text_block_score(div)
                    if score > 0:
                        candidates.append((score, div, 'div'))
            except (AttributeError, TypeError):
                continue

        # Strategy 3: Look for sections
        for section in soup_copy.find_all('section'):
            score = self.get_text_block_score(section)
            if score > 0:
                candidates.append((score, section, 'section'))

        # Strategy 4: Generic search for high-density containers
        for container in soup_copy.find_all(['div', 'main']):
            # Check if has multiple paragraphs
            direct_paragraphs = container.find_all('p', recursive=False)
            all_paragraphs = container.find_all('p')

            if len(all_paragraphs) >= 3:
                score = self.get_text_block_score(container)
                if score > 0:
                    candidates.append((score, container, 'container'))

        if not candidates:
            # Last resort: find element with most paragraphs
            all_elements = soup_copy.find_all(['div', 'article', 'section', 'main'])
            for elem in all_elements:
                paragraphs = elem.find_all('p')
                if len(paragraphs) >= 2:
                    score = len(paragraphs) * 50 + len(elem.get_text(strip=True))
                    candidates.append((score, elem, 'fallback'))

        if not candidates:
            return "Content not found"

        # Sort by score and get top candidates
        candidates.sort(reverse=True, key=lambda x: x[0])

        # Try top 3 candidates
        for score, element, method in candidates[:3]:
            content_parts = self.extract_paragraphs_from_element(element)

            if content_parts and len('\n\n'.join(content_parts)) > 200:
                print(f"  > Found content using: {method} (score: {score:.0f})")
                return '\n\n'.join(content_parts)

        # If still nothing, try getting all text from best candidate
        if candidates:
            best_element = candidates[0][1]
            text = best_element.get_text(separator='\n', strip=True)
            # Clean up multiple newlines
            text = re.sub(r'\n\s*\n+', '\n\n', text)
            # Remove lines that are too short (likely navigation)
            lines = [line for line in text.split('\n') if len(line.strip()) > 30]
            if lines:
                return '\n\n'.join(lines)

        return "Content not found"

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
        if len(title) < 10:
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
            "char_count": len(content) if content != "Content not found" else 0
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

    print("\nBeautifulSoup Article Extractor - Enhanced Version")
    print("="*80)

    for url, output_file in test_urls:
        print(f"\nProcessing: {url}")
        print("-"*80)

        extractor = ArticleExtractor(url)
        result = extractor.extract()

        # Save to JSON file
        output_path = f"/Users/okan/code/news-extractor/beautifulsoup-heuristics/{output_file}"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Print summary
        print(f"  Title: {result['title'][:80]}{'...' if len(result['title']) > 80 else ''}")
        print(f"  Quality: {result['extraction_quality']}")
        print(f"  Character count: {result['char_count']}")
        if result['char_count'] > 0:
            preview = result['content'][:150].replace('\n', ' ')
            print(f"  Content preview: {preview}...")
        print(f"  Saved to: {output_file}")

        results_summary.append({
            "url": url,
            "file": output_file,
            "quality": result['extraction_quality'],
            "char_count": result['char_count'],
            "title": result['title'][:80]
        })

    # Print overall summary
    print(f"\n{'='*80}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*80}")

    for item in results_summary:
        site_name = item['url'].split('/')[2].replace('www.', '')
        print(f"\n{site_name}:")
        print(f"  Quality: {item['quality']}")
        print(f"  Characters: {item['char_count']}")
        print(f"  File: {item['file']}")

    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()

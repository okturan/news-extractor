#!/usr/bin/env python3
"""
Hurriyet Article Content Scraper
Fetches full article content from individual Hurriyet news URLs
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import sys


async def scrape_article(url: str):
    """Scrape full content from a single Hurriyet article URL"""

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set timeout
        page.set_default_timeout(60000)

        print(f"Fetching article from: {url}")

        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        except Exception as e:
            print(f"Navigation error: {e}")
            await browser.close()
            return None

        # Wait for content to load
        await asyncio.sleep(2)

        article_data = {
            'url': url,
            'title': None,
            'subtitle': None,
            'author': None,
            'publish_date': None,
            'content': None,
            'images': [],
            'tags': [],
            'scraped_at': datetime.now().isoformat()
        }

        try:
            # Extract title
            title_selectors = [
                'h1.title',
                'h1[class*="title"]',
                'h1',
                '.article-title',
                '[class*="article"] h1'
            ]
            for selector in title_selectors:
                title_elem = await page.query_selector(selector)
                if title_elem:
                    article_data['title'] = (await title_elem.inner_text()).strip()
                    break

            # Extract subtitle/summary
            subtitle_selectors = [
                '.subtitle',
                '.summary',
                '.lead',
                '[class*="subtitle"]',
                '[class*="summary"]'
            ]
            for selector in subtitle_selectors:
                subtitle_elem = await page.query_selector(selector)
                if subtitle_elem:
                    article_data['subtitle'] = (await subtitle_elem.inner_text()).strip()
                    break

            # Extract author
            author_selectors = [
                '.author',
                '[class*="author"]',
                '.writer',
                '[itemprop="author"]'
            ]
            for selector in author_selectors:
                author_elem = await page.query_selector(selector)
                if author_elem:
                    article_data['author'] = (await author_elem.inner_text()).strip()
                    break

            # Extract publish date
            date_selectors = [
                'time',
                '[class*="date"]',
                '[class*="time"]',
                '[itemprop="datePublished"]'
            ]
            for selector in date_selectors:
                date_elem = await page.query_selector(selector)
                if date_elem:
                    date_text = await date_elem.inner_text()
                    article_data['publish_date'] = date_text.strip()
                    break

            # Extract main article content
            content_selectors = [
                '.article-content',
                '.content',
                '[class*="article-content"]',
                '[class*="article-body"]',
                '[itemprop="articleBody"]',
                '.news-content'
            ]

            content_paragraphs = []

            # Filter out modal/popup text
            modal_keywords = ['modal window', 'dialog window', 'escape will cancel']

            for selector in content_selectors:
                content_elem = await page.query_selector(selector)
                if content_elem:
                    # Get all paragraphs within the content
                    paragraphs = await content_elem.query_selector_all('p')
                    for p in paragraphs:
                        text = await p.inner_text()
                        # Filter out short paragraphs and modal/popup text
                        if text and len(text.strip()) > 20:
                            # Skip if contains modal keywords
                            text_lower = text.lower()
                            if not any(keyword in text_lower for keyword in modal_keywords):
                                content_paragraphs.append(text.strip())
                    if content_paragraphs:
                        break

            # If no paragraphs found in content divs, try getting all article paragraphs
            if not content_paragraphs:
                all_paragraphs = await page.query_selector_all('article p, .news p, [class*="article"] p')
                for p in all_paragraphs:
                    text = await p.inner_text()
                    if text and len(text.strip()) > 20:
                        content_paragraphs.append(text.strip())

            article_data['content'] = '\n\n'.join(content_paragraphs) if content_paragraphs else None

            # Extract images
            img_selectors = [
                'article img',
                '.article-content img',
                '.content img',
                '[class*="article"] img'
            ]
            for selector in img_selectors:
                images = await page.query_selector_all(selector)
                for img in images[:5]:  # Limit to first 5 images
                    src = await img.get_attribute('src')
                    alt = await img.get_attribute('alt')
                    if src:
                        article_data['images'].append({
                            'src': src,
                            'alt': alt or ''
                        })
                if article_data['images']:
                    break

            # Extract tags/keywords
            tag_selectors = [
                '.tags a',
                '.keywords a',
                '[class*="tag"] a',
                '[rel="tag"]'
            ]
            for selector in tag_selectors:
                tags = await page.query_selector_all(selector)
                for tag in tags:
                    tag_text = await tag.inner_text()
                    if tag_text:
                        article_data['tags'].append(tag_text.strip())
                if article_data['tags']:
                    break

        except Exception as e:
            print(f"Error extracting article data: {e}")

        await browser.close()
        return article_data


async def main():
    """Main execution function"""

    # Get URL from command line or use default
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Default test URL
        url = "https://www.hurriyet.com.tr/gundem/arnavutkoyde-feci-kaza-tir-devrildi-surucu-agir-yarali-43010201"

    print("=" * 80)
    print("Hurriyet Article Scraper")
    print("=" * 80)

    article_data = await scrape_article(url)

    if article_data:
        print("\n" + "=" * 80)
        print("ARTICLE DATA")
        print("=" * 80)

        print(f"\nTitle: {article_data['title']}")

        if article_data['subtitle']:
            print(f"Subtitle: {article_data['subtitle']}")

        if article_data['author']:
            print(f"Author: {article_data['author']}")

        if article_data['publish_date']:
            print(f"Published: {article_data['publish_date']}")

        if article_data['tags']:
            print(f"Tags: {', '.join(article_data['tags'])}")

        if article_data['images']:
            print(f"\nImages found: {len(article_data['images'])}")
            for i, img in enumerate(article_data['images'], 1):
                print(f"  {i}. {img['src']}")

        if article_data['content']:
            print(f"\nContent ({len(article_data['content'])} characters):")
            print("-" * 80)
            # Print first 500 characters
            preview = article_data['content'][:500] + "..." if len(article_data['content']) > 500 else article_data['content']
            print(preview)
            print("-" * 80)

        # Save to JSON
        output_file = f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)

        print(f"\nFull article saved to: {output_file}")

        return article_data
    else:
        print("Failed to scrape article")
        return None


if __name__ == '__main__':
    asyncio.run(main())

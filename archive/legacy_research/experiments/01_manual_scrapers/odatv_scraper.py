#!/usr/bin/env python3
"""
OdaTV News Scraper
Scrapes headlines and full article content from odatv.com
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def scrape_odatv_homepage(browser):
    """Scrape headlines from OdaTV homepage"""

    page = await browser.new_page()
    page.set_default_timeout(60000)

    print("=" * 80)
    print("STEP 1: Scraping odatv.com for headlines...")
    print("=" * 80)

    try:
        await page.goto('https://www.odatv.com/', wait_until='domcontentloaded', timeout=60000)
    except Exception as e:
        print(f"Navigation error: {e}")
        await page.close()
        return []

    await asyncio.sleep(3)

    headlines = []

    print("Searching for article links...")

    # Find all links that look like articles
    all_links = await page.query_selector_all('a[href]')

    print(f"Total links found: {len(all_links)}")

    for link_elem in all_links:
        try:
            href = await link_elem.get_attribute('href')

            # Filter for article URLs (skip navigation, external, etc.)
            if not href or href == '/' or href == '#':
                continue

            # Make link absolute
            if href.startswith('/'):
                href = f'https://www.odatv.com{href}'
            elif not href.startswith('http'):
                continue

            # Skip non-article links
            skip_patterns = [
                'foto-galeri', 'video-galeri', 'gastroda', 'javascript:',
                'facebook.com', 'twitter.com', 'instagram.com',
                '/kategori/', '/etiket/', '/yazar/'
            ]

            if any(pattern in href for pattern in skip_patterns):
                continue

            # Check if link has meaningful text
            text = await link_elem.inner_text()
            if not text or len(text.strip()) < 15:
                continue

            # Check if it looks like an article URL
            article_patterns = ['/gundem/', '/politika/', '/ekonomi/', '/dunya/', '/spor/', '/kultur-sanat/']
            is_article = any(pattern in href for pattern in article_patterns)

            # Or if it has a date-like pattern in URL
            import re
            has_date = bool(re.search(r'/\d{4}/', href) or re.search(r'-\d{6,}', href))

            if is_article or has_date:
                headlines.append({
                    'title': text.strip(),
                    'link': href,
                    'scraped_at': datetime.now().isoformat()
                })

        except Exception as e:
            continue

    await page.close()

    # Remove duplicates based on link
    unique_headlines = []
    seen_links = set()
    for item in headlines:
        if item['link'] not in seen_links:
            unique_headlines.append(item)
            seen_links.add(item['link'])
            print(f"  {len(unique_headlines)}. {item['title'][:70]}...")

    print(f"\nFound {len(unique_headlines)} unique articles")
    return unique_headlines


async def scrape_odatv_article(browser, url, index, total):
    """Scrape full content from a single OdaTV article URL"""

    page = await browser.new_page()
    page.set_default_timeout(60000)

    print(f"  [{index}/{total}] Fetching: {url[:70]}...")

    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
    except Exception as e:
        print(f"    Error navigating: {e}")
        await page.close()
        return None

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
        'category': None,
        'scraped_at': datetime.now().isoformat()
    }

    try:
        # Extract title
        title_selectors = [
            'h1.title',
            'h1[class*="title"]',
            'h1[class*="baslik"]',
            'h1',
            '.article-title',
            '[class*="article"] h1',
            '.haber-baslik'
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
            '.spot',
            '[class*="subtitle"]',
            '[class*="summary"]',
            '[class*="spot"]'
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
            '.yazar',
            '[class*="yazar"]',
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
            '.date',
            '.time',
            '.tarih',
            '[class*="date"]',
            '[class*="time"]',
            '[class*="tarih"]',
            '[itemprop="datePublished"]'
        ]
        for selector in date_selectors:
            date_elem = await page.query_selector(selector)
            if date_elem:
                article_data['publish_date'] = (await date_elem.inner_text()).strip()
                break

        # Extract category
        category_selectors = [
            '.category',
            '.kategori',
            '[class*="category"]',
            '[class*="kategori"]',
            'nav a',
            '.breadcrumb a'
        ]
        for selector in category_selectors:
            category_elem = await page.query_selector(selector)
            if category_elem:
                article_data['category'] = (await category_elem.inner_text()).strip()
                break

        # Extract main article content
        content_selectors = [
            '.article-content',
            '.content',
            '.haber-icerik',
            '.news-content',
            '[class*="article-content"]',
            '[class*="article-body"]',
            '[class*="haber-icerik"]',
            '[itemprop="articleBody"]'
        ]

        content_paragraphs = []
        modal_keywords = ['modal window', 'dialog window', 'escape will cancel', 'cookie', 'çerez']

        for selector in content_selectors:
            content_elem = await page.query_selector(selector)
            if content_elem:
                paragraphs = await content_elem.query_selector_all('p')
                for p in paragraphs:
                    text = await p.inner_text()
                    if text and len(text.strip()) > 20:
                        text_lower = text.lower()
                        if not any(keyword in text_lower for keyword in modal_keywords):
                            content_paragraphs.append(text.strip())
                if content_paragraphs:
                    break

        # If no paragraphs found, try broader search
        if not content_paragraphs:
            all_paragraphs = await page.query_selector_all('article p, .news p, [class*="article"] p, [class*="haber"] p')
            for p in all_paragraphs:
                text = await p.inner_text()
                if text and len(text.strip()) > 20:
                    text_lower = text.lower()
                    if not any(keyword in text_lower for keyword in modal_keywords):
                        content_paragraphs.append(text.strip())

        article_data['content'] = '\n\n'.join(content_paragraphs) if content_paragraphs else None

        # Extract images
        img_selectors = [
            'article img',
            '.article-content img',
            '.content img',
            '.haber-icerik img',
            '[class*="article"] img'
        ]
        for selector in img_selectors:
            images = await page.query_selector_all(selector)
            for img in images[:5]:
                src = await img.get_attribute('src')
                alt = await img.get_attribute('alt')
                if src and src.startswith('http'):
                    article_data['images'].append({'src': src, 'alt': alt or ''})
            if article_data['images']:
                break

        # Extract tags
        tag_selectors = [
            '.tags a',
            '.keywords a',
            '.etiket a',
            '[class*="tag"] a',
            '[class*="etiket"] a',
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

        print(f"    ✓ Extracted {len(article_data['content']) if article_data['content'] else 0} chars")

    except Exception as e:
        print(f"    Error extracting: {e}")

    await page.close()
    return article_data


async def main():
    """Main execution function"""

    print("=" * 80)
    print("ODATV FULL SCRAPER")
    print("=" * 80)
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Step 1: Get all headlines from homepage
        headlines = await scrape_odatv_homepage(browser)

        if not headlines:
            print("No headlines found!")
            await browser.close()
            return

        # Step 2: Scrape each article
        print("\n" + "=" * 80)
        print(f"STEP 2: Scraping {len(headlines)} articles...")
        print("=" * 80)
        print()

        all_articles = []

        for idx, headline in enumerate(headlines, 1):
            article_data = await scrape_odatv_article(browser, headline['link'], idx, len(headlines))

            if article_data and article_data['content']:
                all_articles.append(article_data)

            # Small delay between requests
            await asyncio.sleep(1)

        await browser.close()

        # Save results
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        print(f"Successfully scraped {len(all_articles)} articles with content")

        output_file = f'odatv_full_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, ensure_ascii=False, indent=2)

        print(f"Saved to: {output_file}")

        # Show summary
        print("\nSample of scraped articles:")
        print("-" * 80)
        for i, article in enumerate(all_articles[:5], 1):
            content_preview = article['content'][:80] + "..." if article['content'] and len(article['content']) > 80 else article['content']
            print(f"{i}. {article['title']}")
            if article['publish_date']:
                print(f"   Published: {article['publish_date']}")
            if article['category']:
                print(f"   Category: {article['category']}")
            print(f"   Content: {content_preview}")
            print()

        return all_articles


if __name__ == '__main__':
    asyncio.run(main())

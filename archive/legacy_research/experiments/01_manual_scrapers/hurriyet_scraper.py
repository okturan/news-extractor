#!/usr/bin/env python3
"""
Hurriyet.com.tr News Scraper
Scrapes headlines and news content from Hurriyet newspaper website
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def scrape_hurriyet():
    """Main scraper function for hurriyet.com.tr"""

    async with async_playwright() as p:
        # Launch browser (headless=True means no visible browser window)
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set longer timeout for slow-loading pages
        page.set_default_timeout(60000)  # 60 seconds

        # Navigate to hurriyet.com.tr
        print("Navigating to hurriyet.com.tr...")
        try:
            await page.goto('https://www.hurriyet.com.tr/', wait_until='domcontentloaded', timeout=60000)
        except Exception as e:
            print(f"Navigation took longer than expected, continuing anyway: {e}")

        # Wait a bit for dynamic content to load
        await asyncio.sleep(3)

        # Extract news headlines and articles
        print("Extracting news content...")

        news_items = []

        # Scrape main headlines
        headlines = await page.query_selector_all('article, .news-item, .headline, [class*="news"], [class*="article"]')

        for idx, article in enumerate(headlines[:50]):  # Limit to first 50 items
            try:
                # Extract title
                title_elem = await article.query_selector('h1, h2, h3, h4, .title, [class*="title"]')
                title = await title_elem.inner_text() if title_elem else None

                # Extract link
                link_elem = await article.query_selector('a')
                link = await link_elem.get_attribute('href') if link_elem else None

                # Make link absolute if it's relative
                if link and link.startswith('/'):
                    link = f'https://www.hurriyet.com.tr{link}'

                # Extract description/summary if available
                desc_elem = await article.query_selector('p, .summary, .description, [class*="summary"]')
                description = await desc_elem.inner_text() if desc_elem else None

                # Extract image if available
                img_elem = await article.query_selector('img')
                image = await img_elem.get_attribute('src') if img_elem else None

                if title:  # Only add if we found a title
                    news_items.append({
                        'title': title.strip(),
                        'link': link,
                        'description': description.strip() if description else None,
                        'image': image,
                        'scraped_at': datetime.now().isoformat()
                    })

            except Exception as e:
                print(f"Error extracting article {idx}: {e}")
                continue

        await browser.close()

        return news_items


async def main():
    """Main execution function"""
    print("Starting Hurriyet scraper...")
    print("=" * 60)

    news_items = await scrape_hurriyet()

    print(f"\nScraped {len(news_items)} news items")
    print("=" * 60)

    # Save to JSON file
    output_file = f'hurriyet_news_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(news_items, f, ensure_ascii=False, indent=2)

    print(f"Saved to: {output_file}")

    # Print first 5 headlines as preview
    print("\nFirst 5 headlines:")
    print("-" * 60)
    for i, item in enumerate(news_items[:5], 1):
        print(f"{i}. {item['title']}")
        if item['link']:
            print(f"   URL: {item['link']}")
        print()

    return news_items


if __name__ == '__main__':
    asyncio.run(main())

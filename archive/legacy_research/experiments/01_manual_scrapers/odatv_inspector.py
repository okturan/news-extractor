#!/usr/bin/env python3
"""
OdaTV Page Inspector
Investigates the page structure to find the right selectors
"""

import asyncio
from playwright.async_api import async_playwright


async def inspect_odatv():
    """Inspect OdaTV homepage structure"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(60000)

        print("Loading odatv.com...")
        await page.goto('https://www.odatv.com/', wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)

        print("\n" + "=" * 80)
        print("INSPECTING PAGE STRUCTURE")
        print("=" * 80)

        # Check for links
        all_links = await page.query_selector_all('a')
        print(f"\nTotal links on page: {len(all_links)}")

        # Find links with text (likely article links)
        article_links = []
        for link in all_links[:100]:  # Check first 100 links
            href = await link.get_attribute('href')
            text = await link.inner_text()
            if text and len(text.strip()) > 10 and href:
                article_links.append({
                    'text': text.strip(),
                    'href': href
                })

        print(f"\nFound {len(article_links)} links with substantial text")
        print("\nFirst 10 article-like links:")
        print("-" * 80)
        for i, link in enumerate(article_links[:10], 1):
            print(f"{i}. {link['text'][:70]}...")
            print(f"   URL: {link['href'][:70]}...")
            print()

        # Check for common container elements
        print("\n" + "=" * 80)
        print("CHECKING COMMON SELECTORS")
        print("=" * 80)

        selectors_to_check = [
            ('div.card', 'Bootstrap cards'),
            ('div[class*="item"]', 'Elements with "item" in class'),
            ('div[class*="post"]', 'Elements with "post" in class'),
            ('div[class*="haber"]', 'Elements with "haber" in class'),
            ('div[class*="news"]', 'Elements with "news" in class'),
            ('article', 'Article elements'),
            ('a[href*="/gundem/"]', 'Links to gundem section'),
            ('a[href*="/politika/"]', 'Links to politika section'),
            ('a[href*="/ekonomi/"]', 'Links to ekonomi section'),
        ]

        for selector, description in selectors_to_check:
            elements = await page.query_selector_all(selector)
            print(f"{description:40} -> {len(elements)} found")

        # Get page HTML structure (first 5000 chars)
        html_content = await page.content()
        print("\n" + "=" * 80)
        print("PAGE HTML SNIPPET (first 5000 chars)")
        print("=" * 80)
        print(html_content[:5000])

        await browser.close()


if __name__ == '__main__':
    asyncio.run(inspect_odatv())

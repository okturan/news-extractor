#!/usr/bin/env python3
"""
Test Crawl4AI PROPERLY with extraction strategies
"""

import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy, CosineStrategy
import json
import os

url = "https://bianet.org/haber/erdogan-ozele-tazminat-davasi-acti-313281"

print("=" * 80)
print("CRAWL4AI PROPER USAGE TEST")
print("=" * 80)
print(f"Testing extraction strategies on: {url}")
print()


async def test_basic_markdown():
    """Test 1: Basic markdown (what I used before)"""
    print("1. BASIC MARKDOWN (what I used before)")
    print("-" * 80)

    browser_config = BrowserConfig(headless=True, verbose=False)
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until="networkidle"
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

        if result.success:
            print(f"✅ Success")
            print(f"   Markdown length: {len(result.markdown)} chars")
            print(f"   First 300 chars: {result.markdown[:300]}...")
        else:
            print(f"❌ Failed")

        return result.markdown if result.success else None


async def test_cosine_strategy():
    """Test 2: Cosine similarity strategy (semantic extraction)"""
    print("\n2. COSINE STRATEGY (semantic extraction)")
    print("-" * 80)

    browser_config = BrowserConfig(headless=True, verbose=False)

    # Use cosine similarity to extract semantically similar content
    strategy = CosineStrategy(
        semantic_filter="article news content main text",  # What to look for
        word_count_threshold=10,  # Minimum words per chunk
        sim_threshold=0.3  # Similarity threshold
    )

    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until="networkidle",
        extraction_strategy=strategy
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

        if result.success:
            extracted = result.extracted_content
            print(f"✅ Success")
            print(f"   Extracted content length: {len(extracted) if extracted else 0} chars")
            if extracted:
                print(f"   First 300 chars: {extracted[:300]}...")
        else:
            print(f"❌ Failed")

        return extracted if result.success else None


async def test_css_selector():
    """Test 3: CSS Selector strategy"""
    print("\n3. CSS SELECTOR STRATEGY")
    print("-" * 80)

    # First, let's try to use CSS selectors for article content
    # Common selectors for article content
    css_selectors = [
        "article",
        ".article-content",
        "[itemprop='articleBody']",
        ".haber-icerik",  # Turkish: news content
        "main"
    ]

    browser_config = BrowserConfig(headless=True, verbose=False)
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        wait_until="networkidle",
        css_selector=", ".join(css_selectors)  # Try multiple selectors
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)

        if result.success:
            print(f"✅ Success")
            print(f"   Markdown length: {len(result.markdown)} chars")
            print(f"   First 300 chars: {result.markdown[:300]}...")
        else:
            print(f"❌ Failed")

        return result.markdown if result.success else None


async def test_llm_extraction():
    """Test 4: LLM-based extraction (if API key available)"""
    print("\n4. LLM EXTRACTION STRATEGY")
    print("-" * 80)

    # Check if OpenAI/Anthropic API key exists
    has_openai = os.getenv('OPENAI_API_KEY') is not None
    has_anthropic = os.getenv('ANTHROPIC_API_KEY') is not None

    if not has_openai and not has_anthropic:
        print("⚠️  No API key found (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        print("   Skipping LLM extraction test")
        return None

    try:
        # Define schema for article extraction
        schema = {
            "name": "Article",
            "baseSelector": "body",
            "fields": [
                {
                    "name": "title",
                    "selector": "h1",
                    "type": "text"
                },
                {
                    "name": "author",
                    "selector": ".author, [itemprop='author']",
                    "type": "text"
                },
                {
                    "name": "content",
                    "selector": "article, .article-content, main",
                    "type": "text"
                },
                {
                    "name": "date",
                    "selector": "time, .date, [itemprop='datePublished']",
                    "type": "text"
                }
            ]
        }

        provider = "openai/gpt-4o-mini" if has_openai else "anthropic/claude-3-haiku"

        strategy = LLMExtractionStrategy(
            provider=provider,
            schema=schema,
            instruction="Extract the main article content, title, author, and date. Ignore navigation, ads, and sidebar content."
        )

        browser_config = BrowserConfig(headless=True, verbose=False)
        crawler_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            wait_until="networkidle",
            extraction_strategy=strategy
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=crawler_config)

            if result.success:
                extracted = result.extracted_content
                print(f"✅ Success with {provider}")
                print(f"   Extracted content: {extracted}")
            else:
                print(f"❌ Failed")

            return extracted if result.success else None

    except Exception as e:
        print(f"❌ Exception: {str(e)[:200]}")
        return None


async def main():
    results = {}

    # Test all strategies
    results['basic'] = await test_basic_markdown()
    results['cosine'] = await test_cosine_strategy()
    results['css'] = await test_css_selector()
    results['llm'] = await test_llm_extraction()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\nContent Lengths:")
    for strategy, content in results.items():
        length = len(content) if content else 0
        status = "✅" if length > 0 else "❌"
        print(f"  {strategy:10} {status} {length:6} chars")

    print("\nRecommendation:")
    if results['cosine'] and len(results['cosine']) < len(results['basic'] or '') / 10:
        print("  ✅ Cosine strategy produces cleaner output!")
    elif results['css'] and len(results['css']) < len(results['basic'] or '') / 10:
        print("  ✅ CSS selector strategy produces cleaner output!")
    elif results['llm']:
        print("  ✅ LLM extraction works and might be cleanest")
    else:
        print("  ⚠️  Basic markdown may be only option (includes full page)")

    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())

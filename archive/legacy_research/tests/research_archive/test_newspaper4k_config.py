#!/usr/bin/env python3
"""
Test Newspaper4k's configuration and tuning capabilities
"""

from newspaper import build, Config, Article
import inspect


def explore_newspaper4k_config():
    """Explore what configuration options Newspaper4k provides"""

    print("=" * 80)
    print("NEWSPAPER4K CONFIGURATION OPTIONS")
    print("=" * 80)

    # Get all Config attributes
    config = Config()

    print("\nAvailable Configuration Options:")
    print("-" * 80)

    config_attrs = [attr for attr in dir(config) if not attr.startswith('_')]

    for attr in sorted(config_attrs):
        value = getattr(config, attr)
        if not callable(value):
            print(f"  {attr:30} = {value}")

    print("\n" + "=" * 80)
    print("CAN WE CUSTOMIZE FOR TURKISH SITES?")
    print("=" * 80)

    # Test custom configuration
    custom_config = Config()

    # Language settings
    print("\n1️⃣ Language Customization:")
    print("-" * 80)
    custom_config.language = 'tr'  # Turkish
    custom_config.fetch_images = True
    custom_config.memoize_articles = False  # Don't cache
    print(f"  ✓ Language: {custom_config.language}")
    print(f"  ✓ Fetch images: {custom_config.fetch_images}")
    print(f"  ✓ Memoize: {custom_config.memoize_articles}")

    # Parser settings
    print("\n2️⃣ Parser Customization:")
    print("-" * 80)
    print(f"  Parser: {custom_config.parser}")
    print(f"  Available parsers: lxml, html.parser, html5lib")

    # HTTP settings
    print("\n3️⃣ HTTP/Network Settings:")
    print("-" * 80)
    print(f"  Request timeout: {custom_config.request_timeout}s")
    print(f"  Number of threads: {custom_config.number_threads}")
    print(f"  User agent: {custom_config.browser_user_agent[:50]}...")

    # Content extraction settings
    print("\n4️⃣ Content Extraction Settings:")
    print("-" * 80)
    print(f"  Keep article HTML: {custom_config.keep_article_html}")
    print(f"  Fetch images: {custom_config.fetch_images}")
    print(f"  Follow meta refresh: {custom_config.follow_meta_refresh}")

    # URL/Link discovery settings
    print("\n5️⃣ URL Discovery Settings:")
    print("-" * 80)
    print(f"  Max file memo: {custom_config.MAX_FILE_MEMO}")
    print(f"  Use meta language: {custom_config.use_meta_language}")

    # Check if we can customize article detection
    print("\n6️⃣ Article Detection Customization:")
    print("-" * 80)

    # Look at Source class methods
    from newspaper import Source
    source_methods = [m for m in dir(Source) if not m.startswith('_')]

    print("  Source class methods:")
    for method in source_methods[:10]:
        print(f"    • {method}")

    # Check Article class
    print("\n  Article class methods:")
    article_methods = [m for m in dir(Article) if not m.startswith('_')]
    for method in article_methods[:10]:
        print(f"    • {method}")


def test_custom_url_filtering():
    """Test if we can customize URL filtering"""

    print("\n" + "=" * 80)
    print("CUSTOM URL FILTERING TEST")
    print("=" * 80)

    config = Config()
    config.language = 'tr'
    config.memoize_articles = False

    # Test on Bianet
    print("\nTesting custom filtering on Bianet...")
    site = build('https://bianet.org', config=config)

    print(f"Default discovery found: {site.size()} articles")

    # Get the category URLs
    print("\nCategory URLs discovered:")
    if hasattr(site, 'category_urls'):
        for cat in list(site.category_urls())[:5]:
            print(f"  • {cat}")

    # Get article URLs
    print("\nArticle URLs discovered:")
    for i, article in enumerate(site.articles[:5], 1):
        print(f"  {i}. {article.url}")

    # Check if we can manually add URLs
    print("\n" + "=" * 80)
    print("CAN WE MANUALLY ADD URLS?")
    print("=" * 80)

    # Try creating article directly
    custom_url = "https://bianet.org/haber/some-article-123"
    custom_article = Article(custom_url, config=config)

    print(f"✓ Can create Article object directly: {custom_article.url}")
    print("✓ Can bypass Source discovery entirely")

    # Check source code location
    print("\n" + "=" * 80)
    print("SOURCE CODE INSPECTION")
    print("=" * 80)

    import newspaper
    print(f"Newspaper4k location: {newspaper.__file__}")

    # Check if Source has customizable filters
    from newspaper.source import Source
    print(f"\nSource class location: {inspect.getfile(Source)}")

    # Get generate_articles method
    if hasattr(Source, 'generate_articles'):
        sig = inspect.signature(Source.generate_articles)
        print(f"generate_articles signature: {sig}")


def conclusion():
    """Print conclusion about customization"""

    print("\n" + "=" * 80)
    print("CONCLUSION: CAN WE FINE-TUNE NEWSPAPER4K?")
    print("=" * 80)

    print("""
❌ LIMITED CUSTOMIZATION

While Newspaper4k has many config options, it does NOT allow:
1. Custom URL pattern matching for article detection
2. Site-specific heuristics or rules
3. Custom HTML selectors for article discovery
4. Fine-tuning the ML/heuristic algorithms

✓ WHAT YOU CAN CUSTOMIZE:
- Language (for stopwords, NLP)
- Parser (lxml, html.parser, html5lib)
- HTTP settings (timeout, user agent, threads)
- Image fetching
- Caching behavior

❌ WHAT YOU CANNOT CUSTOMIZE:
- Article URL detection patterns
- HTML structure recognition
- Category vs article classification
- Link filtering heuristics

💡 WORKAROUNDS:

1. **Bypass Source discovery entirely:**
   - Don't use build()
   - Manually discover URLs (our reliable_discovery.py approach)
   - Use Article() directly for each URL

2. **Extend the Source class:**
   - Subclass newspaper.Source
   - Override generate_articles() method
   - Add custom URL filtering logic

3. **Use hybrid approach (RECOMMENDED):**
   - Use our manual discovery for URLs
   - Use Trafilatura for content extraction
   - Best of both worlds!

VERDICT: Newspaper4k is NOT fine-tuneable enough for Turkish sites.
Use manual discovery + Trafilatura instead.
""")


if __name__ == '__main__':
    explore_newspaper4k_config()
    test_custom_url_filtering()
    conclusion()

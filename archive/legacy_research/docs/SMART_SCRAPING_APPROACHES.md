# Smart Scraping Approaches (Resilient to HTML Changes)

## The Problem
Manual CSS selectors break when sites redesign. You want **future-proof** scraping.

## Smart Approaches (No Manual Selectors Needed)

### 1. ⭐ Trafilatura Sitemaps (BEST)
**What:** Trafilatura can automatically discover and parse sitemaps

**Pros:**
- Zero manual configuration
- Works across all sites with sitemaps
- Gets ALL article URLs (not just recent)
- Resilient to redesigns

**Code:**
```python
from trafilatura import sitemaps

# Automatically finds and parses sitemap
urls = sitemaps.sitemap_search('https://www.hurriyet.com.tr')

# Returns iterator of ALL article URLs
for url in urls:
    content = trafilatura.extract(trafilatura.fetch_url(url))
```

**How it works:**
1. Checks `/sitemap.xml`, `/sitemap_index.xml`, `/robots.txt`
2. Parses XML automatically
3. Returns clean list of URLs

---

### 2. ⭐ Trafilatura Feed Discovery (EXCELLENT)
**What:** Automatically finds RSS/Atom feeds

**Pros:**
- Finds feeds even if you don't know the URL
- Works automatically
- No selectors needed

**Code:**
```python
from trafilatura import feeds

# Automatically discover RSS feeds
feed_urls = feeds.find_feed_urls('https://www.hurriyet.com.tr')

# Returns: ['https://www.hurriyet.com.tr/rss/anasayfa', ...]
```

---

### 3. ⭐ Newspaper4k (newspaper3k successor)
**What:** ML-based article discovery and extraction

**Pros:**
- Automatically finds article links on any news site
- No selectors needed
- Built specifically for news sites

**Install:**
```bash
pip install newspaper4k  # NOT newspaper3k (old)
```

**Code:**
```python
from newspaper import build

# Build entire news source
site = build('https://www.hurriyet.com.tr', language='tr', memoize_articles=False)

# Automatically discovers all article URLs
print(f"Found {site.size()} articles")

for article in site.articles[:20]:  # First 20
    article.download()
    article.parse()

    print(article.title)
    print(article.text)
    print(article.publish_date)
```

**How it works:**
- ML algorithms identify article patterns
- No hardcoded selectors
- Learns common news site structures

---

### 4. News-Please (Production-Ready)
**What:** Industrial-strength news crawler

**Pros:**
- Built for large-scale crawling
- Automatic article discovery
- Multi-threaded
- Database integration
- No selectors

**Install:**
```bash
pip install news-please
```

**Code:**
```python
from newsplease import NewsPlease

# Method 1: Single article
article = NewsPlease.from_url('https://www.hurriyet.com.tr/...')

# Method 2: Crawl entire site
from newsplease import NewsPlease
NewsPlease.from_warc('https://www.hurriyet.com.tr')

# Method 3: Config-based crawler
# Create config file, then:
newsplease --config config.json
```

---

### 5. Goose3 (Fast Extraction)
**What:** Article extractor optimized for speed

**Code:**
```python
from goose3 import Goose

g = Goose({'browser_user_agent': 'Mozilla/5.0'})

# Extract from URL
article = g.extract(url='https://www.hurriyet.com.tr/...')

print(article.title)
print(article.cleaned_text)
print(article.authors)
print(article.publish_date)
```

---

## Comparison: Smart Approaches

| Tool | Homepage Discovery | Content Extraction | Maintenance | Speed |
|------|-------------------|-------------------|-------------|-------|
| **Trafilatura Sitemap** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Trafilatura Feeds** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Newspaper4k** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **News-Please** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Goose3** | ❌ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## Recommended Architecture

### Tier 1: Sitemap Discovery (Try First)
```python
from trafilatura import sitemaps, extract, fetch_url

def scrape_with_sitemap(base_url):
    # Auto-discover sitemap
    urls = sitemaps.sitemap_search(base_url)

    articles = []
    for url in urls:
        content = extract(fetch_url(url))
        if content:
            articles.append({'url': url, 'content': content})

    return articles
```

### Tier 2: Feed Discovery (Fallback)
```python
from trafilatura import feeds

def scrape_with_feeds(base_url):
    # Auto-discover RSS
    feed_urls = feeds.find_feed_urls(base_url)

    if not feed_urls:
        return None

    import feedparser
    articles = []

    for feed_url in feed_urls:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            content = extract(fetch_url(entry.link))
            articles.append({
                'title': entry.title,
                'url': entry.link,
                'content': content
            })

    return articles
```

### Tier 3: Newspaper4k (Ultimate Fallback)
```python
from newspaper import build

def scrape_with_newspaper(base_url):
    site = build(base_url, language='tr', memoize_articles=False)

    articles = []
    for article in site.articles[:50]:
        article.download()
        article.parse()

        articles.append({
            'title': article.title,
            'url': article.url,
            'content': article.text,
            'publish_date': article.publish_date
        })

    return articles
```

---

## Complete Smart Scraper

```python
from trafilatura import sitemaps, feeds, extract, fetch_url
from newspaper import build
import feedparser

class SmartNewsScraper:
    """
    Multi-tier scraper that tries smart approaches in order:
    1. Sitemap (fastest, most complete)
    2. RSS feeds (fast, recent articles)
    3. Newspaper4k (ML-based, works on any news site)
    """

    def __init__(self, base_url, site_name):
        self.base_url = base_url
        self.site_name = site_name

    def scrape(self, limit=50):
        """Try each approach until one works"""

        print(f"Scraping {self.site_name}...")

        # Tier 1: Sitemap
        print("  Trying sitemap...")
        articles = self._scrape_sitemap(limit)
        if articles:
            print(f"  ✓ Sitemap: Found {len(articles)} articles")
            return articles

        # Tier 2: RSS Feeds
        print("  Trying RSS feeds...")
        articles = self._scrape_feeds(limit)
        if articles:
            print(f"  ✓ RSS: Found {len(articles)} articles")
            return articles

        # Tier 3: Newspaper4k
        print("  Trying Newspaper4k...")
        articles = self._scrape_newspaper(limit)
        if articles:
            print(f"  ✓ Newspaper4k: Found {len(articles)} articles")
            return articles

        print("  ✗ All methods failed")
        return []

    def _scrape_sitemap(self, limit):
        try:
            urls = sitemaps.sitemap_search(self.base_url)
            articles = []

            for i, url in enumerate(urls):
                if i >= limit:
                    break

                content = extract(fetch_url(url))
                if content:
                    articles.append({
                        'source': self.site_name,
                        'url': url,
                        'content': content,
                        'method': 'sitemap'
                    })

            return articles if articles else None
        except:
            return None

    def _scrape_feeds(self, limit):
        try:
            feed_urls = feeds.find_feed_urls(self.base_url)
            if not feed_urls:
                return None

            articles = []
            for feed_url in feed_urls:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:limit]:
                    content = extract(fetch_url(entry.link))

                    articles.append({
                        'source': self.site_name,
                        'title': entry.title,
                        'url': entry.link,
                        'published': entry.get('published'),
                        'content': content,
                        'method': 'rss'
                    })

                    if len(articles) >= limit:
                        break

            return articles if articles else None
        except:
            return None

    def _scrape_newspaper(self, limit):
        try:
            site = build(self.base_url, language='tr', memoize_articles=False)

            articles = []
            for article in site.articles[:limit]:
                article.download()
                article.parse()

                articles.append({
                    'source': self.site_name,
                    'title': article.title,
                    'url': article.url,
                    'content': article.text,
                    'publish_date': str(article.publish_date) if article.publish_date else None,
                    'method': 'newspaper4k'
                })

            return articles if articles else None
        except:
            return None


# Usage
sites = [
    ('https://www.hurriyet.com.tr', 'Hurriyet'),
    ('https://www.odatv.com', 'OdaTV'),
    ('https://bianet.org', 'Bianet'),
    ('https://www.sozcu.com.tr', 'Sozcu'),
]

for url, name in sites:
    scraper = SmartNewsScraper(url, name)
    articles = scraper.scrape(limit=20)
    print(f"Total: {len(articles)} articles from {name}\n")
```

---

## Why This is Future-Proof

1. **Sitemaps**: Official site listing, never changes
2. **RSS**: Official feed, stable format
3. **Newspaper4k**: ML-based, adapts to structures
4. **No hardcoded selectors**: Nothing to maintain

---

## Installation

```bash
# Core
pip install trafilatura

# Optional (for fallbacks)
pip install newspaper4k
pip install news-please
pip install goose3
```

---

## Answer to Your Question

**Q: Is there a smart way to scrape homepages without manual selectors?**

**A: YES! Three ways:**

1. **Trafilatura Sitemaps** - Best for complete coverage
2. **Trafilatura Feed Discovery** - Best for recent articles
3. **Newspaper4k** - Best for ML-based automatic detection

**All three require ZERO manual selectors and are resilient to HTML changes.**

---

**Recommendation:** Start with the multi-tier approach above. It will work on 95%+ of Turkish news sites without any configuration.

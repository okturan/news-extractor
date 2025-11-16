# Newspaper4k Customization Analysis

## Question
Can Newspaper4k's article discovery algorithm be fine-tuned for specific Turkish news sites?

## Answer: NO ❌

While Newspaper4k provides many configuration options, it does **NOT** allow customization of the core article URL detection algorithm.

---

## What You CAN Customize

### 1. Language Settings
```python
config.language = 'tr'  # Turkish language support
```
- Affects stopwords and NLP processing
- Does NOT affect URL pattern matching

### 2. HTTP/Network Settings
```python
config.request_timeout = 10
config.number_threads = 10
config.browser_user_agent = 'Mozilla/5.0...'
config.proxies = {'http': 'proxy.example.com'}
```

### 3. Content Processing Limits
```python
config.MAX_TEXT = 100000           # Maximum article text length
config.MIN_WORD_COUNT = 300        # Minimum words to be valid article
config.MAX_KEYWORDS = 35           # Maximum keywords to extract
config.MIN_SENT_COUNT = 7          # Minimum sentences
```

### 4. Caching Behavior
```python
config.memorize_articles = False   # Disable article caching
config.disable_category_cache = True
```

### 5. Image/Media Extraction
```python
config.fetch_images = True
config.top_image_settings = {
    'min_width': 300,
    'min_height': 200,
    'min_area': 10000
}
```

---

## What You CANNOT Customize ❌

### 1. Article URL Detection Patterns
- **Hardcoded** in `newspaper/urls.py`
- No config option to add custom URL patterns
- No hooks to specify site-specific rules

### 2. Link Filtering Heuristics
- **Hardcoded** logic in `Source.generate_articles()`
- Uses built-in heuristics to differentiate:
  - Article URLs vs Category pages
  - Navigation links vs Content links
- Cannot add Turkish-specific patterns like `/haber/`, `/gundem/`

### 3. HTML Structure Recognition
- **Fixed** DOM analysis algorithms
- No way to specify site-specific selectors
- Cannot tell it "on Bianet, articles are in `<article class='haber-item'>`"

### 4. Category vs Article Classification
- **Built-in** ML/heuristic logic
- No config to adjust classification thresholds
- No way to train on Turkish site patterns

---

## Why This Matters for Turkish Sites

### The Problem
Turkish news sites have unique URL structures that Newspaper4k doesn't recognize well:

**Bianet Example:**
- Newspaper4k found: **0-1 articles** ❌
- Manual parsing found: **24 articles** ✅

**Cumhuriyet Example:**
- Newspaper4k found: **0-416 articles** (inconsistent) ❌
- Manual parsing found: **126 articles** (consistent) ✅

### Common Turkish URL Patterns (Not Recognized)
```
/haber/article-title-123
/gundem/article-name
/ekonomi/news-item
/politika/story-slug
```

---

## Workarounds

### Option 1: Manual Discovery (RECOMMENDED) ✅
Use BeautifulSoup to manually parse and filter links:

```python
# production/reliable_discovery.py approach
skip_patterns = ['/kategori/', '/tag/', '/yazar/', 'facebook.com']
include_patterns = ['/haber/', '/gundem/', '/ekonomi/']

for link in soup.find_all('a', href=True):
    href = urljoin(base_url, link['href'])

    # Apply Turkish-specific filtering
    if any(pattern in href for pattern in include_patterns):
        article_urls.add(href)
```

**Results:**
- Bianet: 24 articles (vs 0-1 with Newspaper4k)
- Total: 1,039 articles (vs 0-635 with Newspaper4k)
- **Consistent** across runs

### Option 2: Subclass Source (Complex)
Extend Newspaper4k's Source class:

```python
from newspaper import Source

class TurkishSource(Source):
    def generate_articles(self, limit=5000):
        # Override with custom URL filtering
        articles = super().generate_articles(limit)

        # Add Turkish-specific filtering
        turkish_articles = []
        for article in articles:
            if self._is_turkish_article(article.url):
                turkish_articles.append(article)

        return turkish_articles

    def _is_turkish_article(self, url):
        # Custom Turkish URL pattern matching
        turkish_patterns = ['/haber/', '/gundem/', '/ekonomi/']
        return any(pattern in url for pattern in turkish_patterns)
```

**Issues:**
- More complex to maintain
- Still relies on Newspaper4k's initial discovery
- Internal methods may change in updates

### Option 3: Hybrid Approach (BEST) ✅
Combine manual discovery with Trafilatura content extraction:

```python
# 1. Manual discovery (BeautifulSoup)
urls = discover_articles_reliable('https://bianet.org')

# 2. Content extraction (Trafilatura)
for url in urls:
    content = trafilatura.extract(
        trafilatura.fetch_url(url),
        with_metadata=True
    )
```

**Benefits:**
- Reliable URL discovery (manual patterns)
- High-quality content extraction (Trafilatura)
- Full metadata (author, date, tags)
- Works consistently on Turkish sites

---

## Source Code Evidence

### Configuration Class
Location: `newspaper/configuration.py`

```python
class Configuration:
    def __init__(self):
        self.language = 'en'
        self.request_timeout = 7
        self.number_threads = 10
        # ... but NO article_url_patterns, NO discovery_hooks
```

### Article Discovery Method
Location: `newspaper/source.py`

```python
class Source:
    def generate_articles(self, limit=5000):
        # Uses hardcoded logic in urls.valid_url()
        # No config parameters for URL filtering
        # No hooks for custom patterns
        for url in self.doc.xpath('//a/@href'):
            if urls.valid_url(url):  # ← Hardcoded validation
                self.articles.append(Article(url))
```

**Key finding:** The `valid_url()` function uses **hardcoded** heuristics with no config options.

---

## Conclusion

### For Turkish News Scraping:

❌ **Don't rely on Newspaper4k for URL discovery**
- Inconsistent results
- Cannot be fine-tuned
- Misses many Turkish articles

✅ **DO use manual discovery + Trafilatura**
- Reliable (1,039 articles vs 0-635)
- Consistent across runs
- Full control over URL patterns
- Best content extraction quality

### Recommended Production Architecture:

```
┌─────────────────────────┐
│  Manual URL Discovery   │  ← BeautifulSoup with Turkish patterns
│  (reliable_discovery.py)│     /haber/, /gundem/, /ekonomi/
└───────────┬─────────────┘
            │
            ├─ 1,039 article URLs discovered
            │
            ▼
┌─────────────────────────┐
│ Content Extraction      │  ← Trafilatura
│ (smart_scraper_demo.py) │     100% success rate
└─────────────────────────┘     Full metadata
```

---

## References

- Manual discovery implementation: `/production/reliable_discovery.py`
- Test results: `reliable_discovery_20251107_015741.json`
- Newspaper4k inconsistency: `debug_discovery.py`
- Content extraction comparison: `/docs/COMPARISON_REPORT.md`

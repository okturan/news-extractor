# Complete Guide: All Ways to Scrape Turkish News Sites

## Approach Comparison

| Method | Speed | Reliability | Blocking Risk | Setup Difficulty | Best For |
|--------|-------|-------------|---------------|------------------|----------|
| **1. RSS Feeds** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ None | ⭐ Very Easy | **BEST - Use this first!** |
| **2. Trafilatura** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ Low | ⭐ Very Easy | Article content extraction |
| **3. Playwright** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ Medium | ⭐⭐⭐ Moderate | Dynamic content, JS-heavy sites |
| **4. Sitemaps** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ None | ⭐ Easy | Discovering all URLs |
| **5. Google News** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⚠️ Low | ⭐⭐ Easy | Multi-site aggregation |
| **6. APIs (Official)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ None | ⭐⭐ Easy | If available (rare) |
| **7. BeautifulSoup** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⚠️ Medium | ⭐⭐⭐⭐ Hard | Simple HTML sites |

---

## 1. RSS Feeds ⭐ BEST APPROACH

**What:** News sites publish XML feeds with recent articles

**Pros:**
- Official, intended for consumption
- Fast and lightweight
- Structured data (title, link, date, summary)
- No blocking risk
- Updates automatically

**Cons:**
- Limited to recent articles (usually 20-50)
- Sometimes truncated content
- Not all sites have feeds

### Hurriyet RSS Feeds

```python
import feedparser

# Available RSS feeds
feeds = {
    'anasayfa': 'https://www.hurriyet.com.tr/rss/anasayfa',
    'gundem': 'https://www.hurriyet.com.tr/rss/gundem',
    'ekonomi': 'https://www.hurriyet.com.tr/rss/ekonomi',
    'spor': 'https://www.hurriyet.com.tr/rss/spor',
    'dunya': 'https://www.hurriyet.com.tr/rss/dunya',
    'magazin': 'https://www.hurriyet.com.tr/rss/magazin',
}

def scrape_rss(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries:
        articles.append({
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.description,
            'category': entry.get('category', ''),
        })

    return articles

# Get all articles
for category, url in feeds.items():
    articles = scrape_rss(url)
    print(f"{category}: {len(articles)} articles")
```

### Finding RSS Feeds

Common patterns:
```
/rss
/rss.xml
/feed
/feed.xml
/rss/anasayfa
/kategori/rss
```

Check site for RSS icon or look in HTML:
```python
import requests
from bs4 import BeautifulSoup

def find_rss_feeds(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for RSS links
    rss_links = soup.find_all('link', type='application/rss+xml')

    for link in rss_links:
        print(link.get('href'))
```

---

## 2. Sitemaps

**What:** XML files listing all URLs on a website

**Pros:**
- Discover ALL article URLs
- Official listing from the site
- No blocking risk
- Often includes dates

**Location:** `https://site.com/sitemap.xml`

```python
import requests
from xml.etree import ElementTree as ET

def get_sitemap_urls(sitemap_url):
    response = requests.get(sitemap_url)
    root = ET.fromstring(response.content)

    # Handle sitemap index (points to other sitemaps)
    if 'sitemapindex' in root.tag:
        sitemaps = []
        for sitemap in root.findall('.//{*}loc'):
            sitemaps.append(sitemap.text)
        return sitemaps

    # Handle regular sitemap
    urls = []
    for url in root.findall('.//{*}url'):
        loc = url.find('{*}loc').text
        lastmod = url.find('{*}lastmod')
        lastmod = lastmod.text if lastmod is not None else None

        urls.append({
            'url': loc,
            'lastmod': lastmod
        })

    return urls

# Example
urls = get_sitemap_urls('https://www.hurriyet.com.tr/sitemap.xml')
```

---

## 3. Google News RSS

**What:** Google aggregates news from multiple sources

**Pros:**
- Multi-site coverage
- Topic-based filtering
- No site-specific scraping needed

**Example:**
```python
import feedparser

# Turkey news in Turkish
feed_url = "https://news.google.com/rss/search?q=when:24h+allinurl:haberler&hl=tr&gl=TR&ceid=TR:tr"

feed = feedparser.parse(feed_url)

for entry in feed.entries:
    print(entry.title)
    print(entry.link)
    print(entry.source.title)  # Source site
```

**Custom queries:**
```
# Last 24 hours, Turkish news
https://news.google.com/rss/search?q=when:24h&hl=tr&gl=TR&ceid=TR:tr

# Specific topic
https://news.google.com/rss/search?q=ekonomi+when:1d&hl=tr&gl=TR&ceid=TR:tr

# Specific site
https://news.google.com/rss/search?q=site:hurriyet.com.tr+when:12h&hl=tr&gl=TR&ceid=TR:tr
```

---

## 4. Trafilatura (Article Content)

**What:** Automatic content extraction library

**When to use:** After getting URLs from RSS/sitemap

```python
import trafilatura

def extract_article(url):
    downloaded = trafilatura.fetch_url(url)

    metadata = trafilatura.extract_metadata(downloaded)
    content = trafilatura.extract(downloaded)

    return {
        'url': url,
        'title': metadata.title if metadata else None,
        'author': metadata.author if metadata else None,
        'date': metadata.date if metadata else None,
        'content': content
    }
```

---

## 5. Playwright (Dynamic Sites)

**What:** Browser automation for JS-heavy sites

**When to use:**
- Site requires JavaScript
- Need to interact with page (scroll, click)
- RSS/static scraping doesn't work

```python
from playwright.async_api import async_playwright

async def scrape_dynamic():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto('https://www.odatv.com/')
        await page.wait_for_selector('article')

        # Extract links
        links = await page.query_selector_all('a[href*="/guncel/"]')

        urls = []
        for link in links:
            href = await link.get_attribute('href')
            urls.append(href)

        await browser.close()
        return urls
```

---

## 6. BeautifulSoup (Simple HTML)

**What:** Parse static HTML

**When to use:**
- Simple sites without JavaScript
- You need full control
- Quick one-off scraping

```python
import requests
from bs4 import BeautifulSoup

def scrape_html(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find articles
    articles = soup.find_all('article')

    results = []
    for article in articles:
        title = article.find('h2')
        link = article.find('a')

        if title and link:
            results.append({
                'title': title.text.strip(),
                'link': link['href']
            })

    return results
```

---

## 7. Web Scraping Services

**What:** Third-party APIs that scrape for you

**Examples:**
- ScraperAPI
- Bright Data
- Apify
- Diffbot

**Pros:**
- Handle blocking, CAPTCHAs
- Manage proxies
- Scale easily

**Cons:**
- Costs money
- Privacy concerns

---

## Recommended Strategy for Turkish News

### Option A: RSS + Trafilatura (BEST)

```python
import feedparser
import trafilatura

# Step 1: Get URLs from RSS
feed = feedparser.parse('https://www.hurriyet.com.tr/rss/anasayfa')

# Step 2: Extract content from each URL
for entry in feed.entries:
    content = trafilatura.extract(
        trafilatura.fetch_url(entry.link)
    )

    article = {
        'title': entry.title,
        'link': entry.link,
        'published': entry.published,
        'content': content
    }

    # Save to database
    save_article(article)
```

**Pros:**
- Fast (RSS is quick)
- Reliable (official feed)
- Complete content (Trafilatura)
- No blocking risk

### Option B: Sitemap + Trafilatura

For historical data or sites without RSS:

```python
# Get all URLs from sitemap
urls = get_sitemap_urls('https://site.com/sitemap.xml')

# Filter for recent articles
recent = [u for u in urls if '2025-11' in u['lastmod']]

# Extract content
for url_data in recent:
    content = trafilatura.extract(
        trafilatura.fetch_url(url_data['url'])
    )
```

### Option C: Playwright + Trafilatura

For JavaScript-heavy sites:

```python
# 1. Use Playwright to discover URLs
urls = await scrape_dynamic_site()

# 2. Use Trafilatura for content
for url in urls:
    content = trafilatura.extract(trafilatura.fetch_url(url))
```

---

## Complete Example: Multi-Site RSS Aggregator

```python
import feedparser
import trafilatura
from datetime import datetime
import sqlite3

# Define RSS feeds
FEEDS = {
    'hurriyet': {
        'anasayfa': 'https://www.hurriyet.com.tr/rss/anasayfa',
        'gundem': 'https://www.hurriyet.com.tr/rss/gundem',
        'ekonomi': 'https://www.hurriyet.com.tr/rss/ekonomi',
    },
    # Add more sites as you find their RSS feeds
}

def scrape_all_feeds():
    """Scrape all RSS feeds and extract full content"""

    all_articles = []

    for site, categories in FEEDS.items():
        for category, feed_url in categories.items():
            print(f"Scraping {site}/{category}...")

            # Parse RSS
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                # Extract full content with Trafilatura
                content = trafilatura.extract(
                    trafilatura.fetch_url(entry.link),
                    include_comments=False
                )

                article = {
                    'site': site,
                    'category': category,
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('description', ''),
                    'content': content,
                    'scraped_at': datetime.now().isoformat()
                }

                all_articles.append(article)

    return all_articles

def save_to_database(articles):
    """Save articles to SQLite database"""

    conn = sqlite3.connect('news.db')
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (site TEXT, category TEXT, title TEXT, link TEXT UNIQUE,
                  published TEXT, summary TEXT, content TEXT, scraped_at TEXT)''')

    # Insert articles
    for article in articles:
        try:
            c.execute('''INSERT OR IGNORE INTO articles VALUES
                         (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (article['site'], article['category'], article['title'],
                       article['link'], article['published'], article['summary'],
                       article['content'], article['scraped_at']))
        except Exception as e:
            print(f"Error saving: {e}")

    conn.commit()
    conn.close()

# Run
if __name__ == '__main__':
    articles = scrape_all_feeds()
    save_to_database(articles)
    print(f"Saved {len(articles)} articles")
```

---

## Summary: Choose Based on Your Needs

### For Real-Time News Monitoring
→ **RSS + Trafilatura** (Best balance)

### For Historical Archive
→ **Sitemap + Trafilatura**

### For JavaScript-Heavy Sites
→ **Playwright + Trafilatura**

### For Multi-Site Aggregation
→ **Google News RSS**

### For One-Time Data Collection
→ **BeautifulSoup** (simplest)

---

## Turkish News Sites with RSS

### Confirmed RSS Feeds:
- ✅ **Hurriyet** - https://www.hurriyet.com.tr/rss/anasayfa
- ⚠️ **OdaTV** - Need to test other URLs
- ⚠️ **Milliyet** - Need to test
- **Add more as you find them**

### How to Find More RSS Feeds

1. Check common URLs:
   - `/rss`
   - `/rss.xml`
   - `/feed`
   - `/rss/anasayfa`

2. Look in page source for:
   ```html
   <link rel="alternate" type="application/rss+xml" href="...">
   ```

3. Try adding `/rss` to category URLs:
   - `site.com/gundem` → `site.com/gundem/rss`

---

**Bottom Line:** Start with RSS + Trafilatura. It's fast, reliable, and won't get you blocked!

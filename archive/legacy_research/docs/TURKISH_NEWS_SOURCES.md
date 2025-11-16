# Turkish News Sources - RSS Availability

## Confirmed RSS Feeds ✅

### Hurriyet (Hürriyet)
- **RSS:** https://www.hurriyet.com.tr/rss/anasayfa
- **Format:** application/rss+xml
- **Status:** ✅ Working
- **Categories:**
  - Anasayfa: /rss/anasayfa
  - Gündem: /rss/gundem
  - Ekonomi: /rss/ekonomi
  - Spor: /rss/spor
  - Dünya: /rss/dunya

### OdaTV
- **RSS:** https://www.odatv.com/rss.xml
- **Format:** text/xml
- **Status:** ✅ Working

### T24
- **RSS:** https://www.t24.com.tr/rss
- **Format:** text/xml
- **Status:** ✅ Working

### Diken
- **RSS:** https://www.diken.com.tr/rss
- **Alternate:** https://www.diken.com.tr/feed
- **Format:** application/rss+xml
- **Status:** ✅ Working

### Gazete Duvar
- **RSS:** https://www.gazeteduvar.com.tr/rss
- **Alternate:** https://www.gazeteduvar.com.tr/feed
- **Format:** text/xml
- **Status:** ✅ Working

---

## Needs Verification ⚠️

### Milliyet
- **URL Tried:** /rss, /feed, /rss/anasayfa
- **Status:** ⚠️ Returns HTML, not XML - may not have RSS

### Cumhuriyet
- **URL Tried:** /rss, /rss/anasayfa
- **Status:** ⚠️ Returns HTML, not XML - may not have RSS

---

## No RSS Found ❌

### Sözcü (sozcu.com.tr)
- **Status:** ❌ No RSS feed found

### Bianet (bianet.org)
- **Status:** ❌ No RSS feed found

### BirGün (birgun.net)
- **Status:** ❌ No RSS feed found

---

## Additional Major Turkish News Sites to Check

### Mainstream
- [ ] Sabah (sabah.com.tr)
- [ ] Habertürk (haberturk.com)
- [ ] NTV (ntv.com.tr)
- [ ] CNN Türk (cnnturk.com)
- [ ] TRT Haber (trthaber.com)
- [ ] Anadolu Ajansı (aa.com.tr)

### Independent/Opposition
- [ ] Medyascope (medyascope.tv)
- [ ] Artı Gerçek (artigercek.com)
- [ ] Tele 1 (tele1.com.tr)
- [ ] KRT (krt.com.tr)
- [ ] Halk TV (halktv.com.tr)

---

## Recommendation: Hybrid Approach

Since NOT all major Turkish news sites have RSS feeds, here's the optimal strategy:

### Tier 1: RSS-Based (5 sites) ✅
Use RSS + Trafilatura for these:
- Hurriyet
- OdaTV
- T24
- Diken
- Gazete Duvar

**Code:**
```python
RSS_FEEDS = {
    'hurriyet': 'https://www.hurriyet.com.tr/rss/anasayfa',
    'odatv': 'https://www.odatv.com/rss.xml',
    't24': 'https://www.t24.com.tr/rss',
    'diken': 'https://www.diken.com.tr/rss',
    'gazeteduvar': 'https://www.gazeteduvar.com.tr/rss',
}
```

### Tier 2: Scraping-Based (For sites without RSS) 🔧

Use **Trafilatura + Homepage Link Discovery** for these:
- Sözcü
- Bianet
- BirGün
- Cumhuriyet (if RSS doesn't work)
- Milliyet (if RSS doesn't work)

**Options for Link Discovery:**
1. **Sitemap** (fastest if available)
2. **Playwright** (for JS-heavy sites)
3. **BeautifulSoup** (for static HTML)

### Tier 3: Google News Aggregation 🌐

As a fallback or supplement:
```python
google_news_rss = f"https://news.google.com/rss/search?q=site:{domain}+when:24h&hl=tr&gl=TR&ceid=TR:tr"
```

---

## Proposed Architecture

```python
class TurkishNewsScraper:
    def __init__(self):
        self.rss_sources = {
            'hurriyet': 'https://www.hurriyet.com.tr/rss/anasayfa',
            'odatv': 'https://www.odatv.com/rss.xml',
            't24': 'https://www.t24.com.tr/rss',
            'diken': 'https://www.diken.com.tr/rss',
            'gazeteduvar': 'https://www.gazeteduvar.com.tr/rss',
        }

        self.scraping_sources = {
            'sozcu': 'https://www.sozcu.com.tr/',
            'bianet': 'https://bianet.org/',
            'birgun': 'https://www.birgun.net/',
        }

    def get_articles_rss(self, source_name):
        """Get articles from RSS feed"""
        feed_url = self.rss_sources[source_name]
        feed = feedparser.parse(feed_url)

        articles = []
        for entry in feed.entries:
            # Get full content with Trafilatura
            content = trafilatura.extract(
                trafilatura.fetch_url(entry.link)
            )

            articles.append({
                'source': source_name,
                'title': entry.title,
                'link': entry.link,
                'published': entry.get('published'),
                'content': content
            })

        return articles

    def get_articles_scraping(self, source_name):
        """Get articles by scraping homepage"""
        base_url = self.scraping_sources[source_name]

        # Step 1: Get article URLs from homepage
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find article links (site-specific selectors)
        links = self._find_article_links(soup, source_name)

        # Step 2: Extract content with Trafilatura
        articles = []
        for link in links[:20]:  # Limit to recent 20
            content = trafilatura.extract(
                trafilatura.fetch_url(link)
            )

            articles.append({
                'source': source_name,
                'link': link,
                'content': content
            })

        return articles

    def scrape_all(self):
        """Scrape all sources"""
        all_articles = []

        # RSS sources
        for source in self.rss_sources:
            all_articles.extend(self.get_articles_rss(source))

        # Scraping sources
        for source in self.scraping_sources:
            all_articles.extend(self.get_articles_scraping(source))

        return all_articles
```

---

## Next Steps

1. ✅ Verified 5 sites with working RSS feeds
2. ⚠️ Need to test Milliyet and Cumhuriyet RSS (may be broken)
3. 🔧 Need to add scraping logic for non-RSS sites
4. 📋 Should expand list with more major Turkish news sites

**Do you want me to:**
A. Create a working scraper that uses RSS for the 5 confirmed sites?
B. Check more news sites for RSS availability?
C. Build the full hybrid scraper (RSS + scraping)?
D. Something else?

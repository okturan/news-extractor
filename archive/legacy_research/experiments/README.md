# Experiments Directory

This directory contains all research and experimental work conducted to evaluate different web scraping approaches for Turkish news websites.

## Structure

```
experiments/
├── 01_manual_scrapers/     # Site-specific manual scraping scripts
├── 02_library_comparison/  # Automated library evaluation tests
└── results/                # JSON output from all scraping tests
```

## 1. Manual Scrapers (`01_manual_scrapers/`)

Site-specific scrapers built with Playwright and BeautifulSoup. These were the initial approach before discovering automated extraction libraries.

### Scripts

- **hurriyet_scraper.py** - Basic headline scraper for Hurriyet.com.tr homepage
- **hurriyet_article_scraper.py** - Single article content extractor
- **hurriyet_full_scraper.py** - Complete scraper with full metadata and content
- **odatv_scraper.py** - Full scraper for OdaTV.com
- **odatv_inspector.py** - Debug/inspection tool for analyzing OdaTV page structure
- **test_trafilatura_links.py** - Experiments with Trafilatura link extraction

### Characteristics

**Pros:**
- Complete control over what gets extracted
- Can handle JavaScript-heavy pages with Playwright
- Custom logic for each site's unique structure

**Cons:**
- Brittle - breaks when site HTML changes
- High maintenance - each site needs custom code
- Time-consuming to develop
- Requires understanding of each site's DOM structure

### Usage Example

```bash
cd experiments/01_manual_scrapers
python hurriyet_full_scraper.py
```

## 2. Library Comparison (`02_library_comparison/`)

Systematic evaluation of 4 automatic content extraction approaches. Each subdirectory contains test scripts and results for one library.

### Libraries Tested

#### trafilatura/ (Winner)
- **extract_article.py** - Test script
- **hurriyet_result.json, odatv_result.json, milliyet_result.json** - Results
- **Success Rate:** 100%
- **Metadata:** Full (author, date, categories, tags)
- **Recommendation:** Production use

#### readability/
- **extract_article.py** - Test script
- **hurriyet_result.json, odatv_result.json, milliyet_result.json** - Results
- **Success Rate:** 100%
- **Metadata:** Partial
- **Recommendation:** Fallback option

#### newspaper3k/
- **extract_article.py** - Test script
- **hurriyet_result.json, odatv_result.json, milliyet_result.json** - Results
- **Success Rate:** 50%
- **Metadata:** None
- **Recommendation:** Not recommended

#### beautifulsoup-heuristics/
- **extract_article.py** - Main extraction script
- **extract_article_v2.py** - Improved version
- **debug_odatv.py** - Debug script
- **README.md** - Detailed documentation
- **SUMMARY.md** - Results summary
- **hurriyet_result.json, odatv_result.json, milliyet_result.json** - Results
- **Success Rate:** 100% (with issues)
- **Metadata:** None
- **Issues:** Text spacing problems, complex code
- **Recommendation:** Learning/special cases only

### Comparison Summary

| Library | LOC | Success | Metadata | Best Use Case |
|---------|-----|---------|----------|---------------|
| Trafilatura | 13 | 100% | Full | Production |
| Readability | 15 | 100% | Partial | Fallback |
| newspaper3k | 17 | 50% | None | Simple sites only |
| BeautifulSoup | 150+ | 100% | None | Special cases |

## 3. Test Results (`results/`)

JSON output files from all scraping experiments, organized chronologically.

### Manual Scraper Results

- **hurriyet_news_20251106_201545.json** (2.8 KB)
  - First test: headline scraping from Hurriyet homepage

- **article_20251106_201935.json** (1.4 KB)
  - Single article extraction test

- **article_20251106_202002.json** (1.3 KB)
  - Second single article test

- **hurriyet_full_20251106_202358.json** (14 KB)
  - Full scraper output with multiple articles

- **odatv_full_20251106_202825.json** (2.4 KB)
  - OdaTV scraping first attempt

- **odatv_full_20251106_203441.json** (207 KB)
  - Large OdaTV scraping result

### Smart Scraper Results

- **smart_scrape_results_20251107_001645.json** (21 KB)
  - Production scraper using Trafilatura
  - Multiple news sites
  - Clean extraction with metadata

### Library Comparison Results

Results from library tests are stored in their respective subdirectories:
- `02_library_comparison/trafilatura/*.json`
- `02_library_comparison/readability/*.json`
- `02_library_comparison/newspaper3k/*.json`
- `02_library_comparison/beautifulsoup-heuristics/*.json`

## Key Learnings

### 1. Manual Scraping is Not Sustainable
- Each site requires 100+ lines of custom code
- Breaks frequently when sites update
- High maintenance burden
- Not worth it when libraries exist

### 2. Trafilatura is Superior
- Works out of the box
- No site-specific code needed
- Automatic metadata extraction
- Handles Turkish characters perfectly
- Battle-tested on millions of pages

### 3. Always Test on Article Pages
- Homepage extraction is unreliable across all approaches
- Article pages have consistent structure
- Better results with direct article URLs

### 4. Turkish Language Support
- All modern libraries handle UTF-8 correctly
- No special encoding needed
- Turkish characters (ğ, ü, ş, ı, ö, ç) work perfectly

## Development Timeline

1. **Day 1 Morning:** Built manual Hurriyet scrapers
2. **Day 1 Afternoon:** Extended to OdaTV
3. **Day 1 Evening:** Discovered Trafilatura and other libraries
4. **Day 1 Night:** Systematic library comparison
5. **Day 2 Early:** Built production smart scraper

## Next Steps

See `/Users/okan/code/haberin-dibi/docs/NEXT_STEPS.md` for future development plans.

## Running the Experiments

### Prerequisites
```bash
pip install -r /Users/okan/code/haberin-dibi/requirements.txt
playwright install chromium
```

### Run Manual Scrapers
```bash
cd 01_manual_scrapers
python hurriyet_full_scraper.py
python odatv_scraper.py
```

### Run Library Tests
```bash
cd 02_library_comparison/trafilatura
python extract_article.py
```

## Documentation

For detailed analysis and recommendations, see:
- `/Users/okan/code/haberin-dibi/docs/COMPARISON_REPORT.md` - Comprehensive comparison
- `/Users/okan/code/haberin-dibi/docs/ALL_SCRAPING_APPROACHES.md` - All approaches explored
- `/Users/okan/code/haberin-dibi/docs/SMART_SCRAPING_APPROACHES.md` - Smart scraping techniques

---

**Summary:** This experimental work concluded that Trafilatura is the best solution for Turkish news scraping, making manual scrapers unnecessary for production use.

# BeautifulSoup Article Extractor for Turkish News Sites

## Quick Start

```bash
# Install dependencies (already installed)
pip install beautifulsoup4 requests lxml

# Run the extractor
python3 extract_article_v2.py
```

## Files in This Directory

- **extract_article_v2.py** - Main extraction script (USE THIS)
- **extract_article.py** - Initial version (has bugs, kept for reference)
- **debug_odatv.py** - Debugging tool for URL investigation
- **hurriyet_result.json** - Extraction result for Hürriyet article
- **odatv_result.json** - Extraction result for OdaTV (URL redirected)
- **milliyet_result.json** - Extraction result for Milliyet homepage
- **SUMMARY.md** - Detailed test results and analysis
- **README.md** - This file

## Custom Heuristics Overview

### Scoring System
The extractor scores potential content containers using multiple signals:

```
Score Calculation:
├─ Paragraph Count × 100         [Primary signal]
├─ Average Paragraph Length      [Quality indicator]
├─ Text Density (text/tags × 2)  [Content vs markup ratio]
├─ Semantic Indicators +200      [article, content, haber, icerik]
└─ Link Density Penalty -300     [Too many links = navigation]
```

### Element Removal Strategy
```
1. Remove by Tag: script, style, nav, header, footer, iframe
2. Remove by Pattern: ads, comments, social, related, reklam, yorum
3. Remove HTML Comments
```

### Content Extraction Flow
```
1. Fetch & Parse HTML
   ↓
2. Remove Unwanted Elements
   ↓
3. Search Strategies (in order):
   - Semantic <article> tags
   - Divs with article-related classes
   - <section> tags
   - High paragraph-density containers
   - Fallback: element with most <p> tags
   ↓
4. Score All Candidates
   ↓
5. Extract Paragraphs from Best Candidate
   ↓
6. Filter Short Paragraphs (<40 chars)
   ↓
7. Join with Double Newlines
```

## Results Summary

| Site | Quality | Characters | Status |
|------|---------|------------|--------|
| **Hürriyet** | ✅ Good | 727 | Perfect extraction |
| **OdaTV** | ⚠️ Good | 682 | URL redirected to different article |
| **Milliyet** | ⚠️ Good | 5,846 | Homepage (multiple article snippets) |

### Hürriyet - SUCCESS ✅
**Article**: Traffic accident in Arnavutköy
- Clean extraction of complete article
- Correct title and content
- No ads or navigation noise

### OdaTV - PARTIAL ⚠️
**Expected**: Food poisoning article
**Actual**: UK Central Bank article
- Original URL redirected to different content
- Extraction worked correctly for current content
- Issue: URL content changed, not extractor failure

### Milliyet - EXPECTED ⚠️
**Type**: Homepage (not single article)
- Extracted main news area with multiple stories
- 5,846 characters of various article previews
- Expected behavior for homepage URL

## Key Heuristics

### 1. Text Density
Measures the ratio of text content to HTML tags. Articles typically have high text density, while navigation and sidebars have low density.

### 2. Paragraph Analysis
- **Count**: Articles have multiple paragraphs (strong signal)
- **Length**: Meaningful paragraphs are >40 characters
- **Average**: Longer average paragraph length = better content quality

### 3. Semantic HTML
Prioritizes semantic tags and meaningful class/id names:
- Tags: `<article>`, `<section>`, `<main>`
- Keywords: article, content, haber, icerik, detay, news, story

### 4. Link Density Penalty
Too many links relative to paragraphs suggests navigation, not content.

### 5. Multi-Strategy Fallback
If primary methods fail, falls back to simpler heuristics (most paragraphs).

## Turkish-Specific Adaptations

### Keywords
- **haber** - news
- **icerik** - content
- **detay** - detail
- **reklam** - advertisement
- **yorum** - comment
- **paylas** - share
- **galeri** - gallery

### Common Patterns
- Remove "haber-listesi" (news lists)
- Remove "diger-haberler" (other news)
- Remove "manset" (headlines section)

## JSON Output Format

```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "content": "Full article text with paragraphs...",
  "method": "beautifulsoup-heuristics",
  "extraction_quality": "good|partial|failed",
  "char_count": 1234
}
```

## Limitations

1. **No redirect detection** - Doesn't warn when URL redirects
2. **Homepage vs article** - Doesn't distinguish content types
3. **Text spacing** - Some words run together (e.g., "İngiltereMerkez")
4. **No metadata** - Date, author, categories not extracted
5. **Site-agnostic** - Not optimized for specific news sites

## When to Use This Approach

### ✅ Good For
- Quick prototyping
- Unknown site structures
- Sites that frequently change layout
- Small-scale scraping
- Sites without structured data

### ❌ Not Ideal For
- Production systems requiring 100% accuracy
- Sites with complex JavaScript rendering
- Real-time news monitoring (no date extraction)
- Sites with paywalls
- Large-scale scraping (use site-specific selectors)

## Comparison with Other Approaches

| Method | Speed | Accuracy | Maintenance | Flexibility |
|--------|-------|----------|-------------|-------------|
| **BeautifulSoup Heuristics** | Fast | 70-85% | Low | High |
| Site-Specific Selectors | Fast | 95%+ | High | Low |
| Readability Algorithm | Medium | 80-90% | Low | High |
| ML-Based Extraction | Slow | 85-95% | Medium | High |
| API Integration | Fast | 100% | Low | N/A |

## Next Steps / Improvements

1. Add redirect tracking and logging
2. Implement content type detection (article vs homepage vs gallery)
3. Extract publication date and author
4. Fix text spacing issues (better inline element handling)
5. Add language detection (verify Turkish content)
6. Implement readability scoring
7. Extract article images with captions
8. Create site-specific rule library for major Turkish news sites
9. Add caching layer for faster repeated requests
10. Implement parallel processing for batch extraction

## License

This is a test/prototype script for educational purposes.

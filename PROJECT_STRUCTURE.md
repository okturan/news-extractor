# Project Structure

## Production Surface ⭐

### Source (`src/news_extractor/`)
- `article_extractor.py` – Newspaper4k primary + Trafilatura fallback implementation (83% success / 0.55s avg).
- `cli.py` – Powers the `news-extractor` executable and `python -m news_extractor.cli` flow.
- `__init__.py` – Exposes `ArticleExtractor` and `extract_article` for downstream imports.

### Packaging & Tooling
- `pyproject.toml` / `poetry.lock` – Poetry-managed metadata, lockfile, and CLI entry point.
- `requirements.txt` – Exported via `poetry export` for environments that cannot use Poetry directly (install with `pip install -r requirements.txt && pip install -e .`).

### Documentation
- `README.md` – Operational guide, workflows, API examples.
- `RESEARCH.md` – Deep dive on experimentation and rationale.

### Examples & Validation
- `examples/batch_extraction.py` – Ready-made batch usage script importing the packaged module.
- `tests/validation/test_ultimate_combo.py` – Live regression suite (83% pass target). Galleries remain out of scope by design.

## Operational Workflow
1. **Bootstrap** – `poetry install`.
2. **Integrate** – Import `ArticleExtractor` (Python jobs) or call the `news-extractor` CLI inside larger workflows/microservices.
3. **Validate** – Run `poetry run python tests/validation/test_ultimate_combo.py` before promoting changes. Investigate any non-gallery failure.
4. **Monitor** – Track success rate and fallback ratio as documented in `README.md` → drop below 80% triggers action.

## Archive (Historical Research) 📦
All prior experimentation is frozen under `archive/legacy_research/`:

| Path | Contents / Notes |
|------|------------------|
| `analysis/` | Narrative reports (`analysis_*`, `newspaper4k_*`, etc.) |
| `docs/` | Earlier documentation set (pre-Nov 2025) |
| `experiments/` | Manual scrapers, Crawl4AI trials, LLM hybrids |
| `production/` | Obsolete Trafilatura-only implementation |
| `scripts/` | Diagnostic helpers (e.g., detailed link discovery) |
| `tests/research_archive/` | Full historical test harness (Crawl4AI, Trafilatura 2.0, etc.) |

These assets are **deprecated**—do not import or execute them inside production flows. They are maintained as evidence for decisions captured in `RESEARCH.md`.

## Repository Map

```
news-extractor/
├── README.md / RESEARCH.md
├── pyproject.toml
├── requirements.txt
├── src/
│   └── news_extractor/
│       ├── __init__.py
│       ├── article_extractor.py
│       └── cli.py
├── tests/
│   └── validation/test_ultimate_combo.py
├── examples/batch_extraction.py
└── archive/
    └── legacy_research/
        ├── analysis/
        ├── docs/
        ├── experiments/
        ├── production/
        ├── scripts/
        └── tests/research_archive/
```

**Last Updated:** November 2025  
**Status:** Production ready ✅ (galleries intentionally excluded)

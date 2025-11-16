# Repository Guidelines

## Project Structure & Module Organization
- `src/news_extractor/` holds the production package: `article_extractor.py` (core logic), `cli.py` (command-line entry), and `__init__.py` (public exports). Treat this directory as the only source for imports.
- `tests/validation/` contains live suites: `test_ultimate_combo.py` (canonical 6-URL benchmark) and `compare_with_jina.py` (side-by-side reader comparison). Galleries intentionally fail—log but do not block.
- `examples/batch_extraction.py` demonstrates batch usage; reuse it when creating new sample code.
- `examples/scrape_news_gatherer_backlog.py`, `examples/view_jsonl.py`, and `examples/backlog_viewer.html` are now documented in `README.md` under "Backlog Inspection Tools"—update both docs and scripts together.
- `archive/legacy_research/` preserves deprecated experiments, docs, and legacy scripts. Never depend on it at runtime; cite it only for research context.

## Build, Test, and Development Commands
- `poetry install` – resolves dependencies, sets up the managed virtualenv, and installs the package.
- `poetry run news-extractor <url ...>` or `poetry run python -m news_extractor.cli <url ...>` – run the extractor against one or more URLs.
- `poetry run python tests/validation/test_ultimate_combo.py` – regression benchmark; expect 5/6 successes (gallery excluded).
- `poetry run python tests/validation/compare_with_jina.py` – compare our output with `https://r.jina.ai/<url>` and review previews manually.

## Coding Style & Naming Conventions
- Python 3.10+ only. Use type hints, `from __future__ import annotations`, and explicit return types (see `article_extractor.py`).
- Follow standard PEP8/Black-style formatting: 4-space indents, snake_case for variables/functions, PascalCase for classes.
- Keep inline comments rare and descriptive (e.g., clarifying fallback logic). Avoid verbose docstrings unless documenting public APIs.

## Testing Guidelines
- Validation scripts reside in `tests/validation/`; replicate their patterns for future suites.
- Name new tests `test_<purpose>.py` and ensure they can run with `poetry run python path/to/test.py`.
- Manual verification is required whenever output previews mention 404/boilerplate text—flag those URLs explicitly in test logs.

## Commit & Pull Request Guidelines
- Git history is not available in this workspace, so default to Conventional Commit style (`feat:`, `fix:`, `docs:`) with concise imperative descriptions.
- PRs should include: summary of changes, affected commands/tests, validation evidence (copy test command + result), and any manual-review notes (e.g., galleries, removed articles).
- Link related issues or TODO references inline so future agents can trace context quickly.

## Security & Configuration Tips
- Never run archived scrapers in production—they may require Playwright or external browsers.
- Network access is restricted; document any URL fetches that need elevated permissions.
- Keep API keys/config out of the repo; rely on environment variables when extending the CLI or FastAPI wrapper.

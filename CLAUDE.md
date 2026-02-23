# CHD Scraper v2

High-fidelity scraper for Trussel's Combined Hawaiian Dictionary (trussel2.com/HAW/).

## Stack
- Python 3.13, Pydantic v2, BeautifulSoup4 + lxml, pytest
- Source package: `src/chd/`
- Next.js frontend also lives in this repo (separate concern)

## Key Conventions
- Activate venv: `source .venv/bin/activate`
- Run tests: `pytest` (from project root)
- All models use Pydantic v2 BaseModel with `exclude_defaults=True` on export
- Hawaiian diacriticals: ʻokina (ʻ, U+02BB) and kahakō (macron vowels: ā ē ī ō ū)
- HTML parsing uses lxml parser with `</p>` injection to fix unclosed tags
- Entry IDs are numeric anchors from the HTML (e.g., "57179")

## Project Structure
- `src/chd/` — main package (models, parsers, utilities)
- `src/chd/parsers/` — per-page-type parsers
- `tests/` — unit tests + per-page fidelity tests
- `tests/fixtures/` — small HTML snippets for testing
- `data/raw/` — downloaded HTML pages (1231 files, ~163MB)
- `data/processed/` — exported JSON
- `reports/` — scrape manifest, parse progress, validation reports

## Data Flow
1. Raw HTML in `data/raw/` → parsers in `src/chd/parsers/`
2. Parsers produce Pydantic models defined in `src/chd/models.py`
3. Export via `src/chd/export.py` → JSON in `data/processed/`
4. Validation via `src/chd/validate.py`

## Reference
- `CHD Complete Capture Guide v4.md` — canonical specification
- `CHD Complete Capture Guide v3.md` — historical reference

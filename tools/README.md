# tools/

Python scripts that do the actual work — the **Tools** layer of WAT.

Each tool should be:
- **Deterministic** — same input, same output
- **Single-purpose** — one job per script
- **Testable** — runnable on its own from the command line
- **Self-documenting** — a docstring at the top stating: what it does, required inputs, outputs

Credentials come from `.env` (never hardcode keys).

Naming: `verb_noun.py` (e.g. `scrape_single_site.py`, `export_to_sheets.py`).

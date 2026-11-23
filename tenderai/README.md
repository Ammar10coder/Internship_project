# TenderAI · Construction tender screening

A local Python application for shortlisting construction tenders. Import a text-based PDF or paste a scope, inspect the extracted text, then save a screening with its category, priority, fit score and decision. Open a saved row to explain its score.

## Run

Use Python 3.11 or later. In the tenderai folder run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

On Windows use `py -3.11 -m venv .venv` and `.venv\Scripts\activate` in Command Prompt. Open **http://127.0.0.1:8010**. If the port is busy, set the PORT environment variable to an available port before launching. The app runs locally after setup and requires no API keys.

## Project structure

```text
main.py                 Launch the local web server
backend/
  api.py                FastAPI endpoints and input validation
  documents.py          Selectable-text PDF extraction
  scoring.py            Category, priority and score rules
  storage.py            SQLite persistence and history filtering
frontend/
  index.html            Screening form and review desk
  app.js                Import, screen, save and filter actions
  style.css             Responsive layout
samples/Boundary-wall.pdf   Fictional tender for the presentation
tests/test_workflow.py   Scoring, PDF import, API and persistence checks
data/tenders.db         Created on first run
requirements.txt        Python dependencies
```

## Two-minute demonstration

1. Upload **samples/Boundary-wall.pdf**. Read the extracted scope and click **Screen and save**. Boundary wall is priority P0. Its base score is 80 and the two matched terms, construction and gate, add 3.5 each. Result: **87, GO**.
2. Choose **School classrooms** and screen it. The category changes to Building construction (P2). Construction and school add eight points to the base of 65. Result: **73, GO**.
3. Choose **Catering services**. Screening checks exclusions first, giving **20, NO-GO**. Filter the saved list to NO-GO, then refresh the page to show that records persist.

The rules illustrate preliminary relevance for a construction team. Phrase matching can miss synonyms or misunderstand negation. Review the scope before making a bid decision. This version uses a plain JavaScript frontend and SQLite. It accepts English text and selectable-text PDFs up to 5 MB and 40 pages. Scanned pages require manual text entry. History displays all matching records.

## Verify

Run `python -m unittest discover -s tests -v`. Tests use a temporary database. Visit `/docs` while the app is running to explore POST /api/extract, POST /api/tenders and GET /api/tenders.

## Tender directory

The home page now shows every saved screening, the most recent successful CPPP latest-listing snapshot and 13 labelled classroom examples from the reference screenshots. Search the cards or filter by source, state, organization, category and decision. Select a card for its details. **Screen PDF** opens the original workflow. **Refresh CPPP** fetches the public latest-listing table on demand. Portal availability and table format can vary. Coverage is limited to that table; missing procurement metadata is left blank. Screenshot scores are historical examples. The saved history includes all records.

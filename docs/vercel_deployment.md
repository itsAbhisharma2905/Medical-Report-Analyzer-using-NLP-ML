# Vercel Deployment

## Architecture

The repository keeps one application with two interfaces:

- `app.py` exports `api.server.app`, the FastAPI ASGI application used by Vercel.
- `frontend/streamlit_app.py` remains the local Streamlit dashboard and is not deployed to Vercel.
- `src/` contains the shared preprocessing, rule-based NER, optional spaCy/scispaCy processing, summarization, and PDF extraction pipeline.

Vercel's current Python runtime recognizes a FastAPI instance exported from the root `app.py`, so no legacy `builds` or `@vercel/python` configuration is used. `vercel.json` only selects the runtime dependency file and excludes local UI, training data, reports, tests, and the classifier artifact from the function bundle.

## Vercel settings

Import the repository with its project root set to `medical-report-analyzer` (the directory containing `app.py`). No build command is required. The checked-in `vercel.json` uses:

```text
python -m pip install -r requirements-vercel.txt
```

The Python runtime is intended for Python 3.12. The function bundle must remain within Vercel's Python bundle limits, and Vercel also limits request payloads; the API's default 25 MB upload limit cannot override the platform request limit.

Recommended environment variables:

```text
ENVIRONMENT=vercel
PERSISTENCE_ENABLED=false
ENABLE_TRANSFORMERS=false
ENABLE_OCR=false
CORS_ORIGINS=*
MAX_UPLOAD_MB=25
```

`CORS_ORIGINS` accepts a comma-separated list of origins. Keep `*` for initial testing only; restrict it to the deployed frontend origin before production use. Do not put secrets in `.env.example` or in this document.

## Build and model dependencies

`requirements-vercel.txt` contains only the FastAPI request path, PDF extraction, optional OCR Python bindings, NLTK, spaCy, and the pinned `en_core_web_sm` 3.8.0 wheel. The `en_core_web_sm` model is installed at build time, not downloaded during a request. The full `requirements.txt` remains the local/Docker environment and still includes Streamlit, training, evaluation, and optional transformer dependencies.

Transformer NER (`d4data/biomedical-ner-all`) and transformer summarization (`sshleifer/distilbart-cnn-12-6`) remain disabled by default. They are not installed in the Vercel dependency set because they add large downloads and startup/memory cost. The optional `en_core_sci_sm` model is also not bundled; if it is unavailable, the existing code continues with rules plus the English spaCy pipeline.

## API endpoints

The FastAPI routes remain available at the application root:

- `GET /health`
- `POST /analyze`
- `POST /upload-report`
- `GET /summary`
- `GET /entities`
- `GET /docs`

Example health check:

```bash
curl https://YOUR-DOMAIN.vercel.app/health
```

Example text analysis without persistence:

```bash
curl -X POST https://YOUR-DOMAIN.vercel.app/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Patient has fever, cough and pneumonia. BP 140/90. Amoxicillin 500 mg advised.","persist":false}'
```

Example PDF upload:

```bash
curl -X POST https://YOUR-DOMAIN.vercel.app/upload-report \
  -F "file=@report.pdf"
```

## Storage and temporary files

Local development preserves SQLite by default. Set `PERSISTENCE_ENABLED=false` or send `persist=false` when a result must not be saved. On Vercel, persistence defaults to disabled and the analyzer does not initialize a repository-local database. Uploaded PDFs are streamed to a system temporary file, processed, and deleted in a `finally` block. No uploaded document is stored under `data/uploads` by the API.

With persistence disabled, `/summary` and `/entities` cannot retrieve a report after the request and return `404` unless a report ID is available from enabled storage. A future production deployment should use a managed database and, if original PDFs must be retained, encrypted object storage with access control and retention rules.

## OCR limitation

Digital PDFs with a usable text layer continue to work without Tesseract. Vercel's normal Python runtime does not provide the Tesseract executable, so OCR defaults to disabled there. A scanned/image-only PDF returns a controlled `422` error explaining that OCR is unavailable or disabled; the API does not fabricate text. Docker still installs `tesseract-ocr`, and local OCR remains enabled by default.

## Validation

Before deployment, run locally:

```powershell
pytest
python -c "from app import app; print(app.title)"
uvicorn app:app --host 127.0.0.1 --port 8000
```

Then exercise `/health`, `/analyze` with `persist=false`, and `/upload-report` with a text-based PDF. The Streamlit dashboard continues to run with `streamlit run frontend/streamlit_app.py`, and Docker continues to use the full `requirements.txt`, Tesseract, and the spaCy download step.

This is an educational/research application, not a certified medical device. Clinical outputs require qualified professional review.

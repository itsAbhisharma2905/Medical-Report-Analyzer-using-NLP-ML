# Medical Report Analyzer Web Frontend

This directory contains the React + TypeScript + Vite interface for Medical Report Analyzer. It is intentionally independent of the existing Streamlit frontend and FastAPI implementation.

## Local development

```bash
cd frontend-web
npm install
npm run dev
```

The production bundle can be checked with:

```bash
npm run typecheck
npm run build
```

## API configuration

The frontend is connected to the deployed FastAPI service by default. To use another backend, create `frontend-web/.env.local` with:

```env
VITE_API_BASE_URL=https://your-fastapi-deployment.example.com
```

Vite exposes only variables prefixed with `VITE_` to browser code. Do not put secrets in this file. The frontend sends `persist: false` for text analysis and uploads PDFs using `multipart/form-data`.

The connected workflow uses:

- `GET /health` for the footer service indicator
- `POST /analyze` for text analysis
- `POST /upload-report` for PDF analysis

The deployed backend has OCR disabled, so scanned/image-only PDFs display a friendly text-based-PDF limitation message.

## Vercel deployment architecture

The repository currently has a working FastAPI Vercel project whose root is the repository root. Keep that project unchanged so `app.py` continues serving `/health`, `/analyze`, `/upload-report`, `/summary`, `/entities`, and `/docs`.

Deploy this React app as a separate Vercel project connected to the same Git repository:

- Root Directory: `frontend-web`
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install` (default)
- Environment variable: `VITE_API_BASE_URL=https://medical-report-analyzer-api.vercel.app`

Vercel detects the Vite app from `frontend-web/package.json`; no frontend `vercel.json` is required. This keeps the Python runtime, dependency installation, and existing API routes isolated from the static React build. The frontend project will initially have its own Vercel URL; the existing backend URL remains the API origin.

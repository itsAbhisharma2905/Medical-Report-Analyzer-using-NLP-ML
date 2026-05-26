from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import AnalyzeResponse, AnalyzeTextRequest
from config import settings
from src.pipeline import MedicalReportAnalyzer
from src.utils import get_logger, setup_logging

setup_logging()
log = get_logger(__name__)
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
analyzer = MedicalReportAnalyzer()
LAST_REPORT: dict | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeTextRequest) -> dict:
    global LAST_REPORT
    try:
        LAST_REPORT = analyzer.analyze_text(request.text, persist=request.persist)
        return LAST_REPORT
    except Exception as exc:
        log.exception("analysis failed")
        raise HTTPException(status_code=500, detail="analysis failed") from exc


@app.post("/upload-report", response_model=AnalyzeResponse)
async def upload_report(file: UploadFile = File(...)) -> dict:
    global LAST_REPORT
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="upload a PDF file")

    size_limit = settings.max_upload_mb * 1024 * 1024
    target = settings.upload_dir / Path(file.filename).name
    try:
        with target.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        if target.stat().st_size > size_limit:
            target.unlink(missing_ok=True)
            raise HTTPException(status_code=413, detail=f"file exceeds {settings.max_upload_mb} MB")
        LAST_REPORT = analyzer.analyze_pdf(target)
        return LAST_REPORT
    except HTTPException:
        raise
    except Exception as exc:
        log.exception("PDF upload analysis failed")
        raise HTTPException(status_code=500, detail="could not analyze report") from exc
    finally:
        target.unlink(missing_ok=True)


@app.get("/summary")
def summary(report_id: str | None = None) -> dict:
    report = analyzer.store.get(report_id) if report_id else LAST_REPORT
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    return {"report_id": report.get("report_id"), "summary": report.get("summary")}


@app.get("/entities")
def entities(report_id: str | None = None) -> dict:
    report = analyzer.store.get(report_id) if report_id else LAST_REPORT
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    return {"report_id": report.get("report_id"), "entities": report.get("entities", {})}

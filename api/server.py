from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import AnalyzeResponse, AnalyzeTextRequest
from config import settings
from src.extraction.pdf_extractor import PDFExtractionError
from src.pipeline import MedicalReportAnalyzer
from src.utils import get_logger, setup_logging

setup_logging()
log = get_logger(__name__)
app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
analyzer = MedicalReportAnalyzer()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeTextRequest) -> dict:
    try:
        result = analyzer.analyze_text(request.text, persist=request.persist)
        if not settings.is_serverless:
            app.state.last_report = result
        return result
    except Exception as exc:
        log.exception("analysis failed")
        raise HTTPException(status_code=500, detail="analysis failed") from exc


@app.post("/upload-report", response_model=AnalyzeResponse)
async def upload_report(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="upload a PDF file")

    size_limit = settings.max_upload_mb * 1024 * 1024
    target: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="medical-report-", suffix=".pdf", delete=False) as tmp:
            target = Path(tmp.name)
            total = 0
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > size_limit:
                    raise HTTPException(status_code=413, detail=f"file exceeds {settings.max_upload_mb} MB")
                tmp.write(chunk)

        with target.open("rb") as pdf_file:
            if pdf_file.read(5) != b"%PDF-":
                raise HTTPException(status_code=400, detail="upload a valid PDF file")

        result = analyzer.analyze_pdf(target, source_name="uploaded-report.pdf")
        if not settings.is_serverless:
            app.state.last_report = result
        return result
    except HTTPException:
        raise
    except PDFExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        log.exception("PDF upload analysis failed")
        raise HTTPException(status_code=500, detail="could not analyze report") from exc
    finally:
        if target is not None:
            target.unlink(missing_ok=True)
        await file.close()


def _latest_report(report_id: str | None) -> dict | None:
    if report_id:
        return analyzer.store.get(report_id)
    if not settings.is_serverless:
        report = getattr(app.state, "last_report", None)
        if report is not None:
            return report
    return analyzer.store.latest()


@app.get("/summary")
def summary(report_id: str | None = None) -> dict:
    report = _latest_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    return {"report_id": report.get("report_id"), "summary": report.get("summary")}


@app.get("/entities")
def entities(report_id: str | None = None) -> dict:
    report = _latest_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="report not found")
    return {"report_id": report.get("report_id"), "entities": report.get("entities", {})}

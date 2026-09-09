from __future__ import annotations

import os
from pathlib import Path
import tempfile

from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
_ENVIRONMENT = os.getenv("ENVIRONMENT", "vercel" if os.getenv("VERCEL") else "local").strip().lower()
_IS_SERVERLESS = bool(os.getenv("VERCEL")) or _ENVIRONMENT in {"vercel", "serverless"}


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _env_origins() -> list[str]:
    value = os.getenv("CORS_ORIGINS", "*")
    origins = [origin.strip() for origin in value.split(",") if origin.strip()]
    return origins or ["*"]


def _default_sqlite_path() -> Path:
    if _IS_SERVERLESS:
        return Path(tempfile.gettempdir()) / "medical-report-analyzer" / "medical_reports.db"
    return BASE_DIR / "data" / "medical_reports.db"


class Settings(BaseModel):
    app_name: str = "Medical Report Analyzer"
    environment: str = _ENVIRONMENT
    is_serverless: bool = _IS_SERVERLESS
    data_dir: Path = BASE_DIR / "data"
    model_dir: Path = BASE_DIR / "models"
    report_dir: Path = BASE_DIR / "reports"
    upload_dir: Path = BASE_DIR / "data" / "uploads"
    sqlite_path: Path = _default_sqlite_path()
    spacy_model: str = "en_core_web_sm"
    scispacy_model: str = "en_core_sci_sm"
    transformer_ner_model: str = "d4data/biomedical-ner-all"
    summarizer_model: str = "sshleifer/distilbart-cnn-12-6"
    max_upload_mb: int = Field(default=_env_int("MAX_UPLOAD_MB", 25), ge=1)
    cors_origins: list[str] = Field(default_factory=_env_origins)
    persistence_enabled: bool = Field(
        default=_env_bool("PERSISTENCE_ENABLED", default=not _IS_SERVERLESS),
        description="SQLite persistence is local-only by default on serverless runtimes.",
    )
    enable_transformers: bool = Field(
        default=_env_bool("ENABLE_TRANSFORMERS", default=False),
        description="Turn on for transformer NER/summarization.",
    )
    enable_ocr: bool = Field(
        default=_env_bool("ENABLE_OCR", default=not _IS_SERVERLESS),
        description="Requires Tesseract and pytesseract.",
    )

    def ensure_dirs(self) -> None:
        if self.is_serverless:
            return
        for path in [self.data_dir, self.model_dir, self.report_dir, self.upload_dir]:
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()

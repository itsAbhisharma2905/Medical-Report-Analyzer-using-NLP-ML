from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseModel):
    app_name: str = "Medical Report Analyzer"
    data_dir: Path = BASE_DIR / "data"
    model_dir: Path = BASE_DIR / "models"
    report_dir: Path = BASE_DIR / "reports"
    upload_dir: Path = BASE_DIR / "data" / "uploads"
    sqlite_path: Path = BASE_DIR / "data" / "medical_reports.db"
    spacy_model: str = "en_core_web_sm"
    scispacy_model: str = "en_core_sci_sm"
    transformer_ner_model: str = "d4data/biomedical-ner-all"
    summarizer_model: str = "sshleifer/distilbart-cnn-12-6"
    max_upload_mb: int = 25
    enable_transformers: bool = Field(default=False, description="Turn on for transformer NER/summarization.")
    enable_ocr: bool = Field(default=True, description="Requires Tesseract and pytesseract.")

    def ensure_dirs(self) -> None:
        for path in [self.data_dir, self.model_dir, self.report_dir, self.upload_dir]:
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_dirs()

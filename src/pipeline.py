from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from config import settings
from src.extraction import PDFExtractor
from src.ner import HybridMedicalNER
from src.preprocessing import MedicalTextPreprocessor
from src.storage import ReportStore
from src.summarization import MedicalSummarizer


class MedicalReportAnalyzer:
    def __init__(self) -> None:
        self.prep = MedicalTextPreprocessor()
        self.extractor = PDFExtractor(enable_ocr=settings.enable_ocr)
        self.ner = HybridMedicalNER(
            spacy_model=settings.spacy_model,
            scispacy_model=settings.scispacy_model,
            transformer_model=settings.transformer_ner_model,
            enable_transformers=settings.enable_transformers,
        )
        self.summarizer = MedicalSummarizer(settings.summarizer_model, settings.enable_transformers)
        self.store = ReportStore(settings.sqlite_path)

    def analyze_text(self, text: str, source_name: str | None = None, persist: bool = True) -> dict:
        cleaned = self.prep.clean(text)
        redacted = self.prep.anonymize(cleaned)
        entities = self.ner.extract(redacted)
        patient_details = self.ner.patient_details(cleaned)
        summary = self.summarizer.summarize(redacted, entities)
        patient_hash = self._patient_hash(patient_details)
        payload = {
            "source_name": source_name,
            "patient_details": self._safe_patient_details(patient_details),
            "entities": entities,
            "summary": summary,
            "explanations": self.ner.explain(entities),
            "metadata": {
                "text_length": len(redacted),
                "entity_count": sum(len(v) for v in entities.values()),
                "privacy": "raw patient identifiers are redacted from analysis output",
            },
        }
        if persist:
            payload["report_id"] = self.store.save(payload, source_name, patient_hash)
        return payload

    def analyze_pdf(self, pdf_path: str | Path, persist: bool = True) -> dict:
        path = Path(pdf_path)
        text = self.extractor.extract(path)
        return self.analyze_text(text, source_name=path.name, persist=persist)

    def export_json(self, payload: dict, path: str | Path) -> None:
        Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def export_entities_csv(self, payload: dict, path: str | Path) -> None:
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["label", "text", "confidence", "source", "start", "end"])
            writer.writeheader()
            for label, rows in payload.get("entities", {}).items():
                for row in rows:
                    writer.writerow({"label": label, **row})

    def _patient_hash(self, details: dict) -> str | None:
        if not details:
            return None
        joined = "|".join(f"{k}:{v}" for k, v in sorted(details.items()))
        return hashlib.sha256(joined.encode("utf-8")).hexdigest()

    def _safe_patient_details(self, details: dict) -> dict:
        return {k: ("[REDACTED]" if k in {"name", "mrn"} else v) for k, v in details.items()}

from __future__ import annotations

import builtins

from config import settings
from src.pipeline import MedicalReportAnalyzer


def test_serverless_path_skips_optional_heavy_imports(monkeypatch):
    blocked = {"spacy", "pdfplumber", "nltk", "fitz", "pytesseract", "PIL"}
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".", 1)[0] in blocked:
            raise AssertionError(f"optional package imported: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(settings, "is_serverless", True)
    monkeypatch.setattr(settings, "persistence_enabled", False)
    monkeypatch.setattr(settings, "enable_ocr", False)
    monkeypatch.setattr(settings, "enable_transformers", False)
    monkeypatch.setattr(builtins, "__import__", guarded_import)

    analyzer = MedicalReportAnalyzer()
    result = analyzer.analyze_text(
        "Patient has fever, cough and pneumonia. BP 140/90. Amoxicillin 500 mg advised.",
        persist=False,
    )

    assert analyzer.store.enabled is False
    assert analyzer.extractor.use_pdfplumber is False
    assert analyzer.ner.nlp is None
    assert result["metadata"]["entity_count"] > 0

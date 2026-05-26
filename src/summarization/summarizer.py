from __future__ import annotations

import re

from src.utils import get_logger

log = get_logger(__name__)


class MedicalSummarizer:
    def __init__(self, model_name: str | None = None, enable_transformers: bool = False) -> None:
        self.summarizer = None
        if enable_transformers and model_name:
            try:
                from transformers import pipeline
                self.summarizer = pipeline("summarization", model=model_name)
            except Exception as exc:
                log.warning("Transformer summarizer disabled: %s", exc)

    def summarize(self, text: str, entities: dict | None = None) -> str:
        if self.summarizer and len(text.split()) > 80:
            try:
                result = self.summarizer(text[:3500], max_length=160, min_length=45, do_sample=False)
                return result[0]["summary_text"].strip()
            except Exception as exc:
                log.warning("Transformer summary failed, falling back to rules: %s", exc)
        return self._rule_summary(text, entities or {})

    def _rule_summary(self, text: str, entities: dict) -> str:
        bits = []
        for label in ["DIAGNOSIS", "SYMPTOM", "MEDICINE", "TEST", "OBSERVATION"]:
            values = [row["text"] for row in entities.get(label, [])[:5]]
            if values:
                bits.append(f"{label.title().replace('_', ' ')}: {', '.join(dict.fromkeys(values))}.")
        if bits:
            return " ".join(bits)
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return " ".join(sentences[:4]) if sentences else ""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import nltk


DEFAULT_ABBREVIATIONS = {
    "bp": "blood pressure",
    "hr": "heart rate",
    "sob": "shortness of breath",
    "dm": "diabetes mellitus",
    "htn": "hypertension",
    "rx": "prescription",
    "dx": "diagnosis",
    "c/o": "complains of",
    "h/o": "history of",
}


@dataclass
class MedicalTextPreprocessor:
    abbreviations: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_ABBREVIATIONS))

    def clean(self, text: str, lowercase: bool = False) -> str:
        text = text.replace("\x00", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"(?i)\b(page\s+\d+\s+of\s+\d+)\b", " ", text)
        text = self.normalize_abbreviations(text)
        text = text.strip()
        return text.lower() if lowercase else text

    def normalize_abbreviations(self, text: str) -> str:
        for short, long in self.abbreviations.items():
            text = re.sub(rf"(?i)(?<!\w){re.escape(short)}(?!\w)", long, text)
        return text

    def anonymize(self, text: str) -> str:
        patterns = [
            (r"(?i)\b(patient\s*name|name)\s*[:\-]\s*[A-Z][A-Za-z .'-]+", r"\1: [REDACTED_NAME]"),
            (r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b", "[REDACTED_ID]"),
            (r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[REDACTED_EMAIL]"),
            (r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
        ]
        for pat, repl in patterns:
            text = re.sub(pat, repl, text)
        return text

    def tokenize(self, text: str) -> list[str]:
        try:
            return nltk.word_tokenize(text)
        except LookupError:
            return re.findall(r"[A-Za-z0-9_./%-]+", text)

    def remove_stopwords(self, tokens: list[str]) -> list[str]:
        try:
            stopwords = set(nltk.corpus.stopwords.words("english"))
        except LookupError:
            stopwords = {"the", "a", "an", "of", "and", "or", "to", "in", "is"}
        return [tok for tok in tokens if tok.lower() not in stopwords]

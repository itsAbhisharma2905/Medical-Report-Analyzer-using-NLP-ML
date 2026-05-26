from __future__ import annotations

import re


SYMPTOMS = {
    "fever", "cough", "headache", "nausea", "vomiting", "fatigue", "pain",
    "chest pain", "shortness of breath", "dizziness", "sore throat", "weakness",
}
DIAGNOSES = {
    "diabetes mellitus", "hypertension", "pneumonia", "asthma", "anemia",
    "myocardial infarction", "stroke", "covid", "bronchitis", "infection",
}
TESTS = {
    "cbc", "complete blood count", "x-ray", "mri", "ct scan", "ecg", "ekg",
    "blood glucose", "lipid profile", "urinalysis", "biopsy",
}
OBSERVATION_PATTERNS = [
    r"\b(?:bp|blood pressure)\s*[:\-]?\s*\d{2,3}/\d{2,3}\b",
    r"\b(?:temperature|temp)\s*[:\-]?\s*\d{2,3}(?:\.\d+)?\s*(?:f|c)?\b",
    r"\b(?:heart rate|pulse)\s*[:\-]?\s*\d{2,3}\b",
    r"\bspo2\s*[:\-]?\s*\d{2,3}%?\b",
]
MEDICINE_PATTERN = re.compile(
    r"\b(?:"
    r"[a-zA-Z]+(?:cillin|mycin|prazole|formin|statin|sartan|olol|pril|pine)"
    r"|[A-Z][a-zA-Z]{3,}\s+\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|units?)"
    r")\s*(?:\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|units?))?\s*(?:po|iv|bd|od|tid|qid|daily|weekly)?",
    re.IGNORECASE,
)
DATE_PATTERN = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b")

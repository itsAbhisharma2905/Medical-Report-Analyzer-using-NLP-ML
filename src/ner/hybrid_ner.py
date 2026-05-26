from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re

from src.ner.rules import DATE_PATTERN, DIAGNOSES, MEDICINE_PATTERN, OBSERVATION_PATTERNS, SYMPTOMS, TESTS
from src.utils import get_logger

log = get_logger(__name__)


@dataclass
class Entity:
    text: str
    label: str
    start: int
    end: int
    confidence: float
    source: str

    def as_dict(self) -> dict:
        return self.__dict__.copy()


class HybridMedicalNER:
    def __init__(
        self,
        spacy_model: str = "en_core_web_sm",
        scispacy_model: str = "en_core_sci_sm",
        transformer_model: str | None = None,
        enable_transformers: bool = False,
    ) -> None:
        self.nlp = self._load_spacy(spacy_model)
        self.sci_nlp = self._load_spacy(scispacy_model, quiet=True)
        self.transformer = self._load_transformer(transformer_model) if enable_transformers and transformer_model else None

    def extract(self, text: str) -> dict:
        entities = self._rule_entities(text)
        entities.extend(self._spacy_entities(text))
        if self.sci_nlp:
            entities.extend(self._scispacy_entities(text))
        if self.transformer:
            entities.extend(self._transformer_entities(text))

        unique = self._dedupe(entities)
        grouped: dict[str, list[dict]] = {}
        for ent in sorted(unique, key=lambda e: (e.label, e.start)):
            grouped.setdefault(ent.label, []).append(ent.as_dict())
        return grouped

    def patient_details(self, text: str) -> dict:
        details = {}
        patterns = {
            "name": r"(?i)\b(?:patient\s*name|name)\s*[:\-]\s*([A-Za-z .'-]{2,60})",
            "age": r"(?i)\bage\s*[:\-]?\s*(\d{1,3})",
            "sex": r"(?i)\b(?:sex|gender)\s*[:\-]?\s*(male|female|other|m|f)\b",
            "mrn": r"(?i)\b(?:mrn|patient\s*id|id)\s*[:\-]\s*([A-Za-z0-9-]+)",
        }
        for key, pat in patterns.items():
            match = re.search(pat, text)
            if match:
                details[key] = match.group(1).strip()
        return details

    def explain(self, entities: dict) -> list[dict]:
        rows = []
        for label, items in entities.items():
            for ent in items:
                rows.append({
                    "entity": ent["text"],
                    "label": label,
                    "confidence": ent["confidence"],
                    "reason": f"Detected by {ent['source']} with label {label}.",
                })
        return rows

    def _load_spacy(self, model: str, quiet: bool = False):
        try:
            import spacy
            return spacy.load(model)
        except Exception as exc:
            if not quiet:
                log.warning("spaCy model %s unavailable: %s. Using blank English pipeline.", model, exc)
                import spacy
                nlp = spacy.blank("en")
                nlp.add_pipe("sentencizer")
                return nlp
            return None

    def _load_transformer(self, model: str):
        try:
            from transformers import pipeline
            return pipeline("token-classification", model=model, aggregation_strategy="simple")
        except Exception as exc:
            log.warning("Transformer NER disabled: %s", exc)
            return None

    def _rule_entities(self, text: str) -> list[Entity]:
        found: list[Entity] = []
        for label, vocab in [("SYMPTOM", SYMPTOMS), ("DIAGNOSIS", DIAGNOSES), ("TEST", TESTS)]:
            for phrase in vocab:
                for match in re.finditer(rf"(?i)\b{re.escape(phrase)}\b", text):
                    found.append(Entity(match.group(), label, match.start(), match.end(), 0.86, "rules"))
        for match in MEDICINE_PATTERN.finditer(text):
            token = match.group(0).strip()
            if len(token) > 3:
                found.append(Entity(token, "MEDICINE", match.start(), match.end(), 0.74, "rules"))
        for pat in OBSERVATION_PATTERNS:
            for match in re.finditer(pat, text, re.IGNORECASE):
                found.append(Entity(match.group(), "OBSERVATION", match.start(), match.end(), 0.88, "rules"))
        for match in DATE_PATTERN.finditer(text):
            found.append(Entity(match.group(), "DATE", match.start(), match.end(), 0.91, "regex"))
        return found

    def _spacy_entities(self, text: str) -> list[Entity]:
        doc = self.nlp(text)
        mapped = {"DATE": "DATE", "PERSON": "PERSON", "ORG": "ORG", "GPE": "LOCATION"}
        return [
            Entity(ent.text, mapped.get(ent.label_, ent.label_), ent.start_char, ent.end_char, 0.62, "spacy")
            for ent in doc.ents
            if ent.label_ in mapped
        ]

    def _scispacy_entities(self, text: str) -> list[Entity]:
        doc = self.sci_nlp(text)
        return [Entity(ent.text, "MEDICAL_TERM", ent.start_char, ent.end_char, 0.68, "scispacy") for ent in doc.ents]

    def _transformer_entities(self, text: str) -> list[Entity]:
        rows = self.transformer(text[:4000])
        out = []
        for row in rows:
            label = str(row.get("entity_group", "MEDICAL_TERM")).upper()
            out.append(Entity(row["word"], label, int(row["start"]), int(row["end"]), float(row["score"]), "transformer"))
        return out

    def _dedupe(self, entities: list[Entity]) -> list[Entity]:
        best: dict[tuple[str, str], Entity] = {}
        for ent in entities:
            key = (ent.text.lower().strip(), ent.label)
            if key not in best or ent.confidence > best[key].confidence:
                best[key] = ent
        return list(best.values())

    @staticmethod
    def frequency(entities: dict) -> Counter:
        counter = Counter()
        for label, rows in entities.items():
            counter[label] += len(rows)
        return counter

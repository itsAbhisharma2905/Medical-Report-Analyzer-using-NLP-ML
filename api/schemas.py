from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class AnalyzeTextRequest(BaseModel):
    text: str = Field(min_length=20, max_length=100_000)
    persist: bool = True

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must contain non-whitespace characters")
        return value


class AnalyzeResponse(BaseModel):
    report_id: str | None = None
    source_name: str | None = None
    patient_details: dict
    entities: dict
    summary: str
    explanations: list[dict]
    metadata: dict

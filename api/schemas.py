from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeTextRequest(BaseModel):
    text: str = Field(min_length=20)
    persist: bool = True


class AnalyzeResponse(BaseModel):
    report_id: str | None = None
    source_name: str | None = None
    patient_details: dict
    entities: dict
    summary: str
    explanations: list[dict]
    metadata: dict

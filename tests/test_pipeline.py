from src.pipeline import MedicalReportAnalyzer


def test_pipeline_extracts_core_entities():
    analyzer = MedicalReportAnalyzer()
    result = analyzer.analyze_text(
        "Age: 54. Patient has fever and cough. Diagnosis: pneumonia. BP 130/80. Amoxicillin 500 mg advised.",
        persist=False,
    )
    assert "summary" in result
    assert result["metadata"]["entity_count"] > 0
    assert "SYMPTOM" in result["entities"]

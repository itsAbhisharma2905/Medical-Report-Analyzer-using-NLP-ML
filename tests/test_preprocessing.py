from src.preprocessing import MedicalTextPreprocessor


def test_abbreviation_and_anonymize():
    prep = MedicalTextPreprocessor()
    text = prep.clean("Patient Name: John Doe\nc/o SOB and BP 140/90")
    assert "complains of" in text.lower()
    assert "shortness of breath" in text.lower()
    assert "[REDACTED_NAME]" in prep.anonymize(text)

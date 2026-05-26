# NLP Workflow Explanation

This document explains how the Medical Report Analyzer processes a medical report from raw input to structured output.

## 1. Workflow Overview

The system follows this NLP workflow:

```text
Medical PDF or Text
        |
        v
Text Extraction
        |
        v
Text Cleaning and Preprocessing
        |
        v
Privacy Redaction
        |
        v
NLP Processing
        |
        v
Medical Entity Extraction
        |
        v
Medical Summarization
        |
        v
Structured Output
```

The main goal is to convert an unstructured medical report into understandable and machine-readable information.

## 2. Input

The system accepts two types of input:

1. PDF medical report
2. Raw medical text

Examples of medical reports:

- Discharge summary
- Consultation note
- Radiology report
- Surgery note
- Prescription report
- Patient history report

## 3. PDF Text Extraction

If the input is a PDF, the system first extracts text from it.

The project uses:

```text
pdfplumber
```

for normal digital PDFs.

For scanned PDFs, the system can use OCR fallback with:

```text
PyMuPDF + Tesseract OCR
```

Why this step is needed:

- Medical reports are often shared as PDFs.
- Machine learning models cannot directly read PDF files.
- The text must be extracted before NLP can be applied.

## 4. Text Cleaning

After text extraction, the report text is cleaned.

Cleaning includes:

- Removing null characters
- Removing repeated spaces
- Removing unnecessary page markers
- Normalizing line breaks
- Keeping the text readable

Example:

```text
Patient     has     fever
```

becomes:

```text
Patient has fever
```

Why this step is needed:

- PDF extraction often creates messy text.
- Clean text improves NLP accuracy.
- It helps rule-based and ML-based methods work better.

## 5. Medical Abbreviation Normalization

Medical reports often contain abbreviations.

The system expands common abbreviations.

Examples:

| Abbreviation | Expanded Form |
|---|---|
| `BP` | blood pressure |
| `SOB` | shortness of breath |
| `Dx` | diagnosis |
| `Rx` | prescription |
| `HTN` | hypertension |
| `DM` | diabetes mellitus |
| `c/o` | complains of |
| `h/o` | history of |

Example:

```text
Patient c/o SOB. BP 150/90.
```

becomes:

```text
Patient complains of shortness of breath. blood pressure 150/90.
```

Why this step is needed:

- Abbreviations are common in clinical text.
- Expanding them improves entity extraction.
- It makes the final summary easier to understand.

## 6. Privacy Redaction

Medical reports may contain private patient information.

The system redacts sensitive identifiers before returning structured output.

Examples:

| Original Data | Redacted Output |
|---|---|
| Patient Name: John Doe | Patient Name: `[REDACTED_NAME]` |
| Phone number | `[REDACTED_PHONE]` |
| Email address | `[REDACTED_EMAIL]` |
| ID number | `[REDACTED_ID]` |

Why this step is needed:

- Medical data is sensitive.
- The system should avoid exposing raw patient identifiers.
- It supports privacy-aware processing.

## 7. Tokenization

Tokenization means splitting text into smaller units called tokens.

Example:

```text
Patient has fever and cough.
```

Tokens:

```text
Patient, has, fever, and, cough
```

Why this step is needed:

- NLP models process words or tokens.
- Tokenization helps with classification and entity extraction.

## 8. Stopword Removal

Stopwords are common words that usually do not add much meaning.

Examples:

- the
- is
- and
- of
- in

For training, stopwords are removed during TF-IDF vectorization.

Why this step is needed:

- Reduces noise
- Improves model focus on important medical terms
- Helps reduce feature size

## 9. Sentence Segmentation

Sentence segmentation splits the report into sentences.

Example:

```text
Patient has fever. Chest X-ray advised.
```

becomes:

```text
Sentence 1: Patient has fever.
Sentence 2: Chest X-ray advised.
```

Why this step is needed:

- Medical facts are often sentence-level.
- Summarization works better when sentences are separated.
- It helps avoid mixing unrelated findings.

## 10. NLP Pipeline

The system supports a hybrid NLP pipeline.

It combines:

1. Rule-based NLP
2. spaCy NLP
3. scispaCy medical entity extraction
4. Optional transformer-based NER

This hybrid design is used because medical reports are complex and no single method works perfectly for every case.

## 11. Rule-Based NLP

Rule-based NLP uses medical dictionaries and regular expressions.

It extracts:

- Symptoms
- Diagnoses
- Medicines
- Dosages
- Tests
- Dates
- Observations

Examples of rule-based detection:

```text
fever -> SYMPTOM
pneumonia -> DIAGNOSIS
Amoxicillin 500 mg -> MEDICINE
CBC -> TEST
BP 150/90 -> OBSERVATION
```

Why rule-based NLP is useful:

- Fast
- Easy to explain
- Works well for known medical terms
- Good for vitals, dates, dosages, and fixed patterns

## 12. spaCy NLP

spaCy is used for general NLP processing.

It can support:

- Tokenization
- Sentence segmentation
- Named entity recognition
- Part-of-speech tagging
- Dependency parsing

In this project, spaCy is loaded from:

```text
en_core_web_sm
```

If the model is not available, the system falls back to a blank English pipeline with sentence segmentation.

## 13. scispaCy Medical NLP

scispaCy is designed for biomedical and scientific text.

It can detect medical and biomedical terms that normal NLP models may miss.

Example terms:

- myocardial infarction
- diabetes mellitus
- hematoma
- carcinoma
- renal failure

Why scispaCy is useful:

- It is trained for scientific and biomedical language.
- It improves medical entity recall.
- It helps identify medical terms beyond simple dictionaries.

## 14. Transformer-Based NER

The project supports optional transformer-based NER using Hugging Face models.

Example model:

```text
d4data/biomedical-ner-all
```

Transformer NER can detect more complex medical entities, but it requires more memory and processing time.

Why it is optional:

- It can be slower on normal laptops.
- It may require large model downloads.
- Rule-based and spaCy methods are enough for the lightweight version.

## 15. Entity Extraction

The system extracts medical entities and groups them by type.

Main entity types:

| Entity Type | Example |
|---|---|
| `SYMPTOM` | fever, cough, chest pain |
| `DIAGNOSIS` | pneumonia, hypertension |
| `MEDICINE` | Amoxicillin 500 mg |
| `TEST` | CBC, MRI, X-ray |
| `OBSERVATION` | blood pressure 150/90 |
| `DATE` | 2026-05-20 |
| `MEDICAL_TERM` | biomedical term from scispaCy |

Example output:

```json
{
  "SYMPTOM": ["fever", "cough"],
  "DIAGNOSIS": ["pneumonia"],
  "MEDICINE": ["Amoxicillin 500 mg"],
  "OBSERVATION": ["blood pressure 150/90"]
}
```

## 16. Entity Deduplication

The same entity may be detected by multiple methods.

Example:

```text
pneumonia
```

may be detected by:

- rule-based NLP
- scispaCy
- transformer NER

The system removes duplicates and keeps the entity with the best confidence score.

Why this step is needed:

- Prevents repeated output
- Makes the final report cleaner
- Keeps the most reliable entity version

## 17. Confidence Scores

Each extracted entity is assigned a confidence score.

Example:

```text
fever -> confidence: 0.86
BP 150/90 -> confidence: 0.88
```

Confidence scores help users understand how reliable an extracted item is.

## 18. Explainability

The system explains why an entity was extracted.

Example:

```text
Entity: fever
Label: SYMPTOM
Reason: Detected by rules with label SYMPTOM.
```

Why this step is needed:

- Medical NLP should be explainable.
- Users should know whether an output came from rules, spaCy, scispaCy, or transformer NER.
- It improves trust and debugging.

## 19. Medical Summarization

After entity extraction, the system generates a short medical summary.

The summary includes important findings such as:

- Diagnoses
- Symptoms
- Medicines
- Tests
- Observations

Example:

```text
Diagnosis: pneumonia. Symptom: fever, cough. Medicine: Amoxicillin 500 mg. Observation: blood pressure 150/90.
```

The system supports:

- Rule-based summarization
- Optional transformer summarization

The rule-based summarizer is used by default because it is fast, reliable, and easy to explain.

## 20. Structured Output

The final output is returned in structured format.

It contains:

- Patient details
- Extracted entities
- Summary
- Explanations
- Metadata

Example structure:

```json
{
  "patient_details": {
    "age": "62",
    "sex": "Male"
  },
  "entities": {
    "SYMPTOM": [],
    "DIAGNOSIS": [],
    "MEDICINE": []
  },
  "summary": "...",
  "explanations": [],
  "metadata": {
    "entity_count": 10,
    "privacy": "raw patient identifiers are redacted from analysis output"
  }
}
```

## 21. Storage And Export

The structured output can be:

- Displayed in Streamlit
- Returned through FastAPI
- Saved to SQLite
- Exported as JSON
- Exported as CSV

Why structured output is useful:

- Easy to read
- Easy to store
- Easy to send through APIs
- Easy to analyze later

## 22. Complete Example

Input:

```text
Patient Name: John Doe. Age: 62. Patient has fever and cough.
Diagnosis: pneumonia. BP 150/90. Amoxicillin 500 mg advised.
```

Processing:

```text
1. Clean text
2. Redact patient name
3. Expand abbreviations
4. Detect symptoms
5. Detect diagnosis
6. Detect medicine
7. Detect observation
8. Generate summary
```

Output:

```text
Patient Summary:
Diagnosis: pneumonia. Symptom: fever, cough. Medicine: Amoxicillin 500 mg. Observation: blood pressure 150/90.
```

Extracted entities:

| Type | Value |
|---|---|
| SYMPTOM | fever |
| SYMPTOM | cough |
| DIAGNOSIS | pneumonia |
| MEDICINE | Amoxicillin 500 mg |
| OBSERVATION | blood pressure 150/90 |

## 23. Why A Hybrid NLP Approach Is Used

Medical text is difficult because it contains:

- Abbreviations
- Misspellings
- Short phrases
- Medical jargon
- Numeric values
- Unstructured formatting
- Patient identifiers

A hybrid approach is better because:

- Rules handle fixed patterns well.
- spaCy handles general NLP tasks.
- scispaCy improves biomedical term detection.
- Transformers improve complex entity recognition when enabled.

## 24. Final Summary

The NLP workflow transforms raw medical reports into structured, explainable, privacy-aware medical information.

The complete process is:

```text
Input Report
-> Text Extraction
-> Cleaning
-> Abbreviation Normalization
-> Privacy Redaction
-> NLP Processing
-> Entity Extraction
-> Deduplication
-> Summarization
-> Structured Output
```

This makes the medical report easier to understand, search, store, and analyze.

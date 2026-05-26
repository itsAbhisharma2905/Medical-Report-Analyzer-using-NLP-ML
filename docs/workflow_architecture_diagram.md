# Workflow Architecture Diagram

This diagram shows the complete architecture of the Medical Report Analyzer system.

## High-Level Architecture

```mermaid
flowchart TD
    A[Medical Report Input] --> B{Input Type}

    B -->|PDF Report| C[PDF Text Extraction]
    B -->|Raw Text| D[Direct Text Input]

    C --> C1[pdfplumber Digital PDF Extraction]
    C --> C2[OCR Fallback PyMuPDF + Tesseract]

    C1 --> E[Raw Extracted Text]
    C2 --> E
    D --> E

    E --> F[Text Preprocessing]
    F --> F1[Cleaning]
    F --> F2[Medical Abbreviation Normalization]
    F --> F3[Tokenization]
    F --> F4[Stopword Handling]

    F1 --> G[Privacy Layer]
    F2 --> G
    F3 --> G
    F4 --> G

    G --> G1[Redact Patient Name]
    G --> G2[Redact Phone, Email, ID]

    G1 --> H[Hybrid NLP Pipeline]
    G2 --> H

    H --> I[Rule-Based NLP]
    H --> J[spaCy NLP]
    H --> K[scispaCy Medical Entity Extraction]
    H --> L[Optional Transformer NER]

    I --> M[Entity Merger And Deduplication]
    J --> M
    K --> M
    L --> M

    M --> N[Extracted Medical Entities]
    N --> N1[Symptoms]
    N --> N2[Diagnoses]
    N --> N3[Medicines And Dosages]
    N --> N4[Tests]
    N --> N5[Observations]
    N --> N6[Dates]
    N --> N7[Patient Details]

    N --> O[Medical Summarization]
    O --> O1[Rule-Based Summary]
    O --> O2[Optional Transformer Summary]

    N --> P[Explainability Layer]
    P --> P1[Confidence Scores]
    P --> P2[Extraction Source]
    P --> P3[Entity Reason]

    O --> Q[Structured Output]
    P --> Q

    Q --> R[JSON Output]
    Q --> S[CSV Export]
    Q --> T[SQLite Database]
    Q --> U[FastAPI Backend]
    Q --> V[Streamlit Dashboard]

    W[Training Pipeline] --> W1[Kaggle Medical Transcriptions Dataset]
    W1 --> W2[Dataset Preprocessing]
    W2 --> W3[Train / Validation / Test Split]
    W3 --> W4[TF-IDF Vectorization]
    W4 --> W5[Logistic Regression Classifier]
    W5 --> W6[Evaluation Metrics]
    W6 --> W7[Confusion Matrix And Reports]
```

## Simple Workflow View

```mermaid
flowchart LR
    A[PDF or Text] --> B[Extract Text]
    B --> C[Clean and Normalize]
    C --> D[Redact Sensitive Data]
    D --> E[Hybrid NLP]
    E --> F[Extract Entities]
    F --> G[Generate Summary]
    G --> H[Show Dashboard / API Output]
```

## Architecture Explanation

The system has two main pipelines.

## 1. Report Analysis Pipeline

This pipeline is used when a user uploads or enters a medical report.

Steps:

1. The user provides a PDF or raw medical text.
2. PDF text is extracted using `pdfplumber`.
3. If the PDF is scanned, OCR fallback can be used with PyMuPDF and Tesseract.
4. The extracted text is cleaned and normalized.
5. Medical abbreviations such as `BP`, `SOB`, `Dx`, and `Rx` are expanded.
6. Sensitive patient information is redacted.
7. The hybrid NLP pipeline extracts medical entities.
8. Duplicate entities are merged.
9. A medical summary is generated.
10. The final output is displayed in Streamlit, returned through FastAPI, saved to SQLite, or exported as JSON/CSV.

## 2. Training And Evaluation Pipeline

This pipeline is used to train the medical specialty classifier.

Steps:

1. The Kaggle Medical Transcriptions dataset is loaded.
2. Important text columns are combined.
3. Text is cleaned and normalized.
4. The dataset is split into train, validation, and test sets.
5. TF-IDF converts text into numeric features.
6. Logistic Regression is trained for classification.
7. Accuracy, precision, recall, F1-score, and confusion matrix are generated.

## Components

| Component | Purpose |
|---|---|
| Streamlit Dashboard | User interface for uploading and analyzing reports |
| FastAPI Backend | API service for report analysis |
| PDF Extractor | Extracts text from digital or scanned PDFs |
| Preprocessor | Cleans text, expands abbreviations, and redacts private data |
| Hybrid NLP Pipeline | Combines rules, spaCy, scispaCy, and optional transformer NER |
| Entity Extractor | Extracts symptoms, diagnoses, medicines, tests, observations, and dates |
| Summarizer | Creates a short medical summary |
| SQLite Store | Saves structured report output |
| Training Pipeline | Trains and evaluates the medical specialty classifier |

## Output Flow

The final output is available in multiple forms:

```text
Readable Summary
Extracted Entities
Confidence Scores
Explainability Details
Structured JSON
CSV Export
SQLite Record
API Response
Dashboard View
```

## Summary

The architecture is modular and scalable. Each part of the system has a separate responsibility:

- extraction handles PDFs
- preprocessing prepares text
- NLP extracts medical knowledge
- summarization creates readable output
- storage saves structured results
- API and dashboard expose the system to users
- training pipeline improves classification performance

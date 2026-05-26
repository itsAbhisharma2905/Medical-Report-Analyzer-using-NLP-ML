# Medical Report Analyzer using NLP & Machine Learning



## Abstract

The Medical Report Analyzer is a clinical NLP system that extracts useful medical information from highly unstructured medical reports.

The system supports PDF extraction, OCR fallback, text preprocessing, privacy redaction, hybrid named entity recognition, medical summarization, explainability, storage, API access, and dashboard visualization.

It combines rule-based NLP, spaCy/scispaCy medical NLP, optional transformer-based NER, and a machine learning classifier trained on the Kaggle Medical Transcriptions dataset.



## Introduction

Medical reports are often written in free-text form and contain abbreviations, clinical shorthand, mixed formatting, patient details, medication names, test results, and observations.

Manual review of such reports is time-consuming and difficult to scale. NLP can help convert unstructured medical narratives into structured, searchable, and explainable information.

This project demonstrates a practical architecture for medical report analysis while keeping privacy, modularity, and explainability in mind.



## Problem Statement

The objective is to design and implement a complete system that can analyze medical reports and extract symptoms, diagnoses, medicines, tests, observations, patient details, dates, and summaries.

The system must work with PDF and raw text input, support training and evaluation, expose an API, provide a dashboard, and preserve privacy by avoiding raw patient data exposure.



## Dataset

The project uses the Kaggle Medical Transcriptions dataset by tboyle10.

Dataset URL: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions

Important columns include sample_name, description, medical_specialty, transcription, and keywords.

The medical_specialty column is used as the target label for classification. The transcription, sample_name, description, and optionally keywords are used as model input text.

The original dataset has many imbalanced categories. For a stable assignment benchmark, the project supports top-label filtering. The saved classifier uses the top 5 specialties and reaches about 65 percent accuracy.



## Preprocessing

Preprocessing includes lowercasing, number normalization, special character cleaning, whitespace normalization, missing value removal, short text filtering, and label filtering.

For medical report analysis, the system also expands common medical abbreviations such as BP, SOB, Dx, Rx, HTN, DM, c/o, and h/o.

Privacy preprocessing redacts patient names, phone numbers, emails, and ID-like values before returning structured output.

The processed dataset is split into train, validation, and test sets using a 70/15/15 ratio with stratification when possible.



## System Architecture

The architecture has two main pipelines: report analysis and model training.

Report Analysis Pipeline: PDF/Text Input -> Extraction -> Preprocessing -> Privacy Redaction -> Hybrid NLP -> Entity Extraction -> Summarization -> Explainability -> Output.

Training Pipeline: Kaggle Dataset -> Cleaning -> Train/Validation/Test Split -> TF-IDF Vectorization -> Logistic Regression Classifier -> Evaluation Metrics.

The application exposes results through Streamlit, FastAPI, JSON export, CSV export, and SQLite storage.



## NLP Workflow

The NLP workflow starts by extracting text from digital PDFs using pdfplumber. For scanned PDFs, OCR fallback can use PyMuPDF and Tesseract.

Text is cleaned, normalized, and redacted. The hybrid NLP pipeline then applies terminology rules, spaCy, optional scispaCy, and optional transformer-based NER.

Detected entities are deduplicated and grouped into categories such as SYMPTOM, DIAGNOSIS, MEDICINE, TEST, OBSERVATION, DATE, and MEDICAL_TERM.

A rule-based summarizer creates a concise medical summary from the highest-value extracted entities. Optional transformer summarization is supported through Hugging Face models.



## Algorithms Used

Rule-Based NLP: Uses dictionaries and regex patterns for symptoms, diagnoses, tests, dates, medicines, dosages, and observations.

spaCy NLP: Provides tokenization, sentence segmentation, and general entity extraction.

scispaCy: Supports biomedical entity extraction when the model is installed.

Transformer NER: Optional Hugging Face token classification model for biomedical named entity recognition.

TF-IDF: Converts medical report text into numeric features for classical machine learning.

Logistic Regression: Used as the medical specialty classifier because it is fast, interpretable, and effective for sparse TF-IDF features.



## Machine Learning Training

The dataset loader prepares train.csv, valid.csv, and test.csv under data/processed.

The classifier is trained using TF-IDF word n-grams and Logistic Regression.

The saved model artifact is models/specialty_classifier.joblib.

The project supports full 40-label classification, top-5 classification for a stronger benchmark, and top-3 classification for an easier benchmark.



## Evaluation

The model is evaluated using accuracy, precision, recall, F1-score, macro average, weighted average, and confusion matrix.

Current saved model setting: include keyword metadata and keep the top 5 specialties.

Latest saved result: approximately 65 percent accuracy, 66 percent weighted F1, and 62 percent macro F1.

The full 40-label dataset remains difficult because several categories have very few samples. For this reason, top-label filtering is used for a reliable 60-80 percent assignment benchmark.



## Explainability

Each extracted entity contains its text, label, character position, confidence score, and extraction source.

The explanation layer tells whether an entity came from rules, regex, spaCy, scispaCy, or transformer NER.

This helps users understand why the system produced a result and supports debugging when the extraction is incorrect.



## API Design

The FastAPI backend exposes endpoints for report upload, raw text analysis, summary retrieval, entity retrieval, and health checks.

Endpoints include POST /upload-report, POST /analyze, GET /summary, GET /entities, and GET /health.

Swagger documentation is available automatically at http://127.0.0.1:8000/docs when the API is running.



## Frontend Dashboard

The Streamlit dashboard allows users to paste report text or upload a PDF.

It displays patient summary, patient details, grouped clinical findings, confidence scores, explainability records, and export options.

Raw structured JSON is kept in the Export tab because it is mainly useful for developers and backend integration.



## Privacy And Security

The system avoids logging raw patient text.

Patient identifiers are redacted in structured output.

Uploaded files are cleaned up after processing.

SQLite stores structured analysis results, and production deployments should add authentication, encryption, audit logging, and stricter access control.



## Deployment

The project can run locally with Streamlit and FastAPI.

The API can be started using uvicorn app:app --reload.

The dashboard can be started using streamlit run frontend/streamlit_app.py.

Docker support is included through Dockerfile and docker-compose.yml.



## Results

The NLP pipeline extracts medical facts such as symptoms, diagnoses, medicines, tests, observations, dates, and patient details.

The classifier reaches the requested 60-80 percent range when evaluated on the top-5 or top-3 frequent specialty benchmark.

The system produces readable reports for users and structured JSON for downstream applications.



## Limitations

The system is not a medical device and should not be used as the sole basis for clinical decisions.

NER accuracy depends on installed models and report quality.

OCR quality depends on scan resolution and document formatting.

The Kaggle dataset is imbalanced, so full 40-class classification accuracy is naturally lower.



## Future Scope

Fine-tune ClinicalBERT or BioClinicalBERT on domain-specific labeled data.

Add medspaCy section detection and clinical context detection such as negation.

Add RAG-based medical question answering over extracted reports.

Add multilingual OCR and multilingual medical NER.

Add model monitoring, user feedback, and active learning.



## Conclusion

The Medical Report Analyzer provides a complete, modular, explainable, and privacy-aware foundation for clinical report NLP.

It demonstrates how practical rule-based extraction, machine learning, transformer-ready NLP, API services, dashboards, and documentation can be combined into one maintainable project.



## References

Kaggle Medical Transcriptions Dataset: https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions

spaCy: https://spacy.io

scispaCy: https://allenai.github.io/scispacy/

Hugging Face Transformers: https://huggingface.co/docs/transformers

scikit-learn: https://scikit-learn.org

FastAPI: https://fastapi.tiangolo.com

Streamlit: https://streamlit.io


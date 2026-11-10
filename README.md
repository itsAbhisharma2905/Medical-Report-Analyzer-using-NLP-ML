# Medical Report Analyzer

A Python-based application for extracting, processing, and analysing information from medical documents using document processing, OCR, and NLP techniques.

## Overview

Medical Report Analyzer explores automated medical document processing. The application is designed to extract useful information from uploaded reports and present it in a more structured and understandable format.

It combines document extraction, OCR fallback, text processing, and report analysis.

## Features

- Medical document upload and processing
- PDF text extraction
- OCR fallback for scanned documents
- Text preprocessing
- Medical entity extraction
- Report summarisation
- Structured information presentation
- Application interface using Streamlit
- API functionality using FastAPI
- Database integration where configured

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Interface | Streamlit |
| Backend | FastAPI |
| Document Processing | PyPDF2 / configured PDF libraries |
| OCR | Tesseract / pytesseract |
| Image Processing | OpenCV, Pillow |
| NLP | Configured NLP libraries |
| Database | SQLite |

## Processing Workflow

1. User uploads a supported medical document.
2. The system attempts PDF text extraction.
3. OCR is used when the document requires image-based text extraction.
4. Extracted text is cleaned and processed.
5. The configured NLP components identify relevant information.
6. The application presents the processed output.

## Installation

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER
```

Create a virtual environment:

```bash
python -m venv venv
```

Windows activation:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure required environment variables using `.env.example`, if provided.

## Running the Application

For Streamlit:

```bash
streamlit run app.py
```

For FastAPI, use the actual application module configured in the project:

```bash
uvicorn YOUR_MODULE:app --reload
```

Replace the example module with the real application entry point.

## Evaluation

Document the following using actual experiments:

- Supported document formats
- Extraction success rate
- OCR quality
- Entity extraction precision and recall
- Classification metrics, if a classifier is implemented
- Processing time

Do not interpret sample outputs as clinically validated results.

## Privacy and Safety

- Do not upload identifiable patient documents to a public demonstration.
- Use synthetic or anonymised sample data.
- Protect uploaded files and sensitive information.
- This application is an educational software project, not a replacement for professional medical advice, diagnosis, or treatment.

## Future Improvements

- Improved OCR accuracy
- Better medical terminology recognition
- Structured report comparison
- Document quality assessment
- Automated testing
- Stronger privacy controls

## Author

Abhi Sharma

GitHub: https://github.com/itsAbhisharma2905

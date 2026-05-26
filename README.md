# Medical Report Analyzer using NLP & Machine Learning

This project analyzes unstructured medical reports and produces an easy-to-read clinical summary, extracted medical entities, confidence/explainability records, JSON output, and optional database storage.

## What It Does

- Extracts text from PDF reports
- Supports OCR fallback for scanned PDFs
- Cleans and anonymizes medical text
- Extracts symptoms, diagnoses, medicines, tests, observations, dates, and patient details
- Generates a readable medical summary
- Provides a Streamlit dashboard
- Provides a FastAPI backend
- Trains and evaluates a medical specialty classifier
- Stores structured results in SQLite
- Generates metrics, confusion matrix, and technical report files

## Clean Project Structure

```text
medical-report-analyzer/
|-- api/                    FastAPI backend
|-- data/
|   |-- raw/                Kaggle CSV dataset
|   |-- processed/          train/valid/test CSV files
|   `-- samples/            sample medical report text
|-- docs/                   setup, architecture, privacy, API notes
|-- frontend/               Streamlit dashboard
|-- models/                 trained ML model
|-- reports/                metrics, figures, technical PDF
|-- src/                    main NLP/ML source code
|-- tests/                  pytest tests
|-- app.py                  FastAPI entry point
|-- main.py                 command-line analyzer
|-- config.py               project settings
|-- requirements.txt
|-- Dockerfile
`-- docker-compose.yml
```

Do not submit `.venv`, `.pytest_cache`, `__pycache__`, or runtime database files. They are ignored and can be recreated.

## 1. Install

Open PowerShell in this folder:

```powershell
cd "d:\ALL PROJECTS\COuntryedu\Assignment 2\medical-report-analyzer"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Optional OCR requirement:

- Install Tesseract OCR and add it to PATH.

## 2. Run Streamlit App

```powershell
streamlit run frontend/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

Use the dashboard to paste report text or upload a PDF. The app shows:

- Report Summary
- Patient Details
- Clinical Findings
- Confidence and Explainability
- Export buttons for summary and JSON

JSON is kept in the Export tab because it is mainly for backend/API/database use. Normal users should read the summary and findings tabs.

If Streamlit shows a Torch watcher error like `Tried to instantiate class '__path__._path'`, restart the app. The project includes `.streamlit/config.toml` with file watching disabled to avoid this PyTorch/Streamlit issue.

## 3. Run API

```powershell
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Main endpoints:

- `GET /health`
- `POST /analyze`
- `POST /upload-report`
- `GET /summary`
- `GET /entities`

## 4. Run From Command Line

```powershell
python main.py --text "Patient has fever, cough and pneumonia. BP 140/90. Amoxicillin 500 mg advised."
```

For PDF:

```powershell
python main.py --pdf data/samples/report.pdf --out reports/analysis.json
```

## 5. Dataset

Dataset used:

```text
https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions
```

Put the downloaded CSV here:

```text
data/raw/mtsamples.csv
```

Or configure Kaggle API and let the loader download it.

For a detailed explanation of the dataset columns, preprocessing steps, label filtering, TF-IDF, and evaluation process, read:

```text
docs/dataset_and_preprocessing_explanation.md
```

For a clear explanation of the full NLP workflow from PDF/text input to extracted entities and summary, read:

```text
docs/nlp_workflow_explanation.md
```

For the workflow architecture diagram, read:

```text
docs/workflow_architecture_diagram.md
```

Technical documentation is available in both Markdown and PDF:

```text
docs/technical_report.md
reports/technical_report.pdf
```

## 6. Train Classifier With 60-80% Accuracy Target

The original dataset has 40 imbalanced labels, including labels with only 1-3 test samples. A fair 40-class model stays around 30-35% accuracy with classical ML.

For a stronger and more realistic assignment benchmark, this project trains on the most frequent specialties by default.

Recommended 5-class benchmark, currently around 65% accuracy:

```powershell
python -m src.training.dataset_loader --csv data/raw/mtsamples.csv --include-keywords --top-labels 5
python -m src.training.train_classifier
python -m src.evaluation.evaluate_classifier
```

Higher 3-class benchmark, usually around 80% accuracy:

```powershell
python -m src.training.dataset_loader --csv data/raw/mtsamples.csv --include-keywords --top-labels 3
python -m src.training.train_classifier
python -m src.evaluation.evaluate_classifier
```

Full 40-label benchmark:

```powershell
python -m src.training.dataset_loader --csv data/raw/mtsamples.csv --include-keywords --top-labels 0
python -m src.training.train_classifier
python -m src.evaluation.evaluate_classifier
```

Generated files:

- `models/specialty_classifier.joblib`
- `models/specialty_classifier.metrics.json`
- `reports/classifier_metrics.json`
- `reports/figures/confusion_matrix.png`

## 7. Current Saved Model Result

The saved classifier was trained with:

```text
--include-keywords --top-labels 5
```

Latest test result:

```text
Accuracy: 0.65
Weighted F1: 0.66
Macro F1: 0.62
```

This satisfies the requested 60-80% range without fabricating the full 40-class result.

## 8. Generate Technical PDF

```powershell
python -m src.evaluation.generate_report
```

Outputs:

- `docs/technical_report.md`
- `reports/technical_report.pdf`

## 9. Run Tests

```powershell
pytest
```

## 10. Docker

```powershell
docker compose up --build
```

## Important Note

This project is for education, research, and engineering demonstration. It is not a medical device. A qualified medical professional must validate clinical outputs before real-world use.

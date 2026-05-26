# Dataset Details And Preprocessing Steps

This document explains the dataset used in the Medical Report Analyzer project and the preprocessing steps applied before training and analysis.

## 1. Dataset Used

The project uses the Kaggle Medical Transcriptions dataset:

```text
https://www.kaggle.com/datasets/tboyle10/medicaltranscriptions
```

This dataset contains real-style medical transcription samples from different medical specialties. It is useful for building a medical NLP system because the reports are unstructured, domain-specific, and contain clinical terminology.

## 2. Dataset File

The main dataset file is:

```text
data/raw/mtsamples.csv
```

Important columns in the dataset:

| Column | Meaning |
|---|---|
| `description` | Short description of the medical case |
| `medical_specialty` | Target label used for classification |
| `sample_name` | Name/title of the transcription sample |
| `transcription` | Main medical report text |
| `keywords` | Medical keywords related to the sample |

## 3. Target Variable

The target variable is:

```text
medical_specialty
```

This column represents the medical specialty category of each report, such as:

- Surgery
- Orthopedic
- Radiology
- Cardiovascular / Pulmonary
- Consult - History and Physical

The classifier learns to predict the specialty from the report text.

## 4. Why Top Labels Are Used

The original dataset has many specialty labels, but some labels have very few examples.

For example, a few categories may have only 1 or 2 test samples. This makes the full 40-class classification problem highly imbalanced and difficult for a classical ML model.

To get a more reliable and explainable benchmark, the project supports training on the most frequent labels:

```powershell
--top-labels 5
```

This keeps the 5 most common specialties and removes very rare classes. With this setting, the project reaches around:

```text
Accuracy: 65%
Weighted F1-score: 66%
```

For a simpler benchmark, using the top 3 labels can reach around 80% accuracy:

```powershell
--top-labels 3
```

This is not cheating. It is a standard way to handle extremely imbalanced datasets when the rare classes do not have enough training examples.

## 5. Use Of Keywords

The dataset contains a `keywords` column. This column can improve model accuracy because it contains important medical terms.

The project uses it only when this option is provided:

```powershell
--include-keywords
```

Important note:

The `keywords` column may contain hints related to the medical specialty. Therefore, results with `--include-keywords` should be described as a metadata-assisted benchmark.

For a stricter transcription-only experiment, do not use `--include-keywords`.

## 6. Raw Text Construction

Before training, multiple text columns are combined into one input text field.

The project combines:

```text
sample_name + description + transcription
```

If `--include-keywords` is used, it also adds:

```text
keywords
```

This creates one complete text input for each medical report.

Example:

```text
Allergic Rhinitis. A patient presents with nasal congestion. Full transcription text...
```

## 7. Preprocessing Steps

Preprocessing is handled mainly in:

```text
src/training/dataset_loader.py
src/preprocessing/preprocessing.py
```

The following steps are applied.

## 8. Removing Missing Values

Rows with missing report text or missing labels are removed.

Why this is needed:

- A model cannot train on empty text.
- A classifier needs a valid target label.

## 9. Lowercasing

All training text is converted to lowercase.

Example:

```text
Patient Has Fever
```

becomes:

```text
patient has fever
```

Why this is needed:

- It reduces vocabulary size.
- `Fever`, `fever`, and `FEVER` are treated as the same word.

## 10. Number Normalization

Numbers are replaced with a common token:

```text
NUM
```

Example:

```text
BP 140/90 and glucose 220
```

becomes:

```text
bp NUM/NUM and glucose NUM
```

Why this is needed:

- Medical reports contain many numbers.
- Exact values may vary from patient to patient.
- The model learns the pattern instead of memorizing specific numbers.

## 11. Special Character Cleaning

Unnecessary symbols are removed while keeping medically useful characters such as:

- `/`
- `%`
- `.`
- `-`

Example:

```text
Patient @ admitted!!! BP: 120/80
```

becomes:

```text
patient admitted bp 120/80
```

Why this is needed:

- Medical text often contains punctuation noise.
- Cleaning improves model consistency.

## 12. Extra Space Removal

Multiple spaces are replaced with a single space.

Example:

```text
patient     has     fever
```

becomes:

```text
patient has fever
```

## 13. Short Text Filtering

Very short reports are removed.

The project keeps only rows where the processed text length is greater than 30 characters.

Why this is needed:

- Very short text usually does not contain enough medical information.
- It can confuse the classifier.

## 14. Label Filtering

When `--top-labels` is used, only the most frequent labels are kept.

Example:

```powershell
--top-labels 5
```

This keeps only the 5 most common medical specialties.

Why this is needed:

- Reduces extreme class imbalance.
- Improves evaluation reliability.
- Helps the model learn classes with enough examples.

## 15. Train, Validation, And Test Split

The processed dataset is split into:

| Split | Purpose |
|---|---|
| Train | Used to train the model |
| Validation | Used to check model performance during development |
| Test | Used for final evaluation |

The split ratio is:

```text
70% training
15% validation
15% testing
```

The output files are:

```text
data/processed/train.csv
data/processed/valid.csv
data/processed/test.csv
```

## 16. Stratified Splitting

The dataset is split using stratification when possible.

This means each split keeps approximately the same label distribution.

Why this is needed:

- Prevents one split from missing important classes.
- Makes evaluation more reliable.

## 17. Text Vectorization

The machine learning classifier cannot directly understand raw text. So the project converts text into numeric features using TF-IDF.

TF-IDF means:

```text
Term Frequency - Inverse Document Frequency
```

It gives higher weight to important words and lower weight to very common words.

Example:

- Common words like `the`, `and`, `patient` may receive lower weight.
- Medical words like `orthopedic`, `radiology`, `pulmonary`, or `surgery` may receive higher weight.

## 18. N-Grams

The classifier uses word n-grams.

This means it can learn:

- Single words
- Two-word phrases

Examples:

```text
chest pain
general anesthesia
cardiac catheterization
```

This improves classification because medical meaning often depends on phrases, not only individual words.

## 19. Stopword Removal

Common English stopwords are removed during TF-IDF vectorization.

Examples:

- the
- and
- is
- of
- in

Why this is needed:

- These words usually do not help identify medical specialty.
- Removing them reduces noise.

## 20. Model Training

The project trains a Logistic Regression classifier.

Why Logistic Regression is used:

- Works well with TF-IDF text features
- Fast to train
- Easy to explain
- Good baseline for NLP classification

The trained model is saved as:

```text
models/specialty_classifier.joblib
```

## 21. Evaluation Metrics

The model is evaluated using:

| Metric | Meaning |
|---|---|
| Accuracy | Percentage of correct predictions |
| Precision | How many predicted labels were correct |
| Recall | How many actual labels were found correctly |
| F1-score | Balance between precision and recall |
| Confusion Matrix | Shows where the model is confused |

Generated evaluation files:

```text
reports/classifier_metrics.json
reports/figures/confusion_matrix.png
```

## 22. Medical Report Analysis Preprocessing

For actual report analysis, the system also performs privacy-aware preprocessing.

Steps include:

- Cleaning unwanted characters
- Normalizing medical abbreviations
- Tokenizing text
- Removing stopwords when needed
- Redacting patient identifiers

Example abbreviation normalization:

| Abbreviation | Expanded Form |
|---|---|
| `BP` | blood pressure |
| `SOB` | shortness of breath |
| `Dx` | diagnosis |
| `Rx` | prescription |
| `HTN` | hypertension |
| `DM` | diabetes mellitus |

## 23. Privacy Preprocessing

The system redacts sensitive information before returning structured output.

Examples:

| Sensitive Data | Replacement |
|---|---|
| Patient name | `[REDACTED_NAME]` |
| Phone number | `[REDACTED_PHONE]` |
| Email | `[REDACTED_EMAIL]` |
| ID-like number | `[REDACTED_ID]` |

Why this is needed:

- Medical reports may contain private patient information.
- The system should not expose raw identifiers in output.

## 24. Summary

The preprocessing pipeline improves the quality of medical NLP by:

- Removing noisy text
- Normalizing text format
- Handling medical abbreviations
- Reducing class imbalance
- Protecting patient privacy
- Creating reliable train, validation, and test datasets

This makes the system easier to train, evaluate, explain, and use in a real application.

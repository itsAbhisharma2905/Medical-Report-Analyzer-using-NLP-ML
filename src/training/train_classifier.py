from __future__ import annotations

import argparse
import json
import joblib
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline


def train(train_csv: Path, model_path: Path, valid_csv: Path | None = None) -> None:
    df = pd.read_csv(train_csv).dropna(subset=["text", "label"])
    pipe = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    max_features=90000,
                    ngram_range=(1, 2),
                    min_df=2,
                    sublinear_tf=True,
                    strip_accents="unicode",
                    stop_words="english",
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=1600,
                    class_weight="balanced",
                    C=2.0,
                    solver="lbfgs",
                    n_jobs=-1,
                ),
            ),
        ]
    )
    pipe.fit(df["text"], df["label"])
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, model_path)
    print(f"Saved classifier to {model_path}")

    if valid_csv and valid_csv.exists():
        valid = pd.read_csv(valid_csv).dropna(subset=["text", "label"])
        pred = pipe.predict(valid["text"])
        metrics = {
            "validation_accuracy": accuracy_score(valid["label"], pred),
            "validation_f1_weighted": f1_score(valid["label"], pred, average="weighted", zero_division=0),
            "validation_f1_macro": f1_score(valid["label"], pred, average="macro", zero_division=0),
            "train_rows": len(df),
            "validation_rows": len(valid),
            "classes": int(df["label"].nunique()),
        }
        metrics_path = model_path.with_suffix(".metrics.json")
        metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
        print(f"Validation accuracy: {metrics['validation_accuracy']:.3f}")
        print(f"Validation weighted F1: {metrics['validation_f1_weighted']:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=Path("data/processed/train.csv"))
    parser.add_argument("--valid", type=Path, default=Path("data/processed/valid.csv"))
    parser.add_argument("--out", type=Path, default=Path("models/specialty_classifier.joblib"))
    args = parser.parse_args()
    train(args.train, args.out, args.valid)


if __name__ == "__main__":
    main()

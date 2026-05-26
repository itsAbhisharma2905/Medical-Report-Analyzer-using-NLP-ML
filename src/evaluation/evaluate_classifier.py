from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from src.evaluation.metrics import evaluate_classification, plot_confusion_matrix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=Path("models/specialty_classifier.joblib"))
    parser.add_argument("--test", type=Path, default=Path("data/processed/test.csv"))
    parser.add_argument("--out", type=Path, default=Path("reports/classifier_metrics.json"))
    args = parser.parse_args()

    model = joblib.load(args.model)
    df = pd.read_csv(args.test).dropna(subset=["text", "label"])
    pred = model.predict(df["text"])
    metrics = evaluate_classification(df["label"], pred)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    serializable = {k: v for k, v in metrics.items() if k != "report"}
    serializable["report"] = metrics["report"]
    serializable["rows"] = len(df)
    serializable["classes"] = int(df["label"].nunique())
    serializable["note"] = (
        "Medical specialty labels are highly imbalanced. Use weighted F1 together with accuracy, "
        "and consider --include-keywords in dataset_loader only for metadata-assisted Kaggle benchmarks."
    )
    args.out.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
    plot_confusion_matrix(df["label"], pred, args.out.parent / "figures" / "confusion_matrix.png")
    print(metrics["report"])


if __name__ == "__main__":
    main()

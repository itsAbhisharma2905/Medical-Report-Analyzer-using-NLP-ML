from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score


def evaluate_classification(y_true, y_pred) -> dict:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision_macro": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "report": classification_report(y_true, y_pred, zero_division=0),
    }


def plot_confusion_matrix(y_true, y_pred, output: str | Path) -> None:
    labels = sorted(set(y_true) | set(y_pred))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(max(8, len(labels) * 0.55), 6))
    sns.heatmap(cm, cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=180)
    plt.close()


def plot_entity_frequency(entity_counts: dict, output: str | Path) -> None:
    df = pd.DataFrame({"entity_type": list(entity_counts), "count": list(entity_counts.values())})
    plt.figure(figsize=(8, 4.5))
    sns.barplot(data=df, x="entity_type", y="count", palette="viridis")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=180)
    plt.close()

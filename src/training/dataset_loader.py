from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


KAGGLE_DATASET = "tboyle10/medicaltranscriptions"


class DatasetLoader:
    def __init__(self, data_dir: str | Path = "data") -> None:
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def download_kaggle(self) -> Path:
        try:
            subprocess.run(
                ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET, "-p", str(self.raw_dir), "--unzip"],
                check=True,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Install kaggle and configure ~/.kaggle/kaggle.json first.") from exc
        csvs = list(self.raw_dir.glob("*.csv"))
        if not csvs:
            raise FileNotFoundError("Kaggle download completed but no CSV was found.")
        return csvs[0]

    def load_transcriptions(
        self,
        csv_path: str | Path | None = None,
        include_keywords: bool = False,
        top_labels: int | None = None,
    ) -> pd.DataFrame:
        if csv_path is None:
            csvs = list(self.raw_dir.glob("*.csv"))
            csv_path = csvs[0] if csvs else self.download_kaggle()
        df = pd.read_csv(csv_path)
        label_col = "medical_specialty" if "medical_specialty" in df.columns else None
        if label_col:
            df = df.rename(columns={label_col: "label"})
        else:
            df["label"] = "unknown"

        text_parts = []
        for col in ["sample_name", "description", "transcription"]:
            if col in df.columns:
                text_parts.append(df[col].fillna("").astype(str))
        if include_keywords and "keywords" in df.columns:
            text_parts.append(df["keywords"].fillna("").astype(str))
        if not text_parts:
            text_parts.append(df[df.columns[-1]].fillna("").astype(str))

        df["text"] = text_parts[0]
        for part in text_parts[1:]:
            df["text"] = df["text"] + ". " + part

        df = df[["text", "label"]].dropna()
        df["text"] = df["text"].map(self.normalize_text)
        df["label"] = df["label"].astype(str).str.strip()
        df = df[df["text"].str.len() > 30].reset_index(drop=True)
        if top_labels:
            keep = df["label"].value_counts().head(top_labels).index
            df = df[df["label"].isin(keep)].reset_index(drop=True)
        return df

    def split(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        train, tmp = train_test_split(df, test_size=0.30, random_state=42, stratify=self._safe_stratify(df["label"]))
        valid, test = train_test_split(tmp, test_size=0.50, random_state=42, stratify=self._safe_stratify(tmp["label"]))
        return train, valid, test

    def prepare(
        self,
        csv_path: str | Path | None = None,
        include_keywords: bool = False,
        top_labels: int | None = 5,
    ) -> None:
        df = self.load_transcriptions(csv_path, include_keywords=include_keywords, top_labels=top_labels)
        train, valid, test = self.split(df)
        train.to_csv(self.processed_dir / "train.csv", index=False)
        valid.to_csv(self.processed_dir / "valid.csv", index=False)
        test.to_csv(self.processed_dir / "test.csv", index=False)
        meta = pd.DataFrame(
            [
                {
                    "rows": len(df),
                    "classes": df["label"].nunique(),
                    "include_keywords": include_keywords,
                    "top_labels": top_labels,
                    "dataset": KAGGLE_DATASET,
                }
            ]
        )
        meta.to_csv(self.processed_dir / "dataset_metadata.csv", index=False)

    @staticmethod
    def normalize_text(text: str) -> str:
        text = str(text).lower()
        text = re.sub(r"\b\d+(?:\.\d+)?\b", " NUM ", text)
        text = re.sub(r"[^a-z0-9/%.\-\s]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _safe_stratify(self, labels: pd.Series):
        return labels if labels.value_counts().min() >= 2 else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--data-dir", default="data")
    parser.add_argument(
        "--include-keywords",
        action="store_true",
        help="Use Kaggle keyword metadata. Improves benchmark accuracy but can leak specialty clues.",
    )
    parser.add_argument(
        "--top-labels",
        type=int,
        default=5,
        help="Keep only the N most frequent specialties. Use 0 for all 40 labels.",
    )
    args = parser.parse_args()
    DatasetLoader(args.data_dir).prepare(
        args.csv,
        include_keywords=args.include_keywords,
        top_labels=args.top_labels or None,
    )
    print("Prepared train/valid/test CSV files.")


if __name__ == "__main__":
    main()

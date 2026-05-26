from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import MedicalReportAnalyzer
from src.utils import setup_logging


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(description="Analyze unstructured medical reports.")
    parser.add_argument("--pdf", type=Path, help="Path to a PDF report")
    parser.add_argument("--text", type=str, help="Raw report text")
    parser.add_argument("--out", type=Path, default=Path("reports/analysis.json"))
    args = parser.parse_args()

    analyzer = MedicalReportAnalyzer()
    if args.pdf:
        result = analyzer.analyze_pdf(args.pdf)
    elif args.text:
        result = analyzer.analyze_text(args.text)
    else:
        parser.error("Provide --pdf or --text")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    analyzer.export_json(result, args.out)
    print(f"Saved analysis to {args.out}")
    print(result["summary"])


if __name__ == "__main__":
    main()

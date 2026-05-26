from __future__ import annotations

import tempfile
from pathlib import Path

import pdfplumber

from src.utils import get_logger

log = get_logger(__name__)


class PDFExtractionError(RuntimeError):
    pass


class PDFExtractor:
    """Extract text from digital PDFs and optionally try OCR for image-only pages."""

    def __init__(self, enable_ocr: bool = True) -> None:
        self.enable_ocr = enable_ocr

    def extract(self, pdf_path: str | Path) -> str:
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported by PDFExtractor")

        text = self._extract_with_pdfplumber(path)
        if len(text.strip()) > 50:
            return text

        if self.enable_ocr:
            log.info("PDF text layer was sparse; trying OCR fallback for %s", path.name)
            ocr_text = self._extract_with_ocr(path)
            if ocr_text.strip():
                return ocr_text

        raise PDFExtractionError("Could not extract useful text from PDF")

    def _extract_with_pdfplumber(self, path: Path) -> str:
        chunks: list[str] = []
        try:
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
                    if page_text.strip():
                        chunks.append(f"\n[page {i}]\n{page_text}")
        except Exception as exc:
            log.warning("pdfplumber failed for %s: %s", path.name, exc)
        return "\n".join(chunks).strip()

    def _extract_with_ocr(self, path: Path) -> str:
        try:
            import fitz
            import pytesseract
            from PIL import Image
        except Exception as exc:
            log.warning("OCR dependencies are missing: %s", exc)
            return ""

        text_parts: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            doc = fitz.open(path)
            for page_no in range(len(doc)):
                pix = doc[page_no].get_pixmap(dpi=220)
                image_path = Path(tmp) / f"page-{page_no + 1}.png"
                pix.save(image_path)
                try:
                    image = Image.open(image_path)
                    text_parts.append(pytesseract.image_to_string(image))
                except Exception as exc:
                    log.warning("OCR failed on page %s: %s", page_no + 1, exc)
        return "\n".join(text_parts).strip()

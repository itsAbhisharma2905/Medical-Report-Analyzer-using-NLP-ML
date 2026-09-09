from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from src.utils import get_logger

log = get_logger(__name__)


class PDFExtractionError(RuntimeError):
    pass


class OCRUnavailableError(RuntimeError):
    pass


class PDFExtractor:
    """Extract text from digital PDFs and optionally try OCR for image-only pages."""

    def __init__(self, enable_ocr: bool = True, use_pdfplumber: bool = True) -> None:
        self.enable_ocr = enable_ocr
        self.use_pdfplumber = use_pdfplumber

    def extract(self, pdf_path: str | Path) -> str:
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported by PDFExtractor")

        text = (
            self._extract_with_pdfplumber(path)
            if self.use_pdfplumber
            else self._extract_with_pypdf(path)
        )
        if len(text.strip()) > 50:
            return text

        if self.enable_ocr:
            log.info("PDF text layer was sparse; trying OCR fallback for %s", path.name)
            try:
                ocr_text = self._extract_with_ocr(path)
            except OCRUnavailableError as exc:
                raise PDFExtractionError(str(exc)) from exc
            if ocr_text.strip():
                return ocr_text

        if not self.enable_ocr:
            raise PDFExtractionError("Could not extract useful text from PDF because OCR is disabled")
        raise PDFExtractionError("Could not extract useful text from PDF")

    def _extract_with_pdfplumber(self, path: Path) -> str:
        chunks: list[str] = []
        try:
            import pdfplumber

            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
                    if page_text.strip():
                        chunks.append(f"\n[page {i}]\n{page_text}")
        except Exception as exc:
            log.warning("pdfplumber failed for %s: %s", path.name, exc)
        return "\n".join(chunks).strip()

    def _extract_with_pypdf(self, path: Path) -> str:
        chunks: list[str] = []
        try:
            from pypdf import PdfReader

            reader = PdfReader(path)
            for i, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    chunks.append(f"\n[page {i}]\n{page_text}")
        except Exception:
            log.warning("lightweight PDF text extraction failed")
        return "\n".join(chunks).strip()

    def _extract_with_ocr(self, path: Path) -> str:
        if shutil.which("tesseract") is None:
            raise OCRUnavailableError(
                "OCR is unavailable because the Tesseract executable is not installed"
            )
        try:
            import fitz
            import pytesseract
            from PIL import Image
        except Exception as exc:
            log.warning("OCR dependencies are unavailable")
            raise OCRUnavailableError("OCR dependencies are not installed") from exc

        try:
            pytesseract.get_tesseract_version()
        except Exception as exc:
            raise OCRUnavailableError("OCR is unavailable because Tesseract could not be started") from exc

        text_parts: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            with fitz.open(path) as doc:
                for page_no in range(len(doc)):
                    pix = doc[page_no].get_pixmap(dpi=220)
                    image_path = Path(tmp) / f"page-{page_no + 1}.png"
                    pix.save(image_path)
                    try:
                        with Image.open(image_path) as image:
                            text_parts.append(pytesseract.image_to_string(image))
                    except Exception:
                        log.warning("OCR failed on page %s", page_no + 1)
        return "\n".join(text_parts).strip()

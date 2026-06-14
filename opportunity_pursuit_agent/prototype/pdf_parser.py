"""
PDF text extractor — wraps pdfplumber.
In production this would also handle:
  - Scanned PDFs (OCR via AWS Textract or Google Document AI)
  - Portal-exported HTML/JSON
  - Word documents
"""

import os

def extract_pdf_text(path: str) -> str:
    """Return full text of a PDF, page by page."""
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")

    if not os.path.exists(path):
        raise FileNotFoundError(f"PDF not found: {path}")

    with pdfplumber.open(path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]

    return "\n\n".join(pages).strip()

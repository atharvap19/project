
"""Render a .docx to PDF using docx2pdf."""

import os
import threading
from contextlib import contextmanager
from pathlib import Path

from docx2pdf import convert

# Word's automation interface is one instance per user session and is not safe
# to drive from two threads at once, so conversions are serialised.
_WORD_LOCK = threading.Lock()


class ConversionError(RuntimeError):
    """Raised when a document could not be rendered to PDF."""


@contextmanager
def com_initialised():
    """
    Initialise COM for the calling thread on Windows.

    docx2pdf calls win32com straight away without doing this, and Streamlit
    runs scripts on a ScriptRunner thread rather than the main one, so without
    it every conversion fails with "CoInitialize has not been called".
    """

    if os.name != "nt":
        yield
        return

    import pythoncom

    pythoncom.CoInitialize()

    try:
        yield
    finally:
        pythoncom.CoUninitialize()


def convert_docx_to_pdf(docx_path, output_dir, backend=None):
    """
    Render docx_path to a PDF inside output_dir and return its path.

    Uses docx2pdf, which relies on Microsoft Word on Windows.
    """

    docx_path = Path(docx_path)
    output_dir = Path(output_dir)

    if not docx_path.exists():
        raise FileNotFoundError(f"Document not found: {docx_path}")

    if docx_path.suffix.lower() != ".docx":
        raise ValueError("Input file must be a .docx file.")

    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = output_dir / f"{docx_path.stem}.pdf"

    try:
        with _WORD_LOCK, com_initialised():
            convert(str(docx_path), str(pdf_path))
    except Exception as exc:
        raise ConversionError(
            f"Could not convert DOCX to PDF: {exc}"
        ) from exc

    if not pdf_path.exists():
        raise ConversionError(
            f"PDF was not produced: {pdf_path}"
        )

    return pdf_path


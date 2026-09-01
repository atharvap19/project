"""The review pipeline: .docx -> PDF -> extracted document.

The uploaded .docx is kept in uploads/ and the rendered PDF in converted/, so
both are on disk for inspection after a review.
"""

from pathlib import Path

from app.converter.docx_to_pdf import convert_docx_to_pdf
from app.engine.rule_engine import RuleEngine
from app.extractor.pdf_extractor import extract_pdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPLOAD_DIR = PROJECT_ROOT / "uploads"
CONVERTED_DIR = PROJECT_ROOT / "converted"


def save_upload(data, filename):
    """
    Write uploaded bytes to uploads/ and return the path.

    `Path(filename).name` strips any directory component, so a crafted
    filename cannot write outside the uploads folder.
    """

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    docx_path = UPLOAD_DIR / Path(filename).name

    with open(docx_path, "wb") as target:
        target.write(data)

    return docx_path


def extract_document(docx_path, filename=None, output_dir=None):
    """
    Render a .docx to PDF and extract it.

    `filename` is the name reported in the result; pass the name the user
    uploaded, because Rule 1 compares the title against it.
    """

    docx_path = Path(docx_path)
    filename = filename or docx_path.name

    pdf_path = convert_docx_to_pdf(
        docx_path,
        output_dir or CONVERTED_DIR,
    )

    document = extract_pdf(pdf_path, filename=filename)

    document["pdf_path"] = str(pdf_path)

    return document


def review_document(docx_path, filename=None, engine=None):
    """
    Extract a document and run every compliance rule against it.

    Returns (document, results).
    """

    document = extract_document(docx_path, filename=filename)

    results = (engine or RuleEngine()).run(document)

    return document, results

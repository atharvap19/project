import aspose.words as aw
from pathlib import Path


def convert_docx_to_pdf(docx_path, pdf_path):

    docx_path = Path(docx_path)
    pdf_path = Path(pdf_path)

    # Check if the input file exists
    if not docx_path.exists():
        raise FileNotFoundError(
            f"The input file {docx_path} does not exist."
        )

    # Check if it is a DOCX file
    if docx_path.suffix.lower() != ".docx":
        raise ValueError(
            f"The input file {docx_path} is not a .docx file."
        )

    # Create output directory if it doesn't exist
    pdf_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # Output PDF path
    pdf_file = pdf_path / (
        docx_path.stem + ".pdf"
    )

    try:

        # Load the Word document
        document = aw.Document(
            str(docx_path)
        )

        # Convert DOCX to PDF
        document.save(
            str(pdf_file)
        )

    except Exception as e:

        raise RuntimeError(
            f"Conversion failed: {str(e)}"
        )

    # Check whether PDF was created
    if not pdf_file.exists():

        raise RuntimeError(
            f"Conversion failed: "
            f"{pdf_file} was not created."
        )

    return pdf_file
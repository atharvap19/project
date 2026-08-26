import re
import fitz


# ---------------------------------------------------------
# Date patterns
# ---------------------------------------------------------

DATE_PATTERNS = [
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
    r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
    r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b",
]


# ---------------------------------------------------------
# Signature-related keywords
# ---------------------------------------------------------

SIGNATURE_KEYWORDS = [
    r"\bsignature\b",
    r"\bsigned\s+by\b",
    r"\bapproved\s+by\b",
    r"\breviewed\s+by\b",
    r"\bprepared\s+by\b",
]


# ---------------------------------------------------------
# Extract dates from text spans
# ---------------------------------------------------------

def extract_dates_from_span(text, bbox, page_number):

    dates = []

    for pattern in DATE_PATTERNS:

        matches = re.finditer(
            pattern,
            text,
            re.IGNORECASE
        )

        for match in matches:

            # Approximate x-position of the date
            x = bbox[0]

            # Approximate y-position
            y = bbox[1]

            dates.append({
                "text": match.group(0),
                "page": page_number,
                "x": x,
                "y": y,
                "bbox": bbox
            })

    return dates


# ---------------------------------------------------------
# Extract signatures from text spans
# ---------------------------------------------------------

def extract_signatures_from_span(text, bbox, page_number):

    signatures = []

    for pattern in SIGNATURE_KEYWORDS:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            signatures.append({
                "text": match.group(0),
                "page": page_number,
                "x": bbox[0],
                "y": bbox[1],
                "bbox": bbox
            })

    # Also detect signature lines

    if re.search(r"_{3,}", text):

        signatures.append({
            "text": text.strip(),
            "page": page_number,
            "x": bbox[0],
            "y": bbox[1],
            "bbox": bbox
        })

    return signatures


# ---------------------------------------------------------
# Extract footer
# ---------------------------------------------------------

def extract_footer(page):

    page_height = page.rect.height

    footer_start = page_height * 0.85

    footer_text_parts = []

    blocks = page.get_text("dict")["blocks"]

    for block in blocks:

        if "lines" not in block:
            continue

        for line in block["lines"]:

            for span in line["spans"]:

                bbox = span["bbox"]

                # Only look at bottom 15% of page
                if bbox[1] >= footer_start:

                    footer_text_parts.append(
                        span["text"]
                    )

    return " ".join(
        footer_text_parts
    ).strip()


# ---------------------------------------------------------
# Main PDF extractor
# ---------------------------------------------------------

def extract_pdf(pdf_path):

    pdf = fitz.open(pdf_path)

    document = {
        "filename": str(pdf_path),
        "full_text": "",
        "pages": [],
        "spans": [],
        "signatures": [],
        "dates": []
    }

    # -----------------------------------------------------
    # Process each page
    # -----------------------------------------------------

    for page_index, page in enumerate(pdf):

        page_number = page_index + 1

        page_text = page.get_text("text")

        # ---------------------------------------------
        # Footer
        # ---------------------------------------------

        footer_text = extract_footer(page)

        # ---------------------------------------------
        # Page information
        # ---------------------------------------------

        page_data = {
            "page_number": page_number,
            "text": page_text,
            "footer_text": footer_text
        }

        document["pages"].append(
            page_data
        )

        document["full_text"] += (
            page_text + "\n"
        )

        # ---------------------------------------------
        # Detailed text information
        # ---------------------------------------------

        page_dict = page.get_text("dict")

        for block in page_dict["blocks"]:

            if "lines" not in block:
                continue

            for line in block["lines"]:

                for span in line["spans"]:

                    text = span["text"]
                    bbox = span["bbox"]

                    # ---------------------------------
                    # Store span information
                    # ---------------------------------

                    document["spans"].append({
                        "text": text,
                        "font": span["font"],
                        "size": span["size"],
                        "flags": span["flags"],
                        "bbox": bbox,
                        "page": page_number
                    })

                    # ---------------------------------
                    # Find dates
                    # ---------------------------------

                    dates = extract_dates_from_span(
                        text,
                        bbox,
                        page_number
                    )

                    document["dates"].extend(
                        dates
                    )

                    # ---------------------------------
                    # Find signatures
                    # ---------------------------------

                    signatures = extract_signatures_from_span(
                        text,
                        bbox,
                        page_number
                    )

                    document["signatures"].extend(
                        signatures
                    )

    pdf.close()

    return document
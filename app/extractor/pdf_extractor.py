"""Extract reviewable information from a rendered PDF using PyMuPDF.

Everything here comes from the laid-out page, so page numbers, headers and
footers are the ones a reader would actually see.

The output is the contract the rules consume:

    filename
    page_count
    full_text
    body_text
    metadata
    pages       [{page_number, text, header, footer, tables}]
    formatting  [{page, paragraph, text, font_name, font_size, bold, type}]
    tables      [{table_index, page, rows}]
"""

import re
from pathlib import Path

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf


# A band at the top/bottom of the page counts as header/footer. Word's default
# margins put running heads well inside these.
HEADER_BAND = 0.08
FOOTER_BAND = 0.90

# Body text is whatever is not noticeably larger or bolder than the norm.
HEADING_SIZE_RATIO = 1.15

# Spans whose line tops are within this many points are on the same visual
# line. Cells in a table row rarely align to the exact same value.
LINE_TOLERANCE = 3.0

WHITESPACE = re.compile(r"[ \t]+")

# PyMuPDF sets bit 4 of span["flags"] for bold faces.
BOLD_FLAG = 1 << 4


def clean_text(text):
    """
    Collapse redundant whitespace, keeping line structure.
    """

    if not text:
        return ""

    lines = []

    for line in text.replace("\r", "\n").split("\n"):

        line = WHITESPACE.sub(" ", line).strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def is_bold(span):
    """
    True when a span is rendered in a bold face.
    """

    if span.get("flags", 0) & BOLD_FLAG:
        return True

    return "bold" in (span.get("font") or "").lower()


def iter_spans(page):
    """
    Every text span on a page, with the geometry the rules need.

    Each entry carries the span itself plus:

        block           index of the layout block (roughly a paragraph)
        line_bbox       rectangle of the line the span sits on
        line_spacing    step down from the previous line of the same block,
                        i.e. the leading, or None on a block's first line
        space_before    gap left by the previous block, or None
    """

    entries = []

    blocks = [
        block
        for block in page.get_text("dict")["blocks"]
        if block.get("lines")
    ]

    gaps = block_gaps(blocks)

    for block_index, block in enumerate(blocks):

        rows = group_lines(block["lines"])

        for row_index, (top, lines) in enumerate(rows):

            if row_index == 0:

                # Nothing above it inside the block, so the gap belongs to
                # the previous paragraph rather than being leading.
                line_spacing = None
                space_before = gaps[block_index]

            else:

                line_spacing = round(top - rows[row_index - 1][0], 1)
                space_before = None

            for line, spans in lines:

                for span in spans:

                    entries.append(
                        {
                            "span": span,
                            "block": block_index,
                            "line_bbox": line["bbox"],
                            "line_spacing": line_spacing,
                            "space_before": space_before,
                        }
                    )

    assign_line_numbers(entries)

    return entries


def group_lines(lines):
    """
    Group a block's lines into visual rows, top down.

    PyMuPDF reports each cell of a table row as its own line. They share a
    vertical position, so without grouping they look like consecutive lines
    with zero leading between them.

    Returns [(top, [(line, spans), ...]), ...].
    """

    rows = []

    for line in lines:

        spans = [
            span
            for span in line["spans"]
            if span.get("text", "").strip()
        ]

        if not spans:
            continue

        top = line["bbox"][1]

        for row in rows:

            if abs(row[0] - top) <= LINE_TOLERANCE:
                row[1].append((line, spans))
                break

        else:
            rows.append((top, [(line, spans)]))

    return sorted(rows, key=lambda row: row[0])


def block_gaps(blocks):
    """
    Vertical gap above each block, keyed by its index.

    Blocks arrive in reading order, which puts a footer before the body text
    it sits under, so gaps are measured after sorting top to bottom. Blocks
    that overlap vertically -- side-by-side columns -- get None rather than a
    negative gap.
    """

    gaps = {}

    previous_bottom = None

    for index in sorted(range(len(blocks)), key=lambda i: blocks[i]["bbox"][1]):

        top = blocks[index]["bbox"][1]

        if previous_bottom is None or top < previous_bottom:
            gaps[index] = None
        else:
            gaps[index] = round(top - previous_bottom, 1)

        previous_bottom = blocks[index]["bbox"][3]

    return gaps


def assign_line_numbers(entries):
    """
    Number the visual lines on a page from the top down, in place.

    Grouping is by vertical position rather than by block, so cells sitting
    side by side in a table row share a line number. Rule 7 needs that to ask
    whether a date is on the same line as a signature, which block nesting
    cannot answer.
    """

    tops = sorted({round(entry["line_bbox"][1], 1) for entry in entries})

    groups = []

    for top in tops:

        if groups and top - groups[-1][-1] <= LINE_TOLERANCE:
            groups[-1].append(top)
        else:
            groups.append([top])

    number_of = {
        top: number
        for number, group in enumerate(groups)
        for top in group
    }

    for entry in entries:
        entry["line"] = number_of[round(entry["line_bbox"][1], 1)]


def band_of(span, page_height):
    """
    Classify a span as "header", "footer" or "body" by where it sits.
    """

    top = span["bbox"][1]

    if top <= page_height * HEADER_BAND:
        return "header"

    if top >= page_height * FOOTER_BAND:
        return "footer"

    return "body"


def read_tables(page):
    """
    Extract tables from a page as lists of rows.

    Table detection is best-effort; a page that defeats it simply has none.
    """

    try:
        found = page.find_tables()
    except Exception:
        return []

    tables = []

    for table in found.tables:

        try:
            rows = table.extract()
        except Exception:
            continue

        tables.append(
            [
                [clean_text(cell or "") for cell in row]
                for row in rows
            ]
        )

    return tables


def dominant_size(entries):
    """
    The most common rounded font size across the body of the document.

    This is the baseline that headings are measured against.
    """

    counts = {}

    for entry in entries:

        if entry["band"] != "body":
            continue

        span = entry["span"]

        size = round(span.get("size", 0), 1)
        counts[size] = counts.get(size, 0) + len(span.get("text", ""))

    if not counts:
        return None

    return max(counts, key=counts.get)


def extract_pdf(pdf_path, filename=None):
    """
    Extract text, layout and formatting from a rendered PDF.

    `filename` overrides the name reported in the result, so the original
    .docx name survives the conversion. Rule 1 compares against it.
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = pymupdf.open(pdf_path)

    try:
        return read_document(document, filename or pdf_path.name)
    finally:
        document.close()


def read_document(document, filename):
    """
    Build the result dictionary from an open PyMuPDF document.
    """

    # First pass: collect every span with the band it sits in, so the dominant
    # body size can be worked out before anything is classified.
    per_page = []

    for page_index, page in enumerate(document):

        height = page.rect.height

        entries = iter_spans(page)

        for entry in entries:
            entry["band"] = band_of(entry["span"], height)

        per_page.append((page_index + 1, page, entries))

    baseline = dominant_size(
        [entry for _, _, entries in per_page for entry in entries]
    )

    result = {
        "filename": filename,
        "page_count": document.page_count,
        "full_text": "",
        "body_text": "",
        "metadata": dict(document.metadata or {}),
        "pages": [],
        "formatting": [],
        "tables": [],
    }

    all_text = []
    body_only = []

    for page_number, page, entries in per_page:

        header_parts = []
        footer_parts = []
        body_parts = []

        for entry in entries:

            span = entry["span"]
            band = entry["band"]
            text = span["text"]

            if band == "header":
                header_parts.append(text)
            elif band == "footer":
                footer_parts.append(text)
            else:
                body_parts.append(text)

            result["formatting"].append(
                {
                    "page": page_number,
                    "paragraph": entry["block"],
                    "line": entry["line"],
                    "text": clean_text(text),
                    "font_name": span.get("font"),
                    "font_size": round(span.get("size", 0), 1),
                    "bold": is_bold(span),
                    "type": classify(span, band, baseline),
                    "bbox": [round(value, 1) for value in span["bbox"]],
                    "line_spacing": entry["line_spacing"],
                    "space_before": entry["space_before"],
                }
            )

        # The full page text, in reading order, rather than the band split.
        page_text = clean_text(page.get_text("text"))

        tables = read_tables(page)

        for rows in tables:
            result["tables"].append(
                {
                    "table_index": len(result["tables"]),
                    "page": page_number,
                    "rows": rows,
                }
            )

        result["pages"].append(
            {
                "page_number": page_number,
                "text": page_text,
                "header": clean_text(" ".join(header_parts)),
                "footer": clean_text(" ".join(footer_parts)),
                "tables": tables,
            }
        )

        all_text.append(page_text)
        body_only.append(clean_text(" ".join(body_parts)))

    result["full_text"] = "\n".join(part for part in all_text if part)
    result["body_text"] = "\n".join(part for part in body_only if part)

    return result


def classify(span, band, baseline):
    """
    Label a span "header", "footer", "title", "heading" or "body".

    Rule 8 skips everything that is not body text when looking for font
    inconsistencies, so headings must not be reported as anomalies.
    """

    if band in ("header", "footer"):
        return band

    if baseline is None:
        return "body"

    size = round(span.get("size", 0), 1)

    if size >= baseline * 1.5:
        return "title"

    if size >= baseline * HEADING_SIZE_RATIO:
        return "heading"

    if is_bold(span) and size > baseline:
        return "heading"

    return "body"

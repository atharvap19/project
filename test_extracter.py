"""Run the full pipeline over a .docx and print what the extractor found.

Usage:

    python test_extracter.py [path/to/document.docx]

With no argument it uses the first .docx in uploads/.
"""

import sys
from pathlib import Path

from app.pipeline import UPLOAD_DIR, review_document


def pick_document():
    """
    The path given on the command line, or the first .docx in uploads/.
    """

    if len(sys.argv) > 1:
        return Path(sys.argv[1])

    candidates = sorted(UPLOAD_DIR.glob("*.docx"))

    if not candidates:
        sys.exit(
            f"No .docx given and none found in {UPLOAD_DIR}.\n"
            "Usage: python test_extracter.py path/to/document.docx"
        )

    return candidates[0]


docx_path = pick_document()

if not docx_path.exists():
    sys.exit(f"Document not found: {docx_path}")

print(f"Reviewing: {docx_path}")

document, results = review_document(docx_path, filename=docx_path.name)


print("\n========== DOCUMENT ==========")
print("Filename  :", document["filename"])
print("Page count:", document["page_count"])
print("Rendered  :", document["pdf_path"])
print("Metadata  :", {k: v for k, v in document["metadata"].items() if v})


print("\n========== PAGES ==========")

for page in document["pages"]:

    print(f"\n--- Page {page['page_number']} ---")
    print("Header:", repr(page["header"]))
    print("Footer:", repr(page["footer"]))
    print("Tables:", len(page["tables"]))
    print("Text  :")
    print(page["text"])


print("\n========== TABLES ==========")

for table in document["tables"]:

    print(f"\nTable {table['table_index']} (page {table['page']}):")

    for row in table["rows"]:
        print("  ", row)


print("\n========== FONTS ==========")

for span in document["formatting"][:15]:
    print({
        "text": span["text"][:40],
        "font": span["font_name"],
        "size": span["font_size"],
        "type": span["type"],
        "page": span["page"]
    })


print("\n========== COMPLIANCE RESULTS ==========")

tally = {}

for result in results:

    tally[result["status"]] = tally.get(result["status"], 0) + 1

    print(
        f"[{result['status']:<7}] "
        f"{result['rule_id']:>2} "
        f"{result['rule_name']}"
    )
    print(f"          {result['message']}")

print("\nSummary:", tally)

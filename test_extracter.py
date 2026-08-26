from app.extractor.pdf_extractor import extract_pdf


pdf_path = "test_output/document_reviewer_test.pdf"

document = extract_pdf(pdf_path)


print("\n========== BASIC INFORMATION ==========")

print("Pages:", len(document["pages"]))

print(
    "Full text length:",
    len(document["full_text"])
)


print("\n========== DATES ==========")

for date in document["dates"]:
    print(date)


print("\n========== SIGNATURES ==========")

for signature in document["signatures"]:
    print(signature)


print("\n========== FONTS ==========")

for span in document["spans"][:10]:
    print({
        "text": span["text"],
        "font": span["font"],
        "size": span["size"],
        "page": span["page"]
    })


print("\n========== FOOTERS ==========")

for page in document["pages"]:
    print(
        page["page_number"],
        ":",
        page["footer_text"]
    )
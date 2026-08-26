import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

import streamlit as st
import tempfile

from app.converter.docx_to_pdf import convert_docx_to_pdf
from app.extractor.pdf_extractor import extract_pdf
from app.engine.rule_engine import RuleEngine


# ---------------------------------------
# Page configuration
# ---------------------------------------

st.set_page_config(
    page_title="Document Reviewer",
    layout="wide"
)


# ---------------------------------------
# Title
# ---------------------------------------

st.title("Document Reviewer")

st.write(
    "Upload a Word document to analyze it "
    "against the document compliance rules."
)


# ---------------------------------------
# Upload
# ---------------------------------------

uploaded_file = st.file_uploader(
    "Upload your Word document",
    type=["docx"]
)


# ---------------------------------------
# Review
# ---------------------------------------

if uploaded_file:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    if st.button("Review Document"):

        try:

            # --------------------------------
            # Temporary directory
            # --------------------------------

            with tempfile.TemporaryDirectory() as temp_dir:

                temp_dir = Path(temp_dir)

                docx_path = (
                    temp_dir /
                    uploaded_file.name
                )

                # --------------------------------
                # Save uploaded DOCX
                # --------------------------------

                with open(
                    docx_path,
                    "wb"
                ) as file:

                    file.write(
                        uploaded_file.getbuffer()
                    )

                st.info(
                    "Step 1/4: Document uploaded"
                )

                # --------------------------------
                # DOCX → PDF
                # --------------------------------

                with st.spinner(
                    "Converting DOCX to PDF..."
                ):

                    pdf_path = (
                        convert_docx_to_pdf(
                            docx_path,
                            temp_dir
                        )
                    )

                st.success(
                    "Step 2/4: DOCX converted to PDF"
                )

                # --------------------------------
                # Extract PDF
                # --------------------------------

                with st.spinner(
                    "Extracting document information..."
                ):

                    document = extract_pdf(
                        pdf_path
                    )

                document["filename"] = (
                    uploaded_file.name
                )

                st.success(
                    "Step 3/4: PDF extracted successfully"
                )

                # --------------------------------
                # Extracted Information
                # --------------------------------

                st.subheader(
                    "Extracted Information"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "Pages",
                        len(document["pages"])
                    )

                with col2:

                    st.metric(
                        "Dates Found",
                        len(document["dates"])
                    )

                with col3:

                    st.metric(
                        "Signatures Found",
                        len(document["signatures"])
                    )

                # --------------------------------
                # Dates
                # --------------------------------

                with st.expander(
                    "Detected Dates"
                ):

                    st.json(
                        document["dates"]
                    )

                # --------------------------------
                # Signatures
                # --------------------------------

                with st.expander(
                    "Detected Signatures"
                ):

                    st.json(
                        document["signatures"]
                    )

                # --------------------------------
                # Fonts
                # --------------------------------

                with st.expander(
                    "Font Information"
                ):

                    st.json(
                        document["spans"][:50]
                    )

                # --------------------------------
                # Footers
                # --------------------------------

                with st.expander(
                    "Footer Information"
                ):

                    for page in document["pages"]:

                        st.write(
                            f"Page {page['page_number']}"
                        )

                        st.code(
                            page["footer_text"]
                        )

                # --------------------------------
                # Run Rule Engine
                # --------------------------------

                with st.spinner(
                    "Running compliance rules..."
                ):

                    engine = RuleEngine()

                    results = engine.run(
                        document
                    )

                st.success(
                    "Step 4/4: Rules completed"
                )

                # --------------------------------
                # Results
                # --------------------------------

                st.subheader(
                    "Compliance Results"
                )

                for result in results:

                    status = result["status"]

                    if status == "PASS":

                        st.success(
                            f"Rule {result['rule_id']} — "
                            f"{result['rule_name']} — PASS"
                        )

                    elif status == "FAIL":

                        st.error(
                            f"Rule {result['rule_id']} — "
                            f"{result['rule_name']} — FAIL"
                        )

                    elif status == "WARNING":

                        st.warning(
                            f"Rule {result['rule_id']} — "
                            f"{result['rule_name']} — WARNING"
                        )

                    else:

                        st.warning(
                            f"Rule {result['rule_id']} — "
                            f"{result['rule_name']} — ERROR"
                        )

                    st.write(
                        result["message"]
                    )

                    if result.get("evidence"):

                        with st.expander(
                            "View evidence"
                        ):

                            st.json(
                                result["evidence"]
                            )

        except Exception as e:

            st.error(
                f"Document review failed: {str(e)}"
            )
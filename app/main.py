import sys

from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

import streamlit as st

from app.converter.docx_to_pdf import ConversionError
from app.engine.rule_engine import RuleEngine
from app.pipeline import extract_document, save_upload


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
            # Save uploaded DOCX to uploads/
            # --------------------------------

            docx_path = save_upload(
                uploaded_file.getbuffer(),
                uploaded_file.name
            )


            st.info(
                "Step 1/2: Document uploaded"
            )

            # --------------------------------
            # Render to PDF and extract
            # --------------------------------

            with st.spinner(
                "Converting to PDF and extracting..."
            ):

                # The uploaded name is passed through because Rule 1
                # compares the title against it.
                document = extract_document(
                    docx_path,
                    filename=uploaded_file.name
                )

            st.success(
                "Step 2/2: Document extracted successfully"
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
                    document.get("page_count", 0)
                )

            with col2:

                st.metric(
                    "Text spans",
                    len(document.get("formatting", []))
                )

            with col3:

                st.metric(
                    "Tables",
                    len(document.get("tables", []))
                )

            # --------------------------------
            # Full Text
            # --------------------------------

            with st.expander(
                "Extracted Text"
            ):

                st.text(
                    document.get(
                        "full_text",
                        ""
                    )
                )

            # --------------------------------
            # Pages
            # --------------------------------

            with st.expander(
                "Page Information"
            ):

                for page in document.get("pages", []):

                    st.markdown(
                        f"**Page {page['page_number']}**"
                    )

                    st.write(
                        {
                            "header": page["header"],
                            "footer": page["footer"],
                            "tables": len(page["tables"])
                        }
                    )

                    st.text(page["text"])

            # --------------------------------
            # Tables
            # --------------------------------

            with st.expander(
                "Table Information"
            ):

                st.json(
                    document.get(
                        "tables",
                        []
                    )
                )

            # --------------------------------
            # Formatting
            # --------------------------------

            with st.expander(
                "Font Information"
            ):

                st.json(
                    document.get(
                        "formatting",
                        []
                    )
                )

            # --------------------------------
            # Document metadata
            # --------------------------------

            with st.expander(
                "Document Metadata"
            ):

                st.json(
                    document.get(
                        "metadata",
                        {}
                    )
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

            st.subheader(
                "Compliance Results"
            )

            # --------------------------------
            # Results
            # --------------------------------

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

        except ConversionError as e:

            st.error(
                f"Could not convert the document to PDF: {str(e)}"
            )

        except Exception as e:

            st.error(
                f"Document review failed: {str(e)}"
            )

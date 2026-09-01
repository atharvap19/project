import re

from .base import BaseRule


class FooterRule(BaseRule):

    rule_id = 13
    rule_name = "Footer Details Validation"

    DOC_ID_PATTERNS = [
        r"\bdoc(?:ument)?\s*(?:id|no|number)\s*[:\-]?\s*[A-Za-z0-9\-_\/]+",
        r"\bID\s*[:\-]\s*[A-Za-z0-9\-_\/]+"
    ]

    CONFIDENTIALITY_KEYWORDS = [
        "confidential",
        "confidentiality",
        "internal use only",
        "restricted",
        "proprietary"
    ]

    def find_doc_id(self, text):

        for pattern in self.DOC_ID_PATTERNS:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(0)

        return None

    def find_confidentiality(self, text):

        for keyword in self.CONFIDENTIALITY_KEYWORDS:

            match = re.search(
                rf"\b{re.escape(keyword)}\b",
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(0)

        return None

    def find_page_number(self, text):

        match = re.search(
            r"\bpage\s*(\d+)",
            text,
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))

        return None

    def check(self, document):

        pages = document.get(
            "pages",
            []
        )

        if not pages:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "ERROR",
                "message": "No page information is available.",
                "page": None,
                "evidence": {}
            }

        page_results = []
        missing_details = []

        for page in pages:

            page_number = page["page_number"]

            footer = page.get(
                "footer",
                ""
            )

            doc_id = self.find_doc_id(
                footer
            )

            confidentiality = (
                self.find_confidentiality(
                    footer
                )
            )

            footer_page_number = (
                self.find_page_number(
                    footer
                )
            )

            result = {
                "page": page_number,
                "doc_id": doc_id,
                "page_number": footer_page_number,
                "confidentiality": confidentiality
            }

            page_results.append(result)

            missing = []

            if not doc_id:
                missing.append("Doc ID")

            if footer_page_number is None:
                missing.append("Page number")

            if not confidentiality:
                missing.append("Confidentiality")

            if missing:

                missing_details.append({
                    "page": page_number,
                    "missing": missing
                })

        # -----------------------------------------
        # Missing footer details
        # -----------------------------------------

        if missing_details:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": (
                    "One or more required footer "
                    "details are missing."
                ),
                "page": missing_details[0]["page"],
                "evidence": {
                    "pages": page_results,
                    "missing": missing_details
                }
            }

        # -----------------------------------------
        # PASS
        # -----------------------------------------

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": (
                "Required footer details are present."
            ),
            "page": 1,
            "evidence": {
                "pages": page_results
            }
        }
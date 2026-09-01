import re

from .base import BaseRule


class PageNumberRule(BaseRule):

    rule_id = 11
    rule_name = "Page Number Validation"

    # A bare number is not a page number: identifiers such as
    # "SOP-001" would match it. Require the word "page", or the
    # "1 of 5" form that only page numbers use.
    PAGE_PATTERNS = [
        re.compile(
            r"\bpage\s*[:\-]?\s*(\d+)\b",
            re.IGNORECASE
        ),
        re.compile(
            r"(?<![\w\-])(\d+)\s*(?:of|/)\s*\d+(?![\w\-])",
            re.IGNORECASE
        ),
    ]

    def extract_page_number(self, text):

        if not text:
            return None

        for pattern in self.PAGE_PATTERNS:

            match = pattern.search(text)

            if match:
                return int(match.group(1))

        return None

    def check(self, document):

        pages = document.get("pages", [])

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
        missing_pages = []
        incorrect_pages = []

        for expected_page in pages:

            page_number = expected_page["page_number"]

            # Footer is the preferred location
            footer = expected_page.get(
                "footer",
                ""
            )

            # If footer isn't available, use page text
            text_to_check = footer

            if not text_to_check:
                text_to_check = expected_page.get(
                    "text",
                    ""
                )

            found_number = self.extract_page_number(
                text_to_check
            )

            result = {
                "page": page_number,
                "expected": page_number,
                "found": found_number
            }

            page_results.append(result)

            if found_number is None:

                missing_pages.append(
                    page_number
                )

            elif found_number != page_number:

                incorrect_pages.append(result)

        # -----------------------------------------
        # Missing page numbers
        # -----------------------------------------

        if missing_pages:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": (
                    "Page numbers are missing on "
                    "one or more pages."
                ),
                "page": missing_pages[0],
                "evidence": {
                    "pages": page_results,
                    "missing_pages": missing_pages,
                    "incorrect_pages": incorrect_pages
                }
            }

        # -----------------------------------------
        # Incorrect page numbers
        # -----------------------------------------

        if incorrect_pages:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": (
                    "Page numbers are not in the "
                    "correct sequence."
                ),
                "page": incorrect_pages[0]["page"],
                "evidence": {
                    "pages": page_results,
                    "missing_pages": missing_pages,
                    "incorrect_pages": incorrect_pages
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
                "Page numbers are present and "
                "in sequence."
            ),
            "page": 1,
            "evidence": {
                "pages": page_results
            }
        }
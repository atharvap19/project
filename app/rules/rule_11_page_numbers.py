import re

from .base import BaseRule


class PageNumberRule(BaseRule):

    rule_id = 11
    rule_name = "Page Number Validation"

    def check(self, document):

        pages = document.get("pages", [])

        if not pages:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "WARNING",
                "message": "No pages were available for checking.",
                "evidence": {}
            }

        found_page_numbers = []

        # --------------------------------
        # Check each page
        # --------------------------------

        for page in pages:

            page_text = page.get("text", "")
            page_number = page.get("page_number")

            # Search for common page number formats
            patterns = [
                rf"\bpage\s+{page_number}\b",
                rf"\b{page_number}\s+of\s+\d+\b"
            ]

            found = False

            for pattern in patterns:

                if re.search(
                    pattern,
                    page_text,
                    re.IGNORECASE
                ):
                    found = True
                    break

            # Also check standalone number
            if not found:

                matches = re.findall(
                    r"\b\d+\b",
                    page_text
                )

                if str(page_number) in matches:
                    found = True

            if found:

                found_page_numbers.append(page_number)

        # --------------------------------
        # Check missing page numbers
        # --------------------------------

        expected = [
            page["page_number"]
            for page in pages
        ]

        missing = [
            number
            for number in expected
            if number not in found_page_numbers
        ]

        # --------------------------------
        # Check sequence
        # --------------------------------

        sequential = (
            found_page_numbers == expected
        )

        # --------------------------------
        # Final result
        # --------------------------------

        if missing:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Page numbers are missing on one or more pages.",
                "evidence": {
                    "expected": expected,
                    "found": found_page_numbers,
                    "missing": missing
                }
            }

        if not sequential:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Page numbers are not in sequence.",
                "evidence": {
                    "expected": expected,
                    "found": found_page_numbers
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": "Page numbers are present and sequential.",
            "evidence": {
                "expected": expected,
                "found": found_page_numbers
            }
        }
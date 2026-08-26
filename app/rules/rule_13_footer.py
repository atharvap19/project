import re

from .base import BaseRule


class FooterRule(BaseRule):

    rule_id = 13
    rule_name = "Footer Details Validation"

    def check(self, document):

        pages = document.get("pages", [])

        if not pages:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "WARNING",
                "message": "No pages were available for footer checking.",
                "evidence": {}
            }

        # --------------------------------
        # Required footer details
        # --------------------------------

        required_details = {
            "document_id": [
                r"\bdoc(?:ument)?\s*(?:id|no|number)\b"
            ],

            "confidentiality": [
                r"\bconfidential\b",
                r"\bconfidentiality\b"
            ],

            "page_number": [
                r"\bpage\s+\d+",
                r"\b\d+\s+of\s+\d+\b"
            ]
        }

        results = {}

        # --------------------------------
        # Check every page
        # --------------------------------

        for page in pages:

            page_number = page["page_number"]

            # Use footer text if extractor provides it
            footer_text = page.get(
                "footer_text",
                ""
            )

            page_results = {}

            # --------------------------------
            # Check each required detail
            # --------------------------------

            for detail, patterns in required_details.items():

                found = False

                for pattern in patterns:

                    if re.search(
                        pattern,
                        footer_text,
                        re.IGNORECASE
                    ):
                        found = True
                        break

                page_results[detail] = found

            results[page_number] = page_results

        # --------------------------------
        # Find missing details
        # --------------------------------

        missing = []

        for page_number, page_results in results.items():

            for detail, found in page_results.items():

                if not found:

                    missing.append({
                        "page": page_number,
                        "missing": detail
                    })

        # --------------------------------
        # Final result
        # --------------------------------

        if missing:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "One or more required footer details are missing.",
                "evidence": {
                    "page_results": results,
                    "missing": missing
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": "Required footer details are present on all pages.",
            "evidence": {
                "page_results": results
            }
        }
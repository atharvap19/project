import re
from datetime import datetime

from .base import BaseRule


class RevisionDateRule(BaseRule):

    rule_id = 3
    rule_name = "Revision History Date Validation"

    REVISION_LABELS = [
        "revision history",
        "revision record",
        "document history",
        "change history",
        "revision"
    ]

    DATE_PATTERNS = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"
    ]

    def parse_date(self, date_text):

        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d/%m/%y",
            "%d-%m-%y",
            "%Y/%m/%d",
            "%Y-%m-%d"
        ]

        for fmt in formats:

            try:
                return datetime.strptime(
                    date_text,
                    fmt
                )

            except ValueError:
                continue

        return None

    def check(self, document):

        revision_found = False
        revision_page = None

        revision_dates = []

        # -----------------------------------------
        # Find revision section
        # -----------------------------------------

        for page in document["pages"]:

            page_number = page["page_number"]
            page_text = page.get("text", "")

            for label in self.REVISION_LABELS:

                if re.search(
                    rf"\b{re.escape(label)}\b",
                    page_text,
                    re.IGNORECASE
                ):
                    revision_found = True
                    revision_page = page_number
                    break

            if revision_found:
                break

        # Revision section doesn't exist
        if not revision_found:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Revision history section was not found.",
                "page": None,
                "evidence": {
                    "revision_section": None,
                    "dates": []
                }
            }

        # -----------------------------------------
        # Extract dates from revision history
        # -----------------------------------------

        for page in document["pages"]:

            if page["page_number"] < revision_page:
                continue

            page_text = page.get("text", "")

            for pattern in self.DATE_PATTERNS:

                matches = re.findall(
                    pattern,
                    page_text
                )

                for date_text in matches:

                    parsed = self.parse_date(
                        date_text
                    )

                    revision_dates.append({
                        "date": date_text,
                        "parsed": parsed,
                        "page": page["page_number"]
                    })

        # No dates
        if not revision_dates:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "No valid dates were found in the revision history.",
                "page": revision_page,
                "evidence": {
                    "revision_section_page": revision_page,
                    "dates": []
                }
            }

        # -----------------------------------------
        # Validate dates
        # -----------------------------------------

        invalid_dates = [
            item
            for item in revision_dates
            if item["parsed"] is None
        ]

        if invalid_dates:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Invalid date found in revision history.",
                "page": invalid_dates[0]["page"],
                "evidence": {
                    "revision_section_page": revision_page,
                    "invalid_dates": invalid_dates,
                    "dates": revision_dates
                }
            }

        # -----------------------------------------
        # Check chronological order
        # -----------------------------------------

        for i in range(1, len(revision_dates)):

            previous = revision_dates[i - 1]
            current = revision_dates[i]

            if current["parsed"] < previous["parsed"]:

                return {
                    "rule_id": self.rule_id,
                    "rule_name": self.rule_name,
                    "status": "FAIL",
                    "message": (
                        "Revision history dates are not "
                        "chronological."
                    ),
                    "page": current["page"],
                    "evidence": {
                        "previous_date": previous,
                        "current_date": current,
                        "dates": revision_dates
                    }
                }

        # Everything is valid
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": (
                "Revision history dates are valid "
                "and chronological."
            ),
            "page": revision_page,
            "evidence": {
                "revision_section_page": revision_page,
                "dates": revision_dates
            }
        }
import re
from datetime import datetime

from .base import BaseRule


class RevisionDateRule(BaseRule):

    rule_id = 3
    rule_name = "Revision History Date Validation"

    def check(self, document):

        full_text = document["full_text"]

        # --------------------------------
        # 1. Find Revision History section
        # --------------------------------

        revision_patterns = [
            r"revision\s+history",
            r"revision\s+record",
            r"document\s+history",
            r"revision"
        ]

        revision_start = None

        for pattern in revision_patterns:

            match = re.search(
                pattern,
                full_text,
                re.IGNORECASE
            )

            if match:
                revision_start = match.end()
                break

        # Revision section not found
        if revision_start is None:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Revision history section was not found.",
                "evidence": {
                    "dates": []
                }
            }

        # --------------------------------
        # 2. Extract revision section
        # --------------------------------

        revision_text = full_text[revision_start:]

        # Stop at next major section if possible
        next_section = re.search(
            r"\n\s*(objective|scope|purpose|references|appendix|approval)\s*\n",
            revision_text,
            re.IGNORECASE
        )

        if next_section:
            revision_text = revision_text[:next_section.start()]

        # --------------------------------
        # 3. Find date strings
        # --------------------------------

        date_patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
            r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b"
        ]

        dates_found = []

        for pattern in date_patterns:

            matches = re.findall(
                pattern,
                revision_text,
                re.IGNORECASE
            )

            dates_found.extend(matches)

        # Remove duplicates while maintaining order
        dates_found = list(dict.fromkeys(dates_found))

        # --------------------------------
        # 4. Check if dates exist
        # --------------------------------

        if not dates_found:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "No revision dates were found.",
                "evidence": {
                    "dates": []
                }
            }

        # --------------------------------
        # 5. Validate each date
        # --------------------------------

        invalid_dates = []
        valid_dates = []

        for date_string in dates_found:

            parsed_date = self.parse_date(date_string)

            if parsed_date is None:
                invalid_dates.append(date_string)
            else:
                valid_dates.append(parsed_date)

        # --------------------------------
        # 6. Check chronological order
        # --------------------------------

        chronological = True

        for i in range(1, len(valid_dates)):

            if valid_dates[i] < valid_dates[i - 1]:
                chronological = False
                break

        # --------------------------------
        # 7. Return result
        # --------------------------------

        if invalid_dates:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Invalid date(s) found in revision history.",
                "evidence": {
                    "dates_found": dates_found,
                    "invalid_dates": invalid_dates
                }
            }

        if not chronological:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Revision dates are not in chronological order.",
                "evidence": {
                    "dates_found": dates_found
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": "Revision history dates are valid and chronological.",
            "evidence": {
                "dates_found": dates_found
            }
        }

    # --------------------------------
    # Date parser
    # --------------------------------

    def parse_date(self, date_string):

        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%Y-%m-%d",
            "%d %B %Y",
            "%d %b %Y"
        ]

        for date_format in formats:

            try:

                return datetime.strptime(
                    date_string,
                    date_format
                )

            except ValueError:
                continue

        return None
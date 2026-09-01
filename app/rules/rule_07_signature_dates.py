import re
from datetime import datetime

from .base import BaseRule


class SignatureDateRule(BaseRule):

    rule_id = 7
    rule_name = "Signature Date Validation"

    SIGNATURE_LABELS = [
        "signature",
        "signed by",
        "approved by",
        "reviewed by",
        "prepared by"
    ]

    DATE_PATTERNS = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b"
    ]

    # A signature's date is written on the signature's own line or below it,
    # so the search reaches further down than up. Without the tight upward
    # limit, a date in a table above the signature block gets claimed as the
    # signature's date.
    MAX_LINES_BELOW = 3
    MAX_LINES_ABOVE = 1

    def find_signatures(self, text):

        signatures = []

        for label in self.SIGNATURE_LABELS:

            for match in re.finditer(
                rf"\b{re.escape(label)}\b",
                text,
                re.IGNORECASE
            ):

                signatures.append({
                    "label": match.group(0),
                    "position": match.start()
                })

        # Signature line
        for match in re.finditer(
            r"_{3,}",
            text
        ):

            signatures.append({
                "label": "signature line",
                "position": match.start()
            })

        return signatures

    def find_dates(self, text):

        dates = []

        for pattern in self.DATE_PATTERNS:

            for match in re.finditer(
                pattern,
                text
            ):

                dates.append({
                    "date": match.group(0),
                    "position": match.start()
                })

        return dates

    def lines_for_page(self, document, page_number):
        """
        The text of each visual line on a page, keyed by line number.

        Built from the extractor's spans, which record the line each piece of
        text was rendered on. Cells of a table row share a line number, so a
        date sitting beside a signature counts as being on the same line.
        """

        lines = {}

        for item in document.get("formatting", []):

            if item.get("page") != page_number:
                continue

            line = item.get("line")

            if line is None:
                continue

            lines.setdefault(line, []).append(item.get("text", ""))

        return {
            line: " ".join(parts)
            for line, parts in lines.items()
        }

    def match_by_line(self, lines, page_number):
        """
        Pair each signature with the nearest date on the page, measured in
        rendered lines.

        Distance in characters cannot tell a signature's own date from an
        unrelated one in a nearby table, so anything further away than
        MAX_LINE_DISTANCE lines is not treated as belonging to the signature.
        """

        signatures = [
            (number, signature)
            for number in sorted(lines)
            for signature in self.find_signatures(lines[number])
        ]

        dates = [
            (number, date)
            for number in sorted(lines)
            for date in self.find_dates(lines[number])
        ]

        results = []

        for line, signature in signatures:

            closest_date = None
            closest_distance = None

            for date_line, date in dates:

                offset = date_line - line

                if offset > self.MAX_LINES_BELOW:
                    continue

                if -offset > self.MAX_LINES_ABOVE:
                    continue

                distance = abs(offset)

                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    closest_date = date

            results.append({
                "signature": signature["label"],
                "signature_page": page_number,
                "signature_line": line,
                "date": closest_date["date"] if closest_date else None,
                "date_page": page_number if closest_date else None,
                "line_distance": closest_distance,
                "matched_by": "line"
            })

        return results

    def match_by_position(self, page_text, page_number):
        """
        Pair signatures with dates by character distance.

        Used only when the document carries no layout information.
        """

        signatures = self.find_signatures(page_text)
        dates = self.find_dates(page_text)

        results = []

        for signature in signatures:

            closest_date = None
            closest_distance = None

            for date in dates:

                distance = abs(date["position"] - signature["position"])

                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    closest_date = date

            results.append({
                "signature": signature["label"],
                "signature_page": page_number,
                "date": closest_date["date"] if closest_date else None,
                "date_page": page_number if closest_date else None,
                "distance": closest_distance,
                "matched_by": "text"
            })

        return results

    def check(self, document):

        signature_results = []

        for page in document["pages"]:

            page_number = page["page_number"]

            lines = self.lines_for_page(document, page_number)

            if lines:
                results = self.match_by_line(lines, page_number)
            else:
                results = self.match_by_position(
                    page.get("text", ""),
                    page_number
                )

            signature_results.extend(results)

        # No signatures
        if not signature_results:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "No signature blocks were detected.",
                "page": None,
                "evidence": {
                    "signatures": []
                }
            }

        # Check whether every signature has a date
        missing_dates = [
            result
            for result in signature_results
            if result["date"] is None
        ]

        if missing_dates:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": (
                    "Dates are missing near one or more "
                    "signature blocks."
                ),
                "page": missing_dates[0]["signature_page"],
                "evidence": {
                    "signatures": signature_results,
                    "missing_dates": missing_dates
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": (
                "Dates were found near all "
                "signature blocks."
            ),
            "page": signature_results[0]["signature_page"],
            "evidence": {
                "signatures": signature_results
            }
        }
import re

from .base import BaseRule


class SignatureRule(BaseRule):

    rule_id = 6
    rule_name = "Signature Block Validation"

    def check(self, document):

        full_text = document["full_text"]

        # --------------------------------
        # Signature keywords
        # --------------------------------

        signature_keywords = [
            r"\bsignature\b",
            r"\bsigned\s+by\b",
            r"\bapproved\s+by\b",
            r"\bapproved\s+signature\b",
            r"\breviewed\s+by\b",
            r"\bprepared\s+by\b"
        ]

        # --------------------------------
        # Signature line patterns
        # --------------------------------

        signature_line_patterns = [
            r"_{3,}",
            r"\.{3,}",
            r"-{3,}"
        ]

        found_keywords = []

        for pattern in signature_keywords:

            matches = re.findall(
                pattern,
                full_text,
                re.IGNORECASE
            )

            found_keywords.extend(matches)

        found_lines = []

        for pattern in signature_line_patterns:

            matches = re.findall(
                pattern,
                full_text
            )

            found_lines.extend(matches)

        # --------------------------------
        # Determine whether signature block exists
        # --------------------------------

        if found_keywords and found_lines:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "PASS",
                "message": "Signature block detected.",
                "evidence": {
                    "signature_keywords": found_keywords,
                    "signature_lines": found_lines
                }
            }

        # --------------------------------
        # Keyword without line
        # --------------------------------

        if found_keywords:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "WARNING",
                "message": "Signature-related text found, but a signature line was not detected.",
                "evidence": {
                    "signature_keywords": found_keywords,
                    "signature_lines": found_lines
                }
            }

        # --------------------------------
        # Nothing found
        # --------------------------------

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "FAIL",
            "message": "No signature block detected.",
            "evidence": {
                "signature_keywords": [],
                "signature_lines": []
            }
        }
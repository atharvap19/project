import re

from .base import BaseRule


class RevisionSectionRule(BaseRule):

    rule_id = 5
    rule_name = "Revision Section Validation"

    def check(self, document):

        full_text = document["full_text"]

        patterns = [
            r"\brevision\s+history\b",
            r"\brevision\s+record\b",
            r"\brevision\s+log\b",
            r"\bdocument\s+history\b",
            r"\bchange\s+history\b"
        ]

        found_section = None

        for pattern in patterns:

            match = re.search(
                pattern,
                full_text,
                re.IGNORECASE
            )

            if match:
                found_section = match.group(0)
                break

        if found_section:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "PASS",
                "message": "Revision section is present.",
                "evidence": {
                    "section": found_section
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "FAIL",
            "message": "Revision section is missing.",
            "evidence": {
                "expected_sections": [
                    "Revision History",
                    "Revision Record",
                    "Revision Log",
                    "Document History",
                    "Change History"
                ]
            }
        }
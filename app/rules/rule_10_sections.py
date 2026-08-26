import re

from .base import BaseRule


class RequiredSectionsRule(BaseRule):

    rule_id = 10
    rule_name = "Required Sections Validation"

    def check(self, document):

        full_text = document.get("full_text", "")

        # --------------------------------
        # Required sections
        # --------------------------------

        required_sections = [
            "objective",
            "scope"
        ]

        found_sections = []
        missing_sections = []

        # --------------------------------
        # Check each section
        # --------------------------------

        for section in required_sections:

            pattern = rf"\b{re.escape(section)}\b"

            if re.search(
                pattern,
                full_text,
                re.IGNORECASE
            ):
                found_sections.append(section)
            else:
                missing_sections.append(section)

        # --------------------------------
        # Final result
        # --------------------------------

        if missing_sections:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "One or more required sections are missing.",
                "evidence": {
                    "found_sections": found_sections,
                    "missing_sections": missing_sections
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": "All required sections are present.",
            "evidence": {
                "found_sections": found_sections,
                "missing_sections": []
            }
        }
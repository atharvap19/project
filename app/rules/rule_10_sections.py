import re

from .base import BaseRule


class RequiredSectionsRule(BaseRule):

    rule_id = 10
    rule_name = "Required Sections Validation"

    REQUIRED_SECTIONS = [
        "Objective",
        "Scope"
    ]

    def find_section(self, section_name, document):

        pattern = rf"\b{re.escape(section_name)}\b"

        for page in document["pages"]:

            page_number = page["page_number"]
            page_text = page.get("text", "")

            match = re.search(
                pattern,
                page_text,
                re.IGNORECASE
            )

            if match:

                return {
                    "section": section_name,
                    "page": page_number,
                    "text": match.group(0)
                }

        return None

    def check(self, document):

        found_sections = []
        missing_sections = []

        # -----------------------------------------
        # Check required sections
        # -----------------------------------------

        for section in self.REQUIRED_SECTIONS:

            result = self.find_section(
                section,
                document
            )

            if result:

                found_sections.append(result)

            else:

                missing_sections.append(section)

        # -----------------------------------------
        # Missing sections
        # -----------------------------------------

        if missing_sections:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": (
                    "One or more required sections "
                    "are missing."
                ),
                "page": (
                    found_sections[0]["page"]
                    if found_sections
                    else None
                ),
                "evidence": {
                    "found_sections": found_sections,
                    "missing_sections": missing_sections
                }
            }

        # -----------------------------------------
        # All sections found
        # -----------------------------------------

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": (
                "All required sections are present."
            ),
            "page": found_sections[0]["page"],
            "evidence": {
                "found_sections": found_sections,
                "missing_sections": []
            }
        }
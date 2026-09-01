import re

from .base import BaseRule


class RevisionSectionRule(BaseRule):

    rule_id = 5
    rule_name = "Revision Section Validation"

    REVISION_LABELS = [
        "revision history",
        "revision record",
        "document history",
        "change history",
        "revision"
    ]

    def check(self, document):

        for page in document["pages"]:

            page_number = page["page_number"]
            page_text = page.get("text", "")

            for label in self.REVISION_LABELS:

                match = re.search(
                    rf"\b{re.escape(label)}\b",
                    page_text,
                    re.IGNORECASE
                )

                if match:

                    return {
                        "rule_id": self.rule_id,
                        "rule_name": self.rule_name,
                        "status": "PASS",
                        "message": "Revision section is present.",
                        "page": page_number,
                        "evidence": {
                            "section": match.group(0),
                            "page": page_number
                        }
                    }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "FAIL",
            "message": "Revision section is missing.",
            "page": None,
            "evidence": {
                "section": None
            }
        }
import re

from .base import BaseRule


class SignatureRule(BaseRule):

    rule_id = 6
    rule_name = "Signature Block Validation"

    SIGNATURE_LABELS = [
        "signature",
        "signed by",
        "approved by",
        "reviewed by",
        "prepared by"
    ]

    SIGNATURE_LINE_PATTERN = r"_{3,}"

    def find_signature(self, text):

        # Check for signature-related labels
        for label in self.SIGNATURE_LABELS:

            match = re.search(
                rf"\b{re.escape(label)}\b",
                text,
                re.IGNORECASE
            )

            if match:
                return {
                    "type": "label",
                    "text": match.group(0),
                    "position": match.start()
                }

        # Check for signature lines
        match = re.search(
            self.SIGNATURE_LINE_PATTERN,
            text
        )

        if match:
            return {
                "type": "signature_line",
                "text": match.group(0),
                "position": match.start()
            }

        return None

    def check(self, document):

        signatures = []

        for page in document["pages"]:

            page_number = page["page_number"]
            page_text = page.get("text", "")

            result = self.find_signature(
                page_text
            )

            if result:

                signatures.append({
                    "type": result["type"],
                    "text": result["text"],
                    "page": page_number
                })

        if signatures:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "PASS",
                "message": "Signature block detected.",
                "page": signatures[0]["page"],
                "evidence": {
                    "signatures": signatures
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "FAIL",
            "message": "Signature block was not detected.",
            "page": None,
            "evidence": {
                "signatures": []
            }
        }
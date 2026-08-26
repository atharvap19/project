import re

from .base import BaseRule


class VersionRule(BaseRule):

    rule_id = 4
    rule_name = "Version Number Validation"

    def check(self, document):

        filename = document["filename"]
        full_text = document["full_text"]

        # --------------------------------
        # 1. Find version in filename
        # --------------------------------

        filename_version = self.extract_version(filename)

        if not filename_version:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Version number not found in filename.",
                "evidence": {}
            }

        # --------------------------------
        # 2. Get first page
        # --------------------------------

        first_page_text = document["pages"][0]["text"]

        first_page_version = self.extract_version(
            first_page_text
        )

        # --------------------------------
        # 3. Find revision history
        # --------------------------------

        revision_match = re.search(
            r"revision\s+history",
            full_text,
            re.IGNORECASE
        )

        revision_version = None

        if revision_match:

            revision_text = full_text[
                revision_match.end():
            ]

            revision_version = self.extract_version(
                revision_text
            )

        # --------------------------------
        # 4. Check all locations
        # --------------------------------

        missing = []

        if not first_page_version:
            missing.append("first page")

        if not revision_version:
            missing.append("revision history")

        if missing:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Version number is missing from required location(s).",
                "evidence": {
                    "filename_version": filename_version,
                    "first_page_version": first_page_version,
                    "revision_version": revision_version,
                    "missing": missing
                }
            }

        # --------------------------------
        # 5. Compare versions
        # --------------------------------

        mismatches = []

        if first_page_version != filename_version:
            mismatches.append("first page")

        if revision_version != filename_version:
            mismatches.append("revision history")

        # --------------------------------
        # 6. Final result
        # --------------------------------

        if mismatches:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Version numbers do not match.",
                "evidence": {
                    "filename_version": filename_version,
                    "first_page_version": first_page_version,
                    "revision_version": revision_version,
                    "mismatches": mismatches
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": "Version number is consistent across all required locations.",
            "evidence": {
                "filename_version": filename_version,
                "first_page_version": first_page_version,
                "revision_version": revision_version
            }
        }

    # --------------------------------
    # Extract version
    # --------------------------------

    def extract_version(self, text):

        patterns = [
            r"\bversion\s*[:\-]?\s*v?(\d+(?:\.\d+)*)\b",
            r"\brev(?:ision)?\s*[:\-]?\s*v?(\d+(?:\.\d+)*)\b",
            r"\bv(\d+(?:\.\d+)*)\b"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(1)

        return None
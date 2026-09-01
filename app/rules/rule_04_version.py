import re

from .base import BaseRule


class VersionRule(BaseRule):

    rule_id = 4
    rule_name = "Version Number Validation"

    VERSION_PATTERN = r"\b(?:version|ver\.?)\s*[:\-]?\s*(\d+(?:\.\d+)*)\b"

    REVISION_LABELS = [
        "revision history",
        "revision record",
        "document history",
        "change history",
        "revision"
    ]

    def find_versions(self, text):

        matches = re.findall(
            self.VERSION_PATTERN,
            text,
            re.IGNORECASE
        )

        return matches

    def check(self, document):

        first_page_text = document["pages"][0].get(
            "text",
            ""
        )

        # -----------------------------------------
        # Find versions on first page
        # -----------------------------------------

        first_page_versions = self.find_versions(
            first_page_text
        )

        if not first_page_versions:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Version number not found on the first page.",
                "page": 1,
                "evidence": {
                    "first_page": None,
                    "revision_history": None
                }
            }

        # Use the first version found as the expected version
        expected_version = first_page_versions[0]

        first_page_evidence = {
            "version": expected_version,
            "page": 1
        }

        # -----------------------------------------
        # Find revision history
        # -----------------------------------------

        revision_page = None
        revision_text = ""

        for page in document["pages"]:

            page_text = page.get("text", "")

            for label in self.REVISION_LABELS:

                if re.search(
                    rf"\b{re.escape(label)}\b",
                    page_text,
                    re.IGNORECASE
                ):

                    revision_page = page["page_number"]
                    revision_text = page_text
                    break

            if revision_page:
                break

        if revision_page is None:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Revision history section was not found.",
                "page": 1,
                "evidence": {
                    "first_page": first_page_evidence,
                    "revision_history": None
                }
            }

        # -----------------------------------------
        # Check version in revision history
        # -----------------------------------------

        revision_versions = self.find_versions(
            revision_text
        )

        matching_revision_version = None

        for version in revision_versions:

            if version == expected_version:
                matching_revision_version = version
                break

        if matching_revision_version is None:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": (
                    f"Version {expected_version} was found on "
                    "the first page but not in the revision history."
                ),
                "page": revision_page,
                "evidence": {
                    "expected_version": expected_version,
                    "first_page": first_page_evidence,
                    "revision_history": {
                        "page": revision_page,
                        "versions_found": revision_versions
                    }
                }
            }

        # -----------------------------------------
        # Title check
        # -----------------------------------------

        # Try to identify the title on the first page.
        # We check whether the expected version appears
        # somewhere on the first page as required.

        title_has_version = (
            expected_version in first_page_text
        )

        if not title_has_version:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": (
                    f"Version {expected_version} is not "
                    "present in the first-page title."
                ),
                "page": 1,
                "evidence": {
                    "expected_version": expected_version,
                    "first_page": first_page_evidence,
                    "revision_history": {
                        "page": revision_page,
                        "version": matching_revision_version
                    }
                }
            }

        # -----------------------------------------
        # PASS
        # -----------------------------------------

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": (
                f"Version {expected_version} is present in "
                "the title, first page, and revision history."
            ),
            "page": 1,
            "evidence": {
                "version": expected_version,

                "title": {
                    "page": 1,
                    "version": expected_version
                },

                "first_page": {
                    "page": 1,
                    "version": expected_version
                },

                "revision_history": {
                    "page": revision_page,
                    "version": matching_revision_version
                }
            }
        }
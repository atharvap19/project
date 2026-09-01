import re
from pathlib import Path

from rapidfuzz.fuzz import ratio

from .base import BaseRule


class TitleRule(BaseRule):

    rule_id = 1
    rule_name = "Title Rule"

    def normalize(self, text):
        text = text.lower()

        # Remove special characters
        text = re.sub(r"[^a-z0-9\s]", "", text)

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def check(self, document):

        # -----------------------------------------
        # 1. Get expected title from filename
        # -----------------------------------------

        filename = Path(
            document["filename"]
        ).stem

        expected_title = self.normalize(
            filename
        )

        # -----------------------------------------
        # 2. Check every page
        # -----------------------------------------

        best_score = 0
        best_match = None
        best_page = None

        for page in document["pages"]:

            page_number = page["page_number"]
            page_text = page.get("text", "")

            # -------------------------------------
            # Exact match on this page
            # -------------------------------------

            normalized_page = self.normalize(
                page_text
            )

            if expected_title in normalized_page:

                return {
                    "rule_id": self.rule_id,
                    "rule_name": self.rule_name,
                    "status": (
                        "PASS"
                        if page_number == 1
                        else "WARNING"
                    ),
                    "message": (
                        "Document title matches the filename "
                        "and is present on Page 1."
                        if page_number == 1
                        else
                        f"Document title matches the filename "
                        f"but was found on Page {page_number}, "
                        "not Page 1."
                    ),
                    "page": page_number,
                    "evidence": {
                        "expected": expected_title,
                        "found": expected_title,
                        "similarity": 100,
                        "page": page_number
                    }
                }

            # -------------------------------------
            # Fuzzy matching
            # -------------------------------------

            for line in page_text.splitlines():

                line = line.strip()

                if not line:
                    continue

                normalized_line = self.normalize(
                    line
                )

                score = ratio(
                    expected_title,
                    normalized_line
                )

                if score > best_score:

                    best_score = score
                    best_match = line
                    best_page = page_number

        # -----------------------------------------
        # 3. Fuzzy match found
        # -----------------------------------------

        if best_score >= 85:

            if best_page == 1:

                return {
                    "rule_id": self.rule_id,
                    "rule_name": self.rule_name,
                    "status": "PASS",
                    "message": (
                        "Document title closely matches "
                        "the filename and is present on Page 1."
                    ),
                    "page": 1,
                    "evidence": {
                        "expected": expected_title,
                        "found": best_match,
                        "similarity": best_score,
                        "page": best_page
                    }
                }

            else:

                return {
                    "rule_id": self.rule_id,
                    "rule_name": self.rule_name,
                    "status": "WARNING",
                    "message": (
                        f"Document title closely matches "
                        f"the filename but was found on "
                        f"Page {best_page}, not Page 1."
                    ),
                    "page": best_page,
                    "evidence": {
                        "expected": expected_title,
                        "found": best_match,
                        "similarity": best_score,
                        "page": best_page
                    }
                }

        # -----------------------------------------
        # 4. No title found
        # -----------------------------------------

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "FAIL",
            "message": (
                "Document title matching the filename "
                "was not found."
            ),
            "page": None,
            "evidence": {
                "expected": expected_title,
                "found": best_match,
                "similarity": best_score,
                "page": best_page
            }
        }
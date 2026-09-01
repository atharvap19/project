import re

from .base import BaseRule


class AuthorRule(BaseRule):

    rule_id = 2
    rule_name = "Author and Role Validation"

    AUTHOR_LABELS = [
        "author",
        "author name",
        "document author",
        "prepared by",
        "written by",
        "created by",
        "developed by"
    ]

    ROLE_LABELS = [
        "role",
        "author role",
        "job role",
        "designation",
        "position",
        "job title",
        "title"
    ]

    def find_label_value(self, text, labels):

        for label in labels:

            pattern = rf"\b{re.escape(label)}\s*[:\-]\s*(.+)"

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                value = match.group(1).strip()

                if value:
                    return {
                        "label": label,
                        "value": value,
                        "source": "text"
                    }

        return None

    def normalize_cell(self, text):
        """
        A table cell reduced to its label, without trailing punctuation.
        """

        cleaned = (text or "").strip()

        cleaned = re.sub(r"[:\-\s]+$", "", cleaned)

        return cleaned.strip().lower()

    def value_for_label(self, rows, row_index, cell_index):
        """
        The value paired with a label cell.

        Two layouts are common:

            Author | John Smith     value sits to the right

            Author                  value sits below, when the label is a
            John Smith              column heading
        """

        row = rows[row_index]

        # A label in the first row of a wide, multi-row table is a column
        # heading, so the value is underneath rather than beside it.
        # Without this, an "Author" column in a revision-history table would
        # return the next heading instead of a name.
        if row_index == 0 and len(rows) > 1 and len(row) > 2:

            below = rows[1]

            if cell_index < len(below):

                value = (below[cell_index] or "").strip()

                if value:
                    return value

        for value in row[cell_index + 1:]:

            value = (value or "").strip()

            if value:
                return value

        return None

    def find_label_in_tables(self, tables, labels):
        """
        Look for a "label | value" pair in a table row.

        Documents often put this information in a table rather than writing
        "Author: name", which leaves no colon for find_label_value to match.

        The label cell has to match exactly: a loose match would let the role
        label "title" pick up the value from a "Document Title" row.
        """

        for label in labels:

            for table in tables:

                rows = table.get("rows", [])

                for row_index, row in enumerate(rows):

                    for cell_index, cell in enumerate(row):

                        if self.normalize_cell(cell) != label:
                            continue

                        value = self.value_for_label(
                            rows,
                            row_index,
                            cell_index
                        )

                        if value:
                            return {
                                "label": label,
                                "value": value,
                                "page": table.get("page"),
                                "source": "table"
                            }

        return None

    def check(self, document):

        author_found = None
        role_found = None

        # Search the entire document
        # while keeping the page where the information was found.

        for page in document["pages"]:

            page_number = page["page_number"]
            page_text = page.get("text", "")

            # Find author
            if author_found is None:

                result = self.find_label_value(
                    page_text,
                    self.AUTHOR_LABELS
                )

                if result:
                    author_found = {
                        **result,
                        "page": page_number
                    }

            # Find role
            if role_found is None:

                result = self.find_label_value(
                    page_text,
                    self.ROLE_LABELS
                )

                if result:
                    role_found = {
                        **result,
                        "page": page_number
                    }

            if author_found and role_found:
                break

        # Nothing written as "Author: name" in the running text, so fall back
        # to label/value pairs in the document's tables.

        tables = document.get("tables", [])

        if author_found is None:

            author_found = self.find_label_in_tables(
                tables,
                self.AUTHOR_LABELS
            )

        if role_found is None:

            role_found = self.find_label_in_tables(
                tables,
                self.ROLE_LABELS
            )

        # Both found
        if author_found and role_found:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "PASS",
                "message": "Author name and role are present.",
                "page": author_found["page"],
                "evidence": {
                    "author": author_found,
                    "role": role_found
                }
            }

        # Author found, role missing
        if author_found and not role_found:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Author name was found, but role is missing.",
                "page": author_found["page"],
                "evidence": {
                    "author": author_found,
                    "role": None
                }
            }

        # Role found, author missing
        if not author_found and role_found:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "Role was found, but author name is missing.",
                "page": role_found["page"],
                "evidence": {
                    "author": None,
                    "role": role_found
                }
            }

        # Neither found
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "FAIL",
            "message": "Required author information is missing.",
            "page": None,
            "evidence": {
                "author": None,
                "role": None
            }
        }
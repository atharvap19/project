import language_tool_python

from .base import BaseRule


class LanguageRule(BaseRule):

    rule_id = 9
    rule_name = "Language Validation"

    def check(self, document):

        text = document.get(
            "full_text",
            ""
        )

        if not text.strip():

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "ERROR",
                "message": "No document text was available.",
                "page": None,
                "evidence": {}
            }

        try:

            tool = language_tool_python.LanguageTool(
                "en-US"
            )

            matches = tool.check(text)

            errors = []

            for match in matches:

                # Get the text that caused the issue
                offset = match.offset
                length = match.error_length

                original = text[
                    offset: offset + length
                ]

                suggestions = match.replacements

                errors.append({
                    "message": match.message,
                    "original": original,
                    "suggestions": suggestions,
                    "offset": offset
                })

            tool.close()

        except Exception as e:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "ERROR",
                "message": f"Language check failed: {str(e)}",
                "page": None,
                "evidence": {}
            }

        # -----------------------------------------
        # No errors
        # -----------------------------------------

        if not errors:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "PASS",
                "message": "No significant language errors were detected.",
                "page": None,
                "evidence": {
                    "errors": []
                }
            }

        # -----------------------------------------
        # Errors found
        # -----------------------------------------

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "WARNING",
            "message": (
                f"{len(errors)} language issue(s) detected."
            ),
            "page": None,
            "evidence": {
                "errors": errors
            }
        }
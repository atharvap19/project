import language_tool_python

from .base import BaseRule


class LanguageRule(BaseRule):

    rule_id = 9
    rule_name = "Language Validation"

    def check(self, document):

        full_text = document.get("full_text", "")

        if not full_text.strip():

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "WARNING",
                "message": "No text was available for language checking.",
                "evidence": {}
            }

        # --------------------------------
        # Start LanguageTool
        # --------------------------------

        tool = language_tool_python.LanguageTool(
            "en-US"
        )

        # --------------------------------
        # Find language errors
        # --------------------------------

        matches = tool.check(full_text)

        # --------------------------------
        # Collect errors
        # --------------------------------

        errors = []

        for match in matches:

            errors.append({
                "message": match.message,
                "suggestions": match.replacements[:5],
                "context": match.context,
                "offset": match.offset,
                "length": match.errorLength
            })

        # --------------------------------
        # Close LanguageTool
        # --------------------------------

        tool.close()

        # --------------------------------
        # Decide result
        # --------------------------------

        if errors:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": f"{len(errors)} language issue(s) detected.",
                "evidence": {
                    "error_count": len(errors),
                    "errors": errors
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": "No language errors were detected.",
            "evidence": {
                "error_count": 0,
                "errors": []
            }
        }
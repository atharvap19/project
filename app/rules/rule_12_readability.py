import textstat

from .base import BaseRule


class ReadabilityRule(BaseRule):

    rule_id = 12
    rule_name = "Readability Validation"

    def check(self, document):

        full_text = document.get("full_text", "")

        if not full_text.strip():

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "WARNING",
                "message": "No text was available for readability analysis.",
                "evidence": {}
            }

        # --------------------------------
        # Calculate readability
        # --------------------------------

        reading_score = textstat.flesch_reading_ease(
            full_text
        )

        grade_level = textstat.flesch_kincaid_grade(
            full_text
        )

        avg_sentence_length = (
            textstat.words_per_sentence(
                full_text
            )
        )

        avg_word_length = (
            textstat.avg_letter_per_word(
                full_text
            )
        )

        # --------------------------------
        # Determine readability
        # --------------------------------

        if reading_score >= 60:

            status = "PASS"

            message = (
                "Document has a generally good "
                "readability level."
            )

        elif reading_score >= 40:

            status = "WARNING"

            message = (
                "Document may be moderately difficult "
                "to read."
            )

        else:

            status = "FAIL"

            message = (
                "Document may be difficult to read."
            )

        # --------------------------------
        # Return result
        # --------------------------------

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": status,
            "message": message,
            "evidence": {
                "flesch_reading_ease": round(
                    reading_score,
                    2
                ),
                "flesch_kincaid_grade": round(
                    grade_level,
                    2
                ),
                "average_sentence_length": round(
                    avg_sentence_length,
                    2
                ),
                "average_word_length": round(
                    avg_word_length,
                    2
                )
            }
        }
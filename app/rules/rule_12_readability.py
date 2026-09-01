import re
import textstat

from .base import BaseRule


class ReadabilityRule(BaseRule):

    rule_id = 12
    rule_name = "Readability Validation"

    def split_sentences(self, text):

        sentences = re.split(
            r"[.!?]+",
            text
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def average_sentence_length(self, text):

        sentences = self.split_sentences(text)

        if not sentences:
            return 0

        total_words = sum(
            len(sentence.split())
            for sentence in sentences
        )

        return total_words / len(sentences)

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

        # -----------------------------------------
        # Readability metrics
        # -----------------------------------------

        try:

            sentence_length = (
                self.average_sentence_length(text)
            )

            word_count = len(
                text.split()
            )

            syllable_count = textstat.syllable_count(
                text
            )

            readability_score = (
                textstat.flesch_reading_ease(text)
            )

        except Exception as e:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "ERROR",
                "message": (
                    f"Readability analysis failed: {str(e)}"
                ),
                "page": None,
                "evidence": {}
            }

        # -----------------------------------------
        # Basic thresholds
        # -----------------------------------------

        issues = []

        # Long average sentence
        if sentence_length > 30:

            issues.append({
                "type": "sentence_length",
                "message": (
                    "Average sentence length is "
                    "greater than 30 words."
                ),
                "value": sentence_length
            })

        # Very low readability score
        if readability_score < 30:

            issues.append({
                "type": "readability",
                "message": (
                    "The document has a low "
                    "readability score."
                ),
                "value": readability_score
            })

        # -----------------------------------------
        # WARNING
        # -----------------------------------------

        if issues:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "WARNING",
                "message": (
                    "Document may be difficult to read."
                ),
                "page": None,
                "evidence": {
                    "average_sentence_length": round(
                        sentence_length,
                        2
                    ),
                    "word_count": word_count,
                    "syllable_count": syllable_count,
                    "flesch_reading_ease": round(
                        readability_score,
                        2
                    ),
                    "issues": issues
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
                "Document readability is acceptable."
            ),
            "page": None,
            "evidence": {
                "average_sentence_length": round(
                    sentence_length,
                    2
                ),
                "word_count": word_count,
                "syllable_count": syllable_count,
                "flesch_reading_ease": round(
                    readability_score,
                    2
                ),
                "issues": []
            }
        }
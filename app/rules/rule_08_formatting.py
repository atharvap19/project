from collections import Counter

from .base import BaseRule


class FormattingRule(BaseRule):

    rule_id = 8
    rule_name = "Font and Spacing Consistency"

    def check(self, document):

        spans = document.get("spans", [])

        if not spans:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "WARNING",
                "message": "No font information was available.",
                "evidence": {}
            }

        # --------------------------------
        # Collect font information
        # --------------------------------

        fonts = []
        font_sizes = []

        for span in spans:

            if span.get("font"):
                fonts.append(span["font"])

            if span.get("size"):
                font_sizes.append(round(span["size"], 1))

        # --------------------------------
        # Find most common font
        # --------------------------------

        font_counts = Counter(fonts)

        dominant_font = (
            font_counts.most_common(1)[0][0]
            if font_counts
            else None
        )

        # --------------------------------
        # Find most common font size
        # --------------------------------

        size_counts = Counter(font_sizes)

        dominant_size = (
            size_counts.most_common(1)[0][0]
            if size_counts
            else None
        )

        # --------------------------------
        # Find font inconsistencies
        # --------------------------------

        font_inconsistencies = []

        for font, count in font_counts.items():

            if font != dominant_font:

                font_inconsistencies.append({
                    "font": font,
                    "count": count
                })

        # --------------------------------
        # Find size inconsistencies
        # --------------------------------

        size_inconsistencies = []

        for size, count in size_counts.items():

            if size != dominant_size:

                size_inconsistencies.append({
                    "size": size,
                    "count": count
                })

        # --------------------------------
        # Calculate percentage
        # --------------------------------

        total_spans = len(spans)

        dominant_font_count = font_counts.get(
            dominant_font,
            0
        )

        dominant_percentage = (
            dominant_font_count / total_spans
        ) * 100

        # --------------------------------
        # Decide result
        # --------------------------------

        # Allow some variation because
        # headings/titles naturally differ.
        if dominant_percentage >= 80:

            status = "PASS"
            message = "Font formatting is reasonably consistent."

        else:

            status = "WARNING"
            message = "Significant font inconsistencies were detected."

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": status,
            "message": message,
            "evidence": {
                "dominant_font": dominant_font,
                "dominant_font_percentage": round(
                    dominant_percentage,
                    2
                ),
                "dominant_font_size": dominant_size,
                "font_variations": font_inconsistencies,
                "font_size_variations": size_inconsistencies
            }
        }
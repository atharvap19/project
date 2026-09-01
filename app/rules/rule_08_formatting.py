from collections import Counter

from .base import BaseRule


class FormattingRule(BaseRule):

    rule_id = 8
    rule_name = "Font and Spacing Consistency"

    # Rendered leading varies by a fraction of a point between lines that are
    # set identically, so only a clear step counts as an inconsistency.
    SPACING_TOLERANCE_RATIO = 0.15
    SPACING_TOLERANCE_MINIMUM = 1.0

    def dominant_spacing(self, items):
        """
        The most common line spacing across body text.

        Spacing is None on the first line of a paragraph, where the gap is
        paragraph spacing rather than leading, so those are skipped.
        """

        counts = Counter(
            item["line_spacing"]
            for item in items
            if item.get("line_spacing") is not None
        )

        if not counts:
            return None

        return counts.most_common(1)[0][0]

    def summarise(self, inconsistencies):
        """
        Say which of font and spacing was actually inconsistent.
        """

        issues = [
            issue
            for item in inconsistencies
            for issue in item["issues"]
        ]

        fonts = any(not issue.startswith("Line spacing") for issue in issues)
        spacing = any(issue.startswith("Line spacing") for issue in issues)

        if fonts and spacing:
            return "Significant font and spacing inconsistencies were detected."

        if spacing:
            return "Significant line spacing inconsistencies were detected."

        return "Significant font inconsistencies were detected."

    def spacing_differs(self, spacing, dominant):
        """
        True when a line's spacing is far enough from the norm to report.
        """

        if spacing is None or not dominant:
            return False

        tolerance = max(
            self.SPACING_TOLERANCE_MINIMUM,
            dominant * self.SPACING_TOLERANCE_RATIO
        )

        return abs(spacing - dominant) > tolerance

    def check(self, document):

        formatting_data = document.get("formatting", [])

        # If formatting information is not available yet
        if not formatting_data:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "ERROR",
                "message": (
                    "Font and spacing information is not "
                    "available from the document extractor."
                ),
                "page": None,
                "evidence": {
                    "formatting": []
                }
            }

        # -----------------------------------------
        # Count font usage
        # -----------------------------------------

        fonts = [
            item.get("font_name")
            for item in formatting_data
            if item.get("font_name")
        ]

        font_sizes = [
            item.get("font_size")
            for item in formatting_data
            if item.get("font_size")
        ]

        font_counts = Counter(fonts)
        size_counts = Counter(font_sizes)

        # Most common font and size
        dominant_font = (
            font_counts.most_common(1)[0][0]
            if font_counts
            else None
        )

        dominant_size = (
            size_counts.most_common(1)[0][0]
            if size_counts
            else None
        )

        # Body text only: headings are meant to differ.
        body_items = [
            item
            for item in formatting_data
            if item.get("type", "body") not in (
                "title",
                "heading",
                "header",
                "footer"
            )
        ]

        dominant_line_spacing = self.dominant_spacing(body_items)

        inconsistencies = []

        # -----------------------------------------
        # Find significant inconsistencies
        # -----------------------------------------

        for item in formatting_data:

            font_name = item.get("font_name")
            font_size = item.get("font_size")
            line_spacing = item.get("line_spacing")

            # Ignore headings/titles if marked as such
            element_type = item.get(
                "type",
                "body"
            )

            if element_type in [
                "title",
                "heading",
                "header",
                "footer"
            ]:
                continue

            problems = []

            if (
                dominant_font
                and font_name
                and font_name != dominant_font
            ):
                problems.append(
                    f"Font '{font_name}' differs from "
                    f"dominant font '{dominant_font}'"
                )

            if (
                dominant_size
                and font_size
                and font_size != dominant_size
            ):
                problems.append(
                    f"Font size {font_size} differs from "
                    f"dominant size {dominant_size}"
                )

            if self.spacing_differs(line_spacing, dominant_line_spacing):
                problems.append(
                    f"Line spacing {line_spacing} differs from "
                    f"dominant spacing {dominant_line_spacing}"
                )

            if problems:

                inconsistencies.append({
                    "page": item.get("page"),
                    "paragraph": item.get("paragraph"),
                    "line": item.get("line"),
                    "font_name": font_name,
                    "font_size": font_size,
                    "line_spacing": line_spacing,
                    "issues": problems
                })

        # -----------------------------------------
        # Result
        # -----------------------------------------

        if inconsistencies:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "WARNING",
                "message": self.summarise(inconsistencies),
                "page": inconsistencies[0].get("page"),
                "evidence": {
                    "dominant_font": dominant_font,
                    "dominant_font_size": dominant_size,
                    "dominant_line_spacing": dominant_line_spacing,
                    "inconsistencies": inconsistencies
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": (
                "Font and spacing are generally consistent."
            ),
            "page": None,
            "evidence": {
                "dominant_font": dominant_font,
                "dominant_font_size": dominant_size,
                "dominant_line_spacing": dominant_line_spacing,
                "inconsistencies": []
            }
        }
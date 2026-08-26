import re
import math

from .base import BaseRule


class SignatureDateRule(BaseRule):

    rule_id = 7
    rule_name = "Signature Date Validation"

    def check(self, document):

        signatures = document.get("signatures", [])
        dates = document.get("dates", [])

        # --------------------------------
        # No signatures found
        # --------------------------------

        if not signatures:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "WARNING",
                "message": "No signature blocks were found to check.",
                "evidence": {
                    "signatures": 0,
                    "dates": 0
                }
            }

        # --------------------------------
        # No dates found
        # --------------------------------

        if not dates:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "No dates were found near the signature blocks.",
                "evidence": {
                    "signatures": len(signatures),
                    "dates": 0
                }
            }

        matched_signatures = []
        unmatched_signatures = []

        # --------------------------------
        # Compare signatures and dates
        # --------------------------------

        for signature in signatures:

            signature_x = signature["x"]
            signature_y = signature["y"]
            signature_page = signature["page"]

            closest_date = None
            closest_distance = float("inf")

            for date in dates:

                # Date must be on same page
                if date["page"] != signature_page:
                    continue

                date_x = date["x"]
                date_y = date["y"]

                distance = math.sqrt(
                    (signature_x - date_x) ** 2 +
                    (signature_y - date_y) ** 2
                )

                if distance < closest_distance:

                    closest_distance = distance
                    closest_date = date

            # --------------------------------
            # Distance threshold
            # --------------------------------

            if closest_date and closest_distance <= 100:

                matched_signatures.append({
                    "signature_page": signature_page,
                    "date": closest_date["text"],
                    "distance": round(
                        closest_distance,
                        2
                    )
                })

            else:

                unmatched_signatures.append({
                    "signature_page": signature_page,
                    "closest_date": (
                        closest_date["text"]
                        if closest_date
                        else None
                    ),
                    "distance": (
                        round(closest_distance, 2)
                        if closest_date
                        else None
                    )
                })

        # --------------------------------
        # Final result
        # --------------------------------

        if unmatched_signatures:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "FAIL",
                "message": "One or more signatures do not have a nearby date.",
                "evidence": {
                    "matched": matched_signatures,
                    "unmatched": unmatched_signatures
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "PASS",
            "message": "Dates were found near all signature blocks.",
            "evidence": {
                "matched": matched_signatures
            }
        }
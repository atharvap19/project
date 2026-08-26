import re


from pathlib import Path
from rapidfuzz.fuzz import ratio


from .base import BaseRule 

class TitleRule(BaseRule):
    rule_id = 1
    rule_name = "Title Rule"
    def normalize(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        #remove spacial characters 
        text = re.sub(r"[^a-z0-9\s]", "", text)
        #remove extra spaces
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def check(self, document):

    
        # 1. Get filename
        
        filename = Path(document["filename"]).stem
        expected_title = self.normalize(filename)

        # 2. Get first page text
        
        first_page_text = document["pages"][0]["text"]
        normalized_page = self.normalize(first_page_text)
        
        # 3. Check exact match
        if expected_title in normalized_page:
            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "PASS",
                "message": "Document title matches the filename.",
                "page": 1,
                "evidence": {
                    "expected": expected_title,
                    "found": expected_title
                }
            }

        # 4. Check fuzzy match
        best_score = 0
        best_match = None

        for line in first_page_text.splitlines():

            line = line.strip()

            if not line:
                continue

            normalized_line = self.normalize(line)

            score = ratio(
                expected_title,
                normalized_line
            )

            if score > best_score:
                best_score = score
                best_match = line

        if best_score >= 85:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "PASS",
                "message": "Document title closely matches the filename.",
                "page": 1,
                "evidence": {
                    "expected": expected_title,
                    "found": best_match,
                    "similarity": best_score
                }
            }

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "FAIL",
            "message": "Document title does not match the filename.",
            "page": 1,
            "evidence": {
                "expected": expected_title,
                "found": best_match,
                "similarity": best_score
            }
        }
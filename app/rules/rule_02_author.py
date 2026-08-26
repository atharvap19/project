import re

from .base import BaseRule


class AuthorRule(BaseRule):

    rule_id = 2
    rule_name = "Author and Role Validation"

    def check(self, document):

        full_text = document["full_text"]

        #patterns for author

        author_patterns = [
            r"\bauthor\s*:\s*(.+)",
            r"\bauthor\s+name\s*:\s*(.+)",
            r"\bprepared\s+by\s*:\s*(.+)",
            r"\bcreated\s+by\s*:\s*(.+)",
            r"\bdrafted\s+by\s*:\s*(.+)"
        ]

        
        # Patterns for role
        
        role_patterns = [
            r"\brole\s*:\s*(.+)",
            r"\bauthor\s+role\s*:\s*(.+)",
            r"\bdesignation\s*:\s*(.+)",
            r"\bposition\s*:\s*(.+)",
            r"\bjob\s+title\s*:\s*(.+)"
        ]

    
        # Find author
        
        author_match = None

        for pattern in author_patterns:

            match = re.search(
                pattern,
                full_text,
                re.IGNORECASE
            )

            if match:
                author_match = match.group(1).strip()
                break
       
        # Find role
        
        role_match = None

        for pattern in role_patterns:

            match = re.search(
                pattern,
                full_text,
                re.IGNORECASE
            )

            if match:
                role_match = match.group(1).strip()
                break


        # Determine result

        if author_match and role_match:

            return {
                "rule_id": self.rule_id,
                "rule_name": self.rule_name,
                "status": "PASS",
                "message": "Author name and role are present.",
                "evidence": {
                    "author": author_match,
                    "role": role_match
                }
            }

        # Missing information
 
        missing = []

        if not author_match:
            missing.append("author name")

        if not role_match:
            missing.append("author role")

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": "FAIL",
            "message": "Required author information is missing.",
            "evidence": {
                "author": author_match,
                "role": role_match,
                "missing": missing
            }
        }
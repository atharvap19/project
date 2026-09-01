"""Quick check of Rule 1 against a hand-built document.

The pages here match what the PDF extractor produces: each page needs a
page_number as well as text.
"""

from app.rules.rule_01_title import TitleRule


document = {
    "filename": "Employee_Onboarding_SOP.docx",
    "pages": [
        {
            "page_number": 1,
            "text": """
            STANDARD OPERATING PROCEDURE

            Employee Onboarding SOP

            Version: 1.0
            Author: John Smith
            """,
            "header": "",
            "footer": "Page 1 of 1"
        }
    ]
}


rule = TitleRule()

result = rule.check(document)

print(f"Rule {result['rule_id']} - {result['rule_name']}")
print(f"Status : {result['status']}")
print(f"Message: {result['message']}")
print(f"Evidence: {result['evidence']}")

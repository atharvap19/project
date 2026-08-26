from app.rules.rule_01_title import TitleRule


document = {
    "filename": "Employee_Onboarding_SOP.docx",
    "pages": [
        {
            "text": """
            STANDARD OPERATING PROCEDURE

            Employee Onboarding SOP

            Version: 1.0
            Author: John Smith
            """
        }
    ]
}


rule = TitleRule()

result = rule.check(document)

print(result)
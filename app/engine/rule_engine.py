from app.rules.rule_01_title import TitleRule
from app.rules.rule_02_author import AuthorRule
from app.rules.rule_03_revision_dates import RevisionDateRule
from app.rules.rule_04_version import VersionRule
from app.rules.rule_05_revision_section import RevisionSectionRule
from app.rules.rule_06_signature import SignatureRule
from app.rules.rule_07_signature_dates import SignatureDateRule
from app.rules.rule_08_formatting import FormattingRule
from app.rules.rule_09_language import LanguageRule
from app.rules.rule_10_sections import RequiredSectionsRule
from app.rules.rule_11_page_numbers import PageNumberRule
from app.rules.rule_12_readability import ReadabilityRule
from app.rules.rule_13_footer import FooterRule


class RuleEngine:

    def __init__(self):

        self.rules = [
            TitleRule(),
            AuthorRule(),
            RevisionDateRule(),
            VersionRule(),
            RevisionSectionRule(),
            SignatureRule(),
            SignatureDateRule(),
            FormattingRule(),
            LanguageRule(),
            RequiredSectionsRule(),
            PageNumberRule(),
            ReadabilityRule(),
            FooterRule()
        ]

    def run(self, document):

        results = []

        for rule in self.rules:

            try:

                result = rule.check(document)

                results.append(result)

            except Exception as e:

                results.append({
                    "rule_id": rule.rule_id,
                    "rule_name": rule.rule_name,
                    "status": "ERROR",
                    "message": f"Rule failed to execute: {str(e)}",
                    "evidence": {}
                })

        return results
class BaseRule:
    rule_id = None
    rule_name = ""

    def check(self, document):
        raise NotImplementedError
    
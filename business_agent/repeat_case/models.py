class RepeatCaseRequest:
    def __init__(self, problem_description=None, product=None, version=None, environment=None):
        self.problem_description = problem_description
        self.product = product
        self.version = version
        self.environment = environment


class RepeatCaseResult:
    def __init__(self, cases=None, recommendation=None, confidence=None):
        self.cases = cases or []
        self.recommendation = recommendation
        self.confidence = confidence

class RepeatCaseAgent:
    def __init__(self, knowledge=None):
        self.knowledge = knowledge

    def analyze(self, request):
        cases = []
        if self.knowledge:
            cases = self.knowledge.search(request.problem_description)

        return {
            "similar_cases": cases,
            "recommendation": "pending expert review",
            "confidence": "low"
        }

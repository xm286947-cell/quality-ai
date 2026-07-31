from .state import WorkflowState

class WorkflowExecutor:
    def __init__(self, agent_executor=None):
        self.agent_executor = agent_executor

    def execute(self, workflow, context):
        workflow.state = WorkflowState.RUNNING

        results = []
        try:
            for step in workflow.definition.steps:
                result = self.agent_executor.execute(
                    step.agent,
                    context
                )
                results.append(result)

            workflow.result = results
            workflow.state = WorkflowState.COMPLETED
            return results

        except Exception:
            workflow.state = WorkflowState.FAILED
            raise

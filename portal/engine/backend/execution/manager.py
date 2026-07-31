from .models import Execution

_executions = {}

def create_execution(request_id, agent_id, input_data):
    execution = Execution(
        request_id=request_id,
        agent_id=agent_id,
        input=input_data
    )
    _executions[request_id] = execution
    return execution

def get_execution(request_id):
    return _executions.get(request_id)

def update_status(request_id, status, output=None):
    execution = _executions[request_id]
    execution.status = status
    if output:
        execution.output = output
    return execution

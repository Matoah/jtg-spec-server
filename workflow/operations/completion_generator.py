from completeions.spec_expert import SpecExpertCompletion
from workflow.state.workflow_state import WorkflowState


def completion_generator(state: WorkflowState):
    """
    完成生成器
    """
    completion = SpecExpertCompletion(state.documents)
    result = completion.ask(state.query)
    return {
        "content": result
    }

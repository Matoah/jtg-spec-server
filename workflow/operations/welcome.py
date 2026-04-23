from workflow.state.workflow_state import WorkflowState


def welcome(state: WorkflowState):
    """
    欢迎
    :param state:
    :return:
    """
    return {
        "content": "我已经接收到问题，正在为您处理..."
    }
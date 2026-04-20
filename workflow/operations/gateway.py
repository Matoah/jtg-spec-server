from completeions.gateway import GatewayCompletion
from workflow.state.workflow_state import WorkflowState
from enums.audit_status import AuditStatus


def gateway(state: WorkflowState):
    """
    网关
    """
    query = state.query
    gateway_completion = GatewayCompletion()
    result = gateway_completion.ask(query)
    return {
        "content": result.reject_message,
        "audit_status":  AuditStatus.PASS if result.is_related else AuditStatus.REJECT
    }

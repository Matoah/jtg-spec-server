from workflow.state.workflow_state import WorkflowState
from retrieval.combined_retrieval import retrieve_document as combined_retrieve_document
from configs import spec_server_config

def combined_search(state: WorkflowState):
    """组合搜索"""
    top_k = spec_server_config.KNOWLEDGE_TOP_K
    documents = combined_retrieve_document(state.query, top_k)
    return {
        "documents": documents
    }

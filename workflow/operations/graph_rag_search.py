from workflow.state.workflow_state import WorkflowState
from retrieval.graph_rag_retrieval import retrieve_document


def graph_rag_search(state: WorkflowState):
    """图RAG搜索"""
    query = state.query
    documents = retrieve_document(query)
    #state.documents.extend(documents)
    return {
        "documents": documents
    }
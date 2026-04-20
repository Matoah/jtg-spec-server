from workflow.state.workflow_state import WorkflowState
import logging
from configs import spec_server_config
from retrieval.hybrid_retrieval import retrieve_document

logger = logging.getLogger(__name__)

def hybrid_traditional_search(state: WorkflowState):
    """混合传统搜索"""
    logger.info("使用传统混合检索")
    query = state.query
    top_k = spec_server_config.KNOWLEDGE_TOP_K

    # 执行传统混合检索
    docs = retrieve_document(query, top_k)
    #state.documents.extend(docs)
    return {
        "documents": docs
    }

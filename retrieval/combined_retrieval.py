from retrieval.graph_rag_retrieval import retrieve_document as graph_retrieve_document
from retrieval.hybrid_retrieval import retrieve_document as hybrid_retrieve_document

def retrieve_document(query: str, top_k: int = 10):
    """组合搜索"""
    traditional_k = max(1, top_k // 2)
    graph_k = top_k - traditional_k

    # 执行两种检索
    traditional_docs = hybrid_retrieve_document(query, traditional_k)
    graph_docs = graph_retrieve_document(query, graph_k)

    # 合并和去重
    combined_docs = []
    seen_contents = set()

    # 交替添加结果（Round-robin）
    max_len = max(len(traditional_docs), len(graph_docs))
    for i in range(max_len):
        # 先添加图RAG结果（通常质量更高）
        if i < len(graph_docs):
            doc = graph_docs[i]
            content_hash = hash(doc.page_content[:100])
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                doc.metadata["search_source"] = "graph_rag"
                combined_docs.append(doc)

        # 再添加传统检索结果
        if i < len(traditional_docs):
            doc = traditional_docs[i]
            content_hash = hash(doc.page_content[:100])
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                doc.metadata["search_source"] = "traditional"
                combined_docs.append(doc)

    return combined_docs[:top_k]

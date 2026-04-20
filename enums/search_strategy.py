from enum import Enum

class SearchStrategy(str, Enum):
    """检索策略"""

    # 传统混合检索
    HYBRID_TRADITIONAL = "hybrid_traditional"

    # 图RAG检索
    GRAPH_RAG = "graph_rag"

    # 组合策略
    COMBINED = "combined"

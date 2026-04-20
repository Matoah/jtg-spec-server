from enum import Enum


class GraphQueryType(str, Enum):
    """图库查询类型"""

    # 实体关系查询：A和B有什么关系？
    ENTITY_RELATION = "entity_relation"

    # 多跳查询：A通过什么连接到C？
    MULTI_HOP = "multi_hop"

    # 子图查询：A相关的所有信息
    SUBGRAPH = "subgraph"

    # 路径查找：从A到B的最佳路径
    PATH_FINDING = "path_finding"

    # 聚类查询：和A相似的都有什么？
    CLUSTERING = "clustering"
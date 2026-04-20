from pydantic import BaseModel, Field
from enums.graph_query_type import GraphQueryType
from typing import List, Dict, Any


class GraphQuery(BaseModel):
    """图库查询模型"""

    query_type: GraphQueryType = Field(description="查询类型")

    source_entities: List[str] = Field(default=None, description="源实体列表")

    target_entities: List[str] = Field(default=None, description="目标实体列表")

    relation_types: List[str] = Field(default=None, description="关系类型列表")

    max_depth: int = Field(default=2, description="最大查询深度")

    max_nodes: int = Field(default=50, description="最大查询节点数")

    constraints: Dict[str, Any] = Field(default=None, description="查询约束")


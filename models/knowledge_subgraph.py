from pydantic import BaseModel, Field
from typing import Any

class KnowledgeSubgraph(BaseModel):
    """知识子图结构"""

    central_nodes: list[dict[str, Any]] = Field(default_factory=list, description="中心节点列表")

    connected_nodes: list[dict[str, Any]] = Field(default_factory=list, description="连接节点列表")

    relationships: list[dict[str, Any]] = Field(default_factory=list, description="关系列表")

    graph_metrics: dict[str, float] = Field(default_factory=dict, description="图指标")

    reasoning_chains: list[list[str]] = Field(default_factory=list, description="推理链列表")

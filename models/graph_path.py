from pydantic import BaseModel, Field
from typing import Any, Dict, List


class GraphPath(BaseModel):
    """图库路径模型"""

    nodes: List[Dict[str, Any]] = Field(description="节点列表")

    path_length: int = Field(description="路径长度")

    relevance_score: float = Field(description="路径相关性分数")

    path_type: str = Field(description="路径类型")

    relationships: List[Dict[str, Any]] = Field(description="路径关系列表")

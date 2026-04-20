from pydantic import BaseModel, Field
from enums.search_strategy import SearchStrategy


class ReasoningRequired(BaseModel):
    """推理需求"""
    multi_hop: bool = Field(description="是否需要多跳推理", default=False)

    causal: bool = Field(description="是否需要因果推理", default=False)

    comparison: bool = Field(description="是否需要比较推理", default=False)


class QueryAnalysisResult(BaseModel):
    """查询分析结果"""

    query_complexity: float = Field(description="查询复杂度（0-1）", default=0.5)

    relationship_intensity: float = Field(description="关系密集度（0-1）", default=0.5)

    reasoning_required: ReasoningRequired | None = Field(description="是否需要推理", default=None)

    entity_count: int = Field(description="实体数量", default=1)

    recommended_strategy: SearchStrategy = Field(description="推荐的检索策略")

    confidence: float = Field(description="推荐置信度", default=0.5)

    reasoning: str = Field(description="推荐理由", default="默认分析")

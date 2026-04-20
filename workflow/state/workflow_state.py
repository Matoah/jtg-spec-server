from pydantic import BaseModel, Field
from langchain_core.documents import Document

from enums.audit_status import AuditStatus
from enums.search_strategy import SearchStrategy


class WorkflowState(BaseModel):

    query: str = Field(description="用户查询信息")

    documents: list[Document] = Field(default_factory=list, description="检索到的知识文档")

    content: str = Field(default="", description="内容信息")

    audit_status: AuditStatus = Field(default=AuditStatus.DEFAULT, description="审核状态")

    search_strategy: SearchStrategy = Field(default=SearchStrategy.HYBRID_TRADITIONAL, description="搜索策略")

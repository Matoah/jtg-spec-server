from langchain_core.documents import Document

from completeions.base import CompletionLLM
from langchain_core.messages import HumanMessage
from completeions.prompt_factory import get_prompt, PromptType


class SpecExpertCompletion(CompletionLLM):
    """
    标准规范专家
    """

    def __init__(self, document_list: list[Document]):
        super().__init__()
        self._document_list = document_list

    def _build_system_prompt(self):
        """构建系统提示"""
        return get_prompt(PromptType.SPEC_EXPERT)

    def _build_user_message(self, user_input: str)-> HumanMessage:
        """构建用户消息"""
        user_message = ["- **【规范定义信息】**："]
        for document in self._document_list:
            user_message.append(document.page_content.strip())
        user_message.append("- **【用户问题】**：")
        user_message.append(user_input)
        return HumanMessage(content="\n".join(user_message))

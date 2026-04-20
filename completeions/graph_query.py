from completeions.prompt_factory import get_prompt, PromptType
from models.graph_query import GraphQuery
from completeions.base import JsonCompletionLLM
from pathlib import Path


class GraphQueryCompletion(JsonCompletionLLM[GraphQuery]):
    """
    图库查询LLM
    """

    def __init__(self, node_schemas: list[str], relation_schemas: list[str]):
        super().__init__()
        self._system_prompt = None
        self._node_schemas = node_schemas
        self._relation_schemas = relation_schemas

    def _get_json_schema(self):
        return GraphQuery

    def _build_system_prompt(self):
        """构建系统提示"""
        prompt_content = get_prompt(PromptType.GRAPH_QUERY)
        return prompt_content.format(
            node_schema="\n".join(["- " + node_schema for node_schema in self._node_schemas]),
            relation_schema="\n".join(["- " + relation_schema for relation_schema in self._relation_schemas])
        )

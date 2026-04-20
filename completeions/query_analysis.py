from completeions.base import JsonCompletionLLM
from completeions.prompt_factory import get_prompt, PromptType
from models.query_analysis_result import QueryAnalysisResult


class QueryAnalysisCompletion(JsonCompletionLLM[QueryAnalysisResult]):

    def _get_json_schema(self):
        return QueryAnalysisResult

    def _build_system_prompt(self):
        """构建系统提示"""
        return get_prompt(PromptType.QUERY_ANALYSIS)

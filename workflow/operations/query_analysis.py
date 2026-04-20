from enums.search_strategy import SearchStrategy
from workflow.state.workflow_state import WorkflowState
from completeions.query_analysis import QueryAnalysisCompletion
import logging

logger = logging.getLogger(__name__)

query_analysis_completion = QueryAnalysisCompletion()


def query_analysis(state: WorkflowState):
    """查询分析"""
    result = query_analysis_completion.ask(state.query)
    logger.info(f"查询分析完成：{result.recommended_strategy.value}，置信度：{result.confidence}, 推荐理由：{result.reasoning}")
    search_strategy = SearchStrategy(result.recommended_strategy)
    return {
        "recommended_strategy": search_strategy,
    }

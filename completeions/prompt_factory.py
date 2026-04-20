from enum import Enum
from pathlib import Path

class PromptType(str, Enum):
    """提示词类型"""

    GATEWAY = "gateway",

    SPEC_EXPERT = "spec_expert",

    QUERY_ANALYSIS = "query_analysis",

    DOCUMENT_FILTER = "document_filter",

    GRAPH_QUERY = "graph_query",

PROMPT_CACHE = {}

def _get_prompt_path(prompt_type: PromptType) -> Path:
    """获取提示词文件路径"""
    return Path(__file__).parent / "prompts" / f"{prompt_type.value}.md"

def get_prompt(prompt_type: PromptType)->str:
    """
    获取提示词
    :param prompt_type:
    :return:
    """
    if prompt_type not in PROMPT_CACHE:
        path = _get_prompt_path(prompt_type)
        PROMPT_CACHE[prompt_type] = path.read_text(encoding="utf-8")
    return PROMPT_CACHE[prompt_type]

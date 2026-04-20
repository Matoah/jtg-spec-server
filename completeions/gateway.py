from completeions.base import JsonCompletionLLM
from completeions.prompt_factory import get_prompt, PromptType
from models.gateway_result import GatewayResult
from pathlib import Path


class GatewayCompletion(JsonCompletionLLM[GatewayResult]):
    """
    网关
    """

    def _get_json_schema(self):
        return GatewayResult

    def _build_system_prompt(self):
        return get_prompt(PromptType.GATEWAY)

from abc import ABC, abstractmethod
import time
from langchain_openai import ChatOpenAI
from configs import spec_server_config
from langchain_core.messages import SystemMessage, HumanMessage
import logging
from utils.text_util import try_parse_json_object

logger = logging.getLogger(__name__)


class CompletionLLM(ABC):
    """LLM基类"""

    def __init__(self):
        self._client = ChatOpenAI(
            api_key=spec_server_config.COMPLETION_API_KEY,
            base_url=spec_server_config.COMPLETION_API_BASE_URL,
            model=spec_server_config.COMPLETION_MODEL,
            max_tokens=spec_server_config.COMPLETION_MAX_TOKEN,
            temperature=spec_server_config.COMPLETION_TEMPERATURE,
            streaming=spec_server_config.COMPLETION_STREAMING,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": spec_server_config.COMPLETION_ENABLE_THINKING
                }
            }
        )

    @abstractmethod
    def _build_system_prompt(self):
        """构建系统提示"""
        raise NotImplementedError("子类必须实现_build_system_prompt方法")

    def _build_user_message(self, user_input: str)-> HumanMessage:
        """构建用户消息"""
        return HumanMessage(content=user_input)

    def ask(self, user_input: str):
        """向大模型提问"""
        system_prompt = self._build_system_prompt()
        human_message = self._build_user_message(user_input)
        messages = [SystemMessage(content=system_prompt), human_message]
        start_time = time.time()
        logger.info(f"正在调用大模型，请稍候...")
        response = self._client.invoke(messages)
        logger.info(f"大模型响应时间：{time.time() - start_time}秒")
        return response.content


class JsonCompletionLLM[T](CompletionLLM):
    """JSON LLM大模型"""

    def __init__(self, max_retry: int = 3):
        super().__init__()
        self._max_retry = max_retry

    @abstractmethod
    def _get_json_schema(self) -> T:
        """获取JSON模式"""
        raise NotImplementedError("子类必须实现_get_json_schema方法")

    def ask(self, user_input: str) -> T:
        """向大模型提问，返回JSON对象"""
        system_prompt = self._build_system_prompt()
        error_msg = ""
        try_count = 0
        while try_count < self._max_retry:
            human_message = f"内容：\n{user_input}"
            if error_msg:
                human_message += f"\n错误信息：\n{error_msg}"
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_message)]
            try:
                start_time = time.time()
                logger.info(f"正在调用大模型，请稍候...")
                response = self._client.invoke(messages)
                logger.info(f"大模型响应时间：{time.time() - start_time}秒")
                response_content, obj = try_parse_json_object(response.content)
                logger.info(f"解析结果：{obj}")
                constructor = self._get_json_schema()
                return constructor(**obj)
            except Exception as e:
                error_msg = str(e)
                try_count += 1
        return None
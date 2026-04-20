from pydantic import Field
from pydantic_settings import SettingsConfigDict
from configs.feature import FeatureConfig
from configs.middleware import MiddlewareConfig


class SpecServerConfig(FeatureConfig, MiddlewareConfig):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # ignore extra attributes
        extra="ignore",
    )

    DEBUG: bool = Field(default=False, description="是否开启调试模式")

    ENABLE_SCHEDULER: bool = Field(default=False, description="是否开启定时任务调度器")

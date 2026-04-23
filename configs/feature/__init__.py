from typing import Annotated, Optional
from pydantic_settings import BaseSettings
from pydantic import (
    AliasChoices,
    Field,
    PositiveFloat,
    PositiveInt,
    computed_field,
    NonNegativeInt,
)


class LoggingConfig(BaseSettings):
    """
    Configuration for application logging
    """

    LOG_LEVEL: str = Field(
        description="Logging level, default to INFO. Set to ERROR for production environments.",
        default="INFO",
    )

    LOG_FILE: Optional[str] = Field(
        description="File path for log output.",
        default=None,
    )

    LOG_FILE_MAX_SIZE: PositiveInt = Field(
        description="Maximum file size for file rotation retention, the unit is megabytes (MB)",
        default=20,
    )

    LOG_FILE_BACKUP_COUNT: PositiveInt = Field(
        description="Maximum file backup count file rotation retention",
        default=5,
    )

    LOG_FORMAT: str = Field(
        description="Format string for log messages",
        default="%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] [%(filename)s:%(lineno)d] - %(message)s",
    )

    LOG_DATEFORMAT: Optional[str] = Field(
        description="Date format string for log timestamps",
        default=None,
    )

    LOG_TZ: Optional[str] = Field(
        description="Timezone for log timestamps (e.g., 'America/New_York')",
        default="UTC",
    )


class SecurityConfig(BaseSettings):
    """
    Security-related configurations for the application
    """

    SECRET_KEY: str = Field(
        description="Secret key for secure session cookie signing."
                    "Make sure you are changing this key for your deployment with a strong key."
                    "Generate a strong key using `openssl rand -base64 42` or set via the `SECRET_KEY` environment variable.",
        default="",
    )

    RESET_PASSWORD_TOKEN_EXPIRY_MINUTES: PositiveInt = Field(
        description="Duration in minutes for which a password reset token remains valid",
        default=5,
    )

    LOGIN_DISABLED: bool = Field(
        description="Whether to disable login checks",
        default=False,
    )

    ADMIN_API_KEY_ENABLE: bool = Field(
        description="Whether to enable admin api key for authentication",
        default=False,
    )

    ADMIN_API_KEY: Optional[str] = Field(
        description="admin api key for authentication",
        default=None,
    )


class CeleryBeatConfig(BaseSettings):
    CELERY_BEAT_SCHEDULER_TIME: int = Field(
        description="Interval in days for Celery Beat scheduler execution, default to 1 day",
        default=1,
    )


class LoginConfig(BaseSettings):
    ENABLE_EMAIL_CODE_LOGIN: bool = Field(
        description="whether to enable email code login",
        default=False,
    )
    ENABLE_EMAIL_PASSWORD_LOGIN: bool = Field(
        description="whether to enable email password login",
        default=True,
    )
    ENABLE_SOCIAL_OAUTH_LOGIN: bool = Field(
        description="whether to enable github/google oauth login",
        default=False,
    )
    EMAIL_CODE_LOGIN_TOKEN_EXPIRY_MINUTES: PositiveInt = Field(
        description="expiry time in minutes for email code login token",
        default=5,
    )
    ALLOW_REGISTER: bool = Field(
        description="whether to enable register",
        default=False,
    )
    ALLOW_CREATE_WORKSPACE: bool = Field(
        description="whether to enable create workspace",
        default=False,
    )


class FileUploadConfig(BaseSettings):
    """
    Configuration for file upload limitations
    """

    UPLOAD_FILE_SIZE_LIMIT: NonNegativeInt = Field(
        description="Maximum allowed file size for uploads in megabytes",
        default=15,
    )

    UPLOAD_FILE_BATCH_LIMIT: NonNegativeInt = Field(
        description="Maximum number of files allowed in a single upload batch",
        default=5,
    )

    UPLOAD_IMAGE_FILE_SIZE_LIMIT: NonNegativeInt = Field(
        description="Maximum allowed image file size for uploads in megabytes",
        default=10,
    )

    UPLOAD_VIDEO_FILE_SIZE_LIMIT: NonNegativeInt = Field(
        description="video file size limit in Megabytes for uploading files",
        default=100,
    )

    UPLOAD_AUDIO_FILE_SIZE_LIMIT: NonNegativeInt = Field(
        description="audio file size limit in Megabytes for uploading files",
        default=50,
    )

    BATCH_UPLOAD_LIMIT: NonNegativeInt = Field(
        description="Maximum number of files allowed in a batch upload operation",
        default=20,
    )

    WORKFLOW_FILE_UPLOAD_LIMIT: PositiveInt = Field(
        description="Maximum number of files allowed in a workflow upload operation",
        default=10,
    )


class HttpConfig(BaseSettings):
    """
    HTTP-related configurations for the application
    """

    API_COMPRESSION_ENABLED: bool = Field(
        description="Enable or disable gzip compression for HTTP responses",
        default=False,
    )

    inner_CONSOLE_CORS_ALLOW_ORIGINS: str = Field(
        description="Comma-separated list of allowed origins for CORS in the console",
        validation_alias=AliasChoices("CONSOLE_CORS_ALLOW_ORIGINS", "CONSOLE_WEB_URL"),
        default="",
    )

    @computed_field
    def CONSOLE_CORS_ALLOW_ORIGINS(self) -> list[str]:
        return self.inner_CONSOLE_CORS_ALLOW_ORIGINS.split(",")

    inner_WEB_API_CORS_ALLOW_ORIGINS: str = Field(
        description="",
        validation_alias=AliasChoices("WEB_API_CORS_ALLOW_ORIGINS"),
        default="*",
    )

    @computed_field
    def WEB_API_CORS_ALLOW_ORIGINS(self) -> list[str]:
        return self.inner_WEB_API_CORS_ALLOW_ORIGINS.split(",")

    HTTP_REQUEST_MAX_CONNECT_TIMEOUT: Annotated[
        PositiveInt,
        Field(
            ge=10, description="Maximum connection timeout in seconds for HTTP requests"
        ),
    ] = 10

    HTTP_REQUEST_MAX_READ_TIMEOUT: Annotated[
        PositiveInt,
        Field(ge=60, description="Maximum read timeout in seconds for HTTP requests"),
    ] = 60

    HTTP_REQUEST_MAX_WRITE_TIMEOUT: Annotated[
        PositiveInt,
        Field(ge=10, description="Maximum write timeout in seconds for HTTP requests"),
    ] = 20

    HTTP_REQUEST_NODE_MAX_BINARY_SIZE: PositiveInt = Field(
        description="Maximum allowed size in bytes for binary data in HTTP requests",
        default=10 * 1024 * 1024,
    )

    HTTP_REQUEST_NODE_MAX_TEXT_SIZE: PositiveInt = Field(
        description="Maximum allowed size in bytes for text data in HTTP requests",
        default=1 * 1024 * 1024,
    )

    HTTP_REQUEST_NODE_SSL_VERIFY: bool = Field(
        description="Enable or disable SSL verification for HTTP requests",
        default=True,
    )

    SSRF_DEFAULT_MAX_RETRIES: PositiveInt = Field(
        description="Maximum number of retries for network requests (SSRF)",
        default=3,
    )

    SSRF_PROXY_ALL_URL: Optional[str] = Field(
        description="Proxy URL for HTTP or HTTPS requests to prevent Server-Side Request Forgery (SSRF)",
        default=None,
    )

    SSRF_PROXY_HTTP_URL: Optional[str] = Field(
        description="Proxy URL for HTTP requests to prevent Server-Side Request Forgery (SSRF)",
        default=None,
    )

    SSRF_PROXY_HTTPS_URL: Optional[str] = Field(
        description="Proxy URL for HTTPS requests to prevent Server-Side Request Forgery (SSRF)",
        default=None,
    )

    SSRF_DEFAULT_TIME_OUT: PositiveFloat = Field(
        description="The default timeout period used for network requests (SSRF)",
        default=5,
    )

    SSRF_DEFAULT_CONNECT_TIME_OUT: PositiveFloat = Field(
        description="The default connect timeout period used for network requests (SSRF)",
        default=5,
    )

    SSRF_DEFAULT_READ_TIME_OUT: PositiveFloat = Field(
        description="The default read timeout period used for network requests (SSRF)",
        default=5,
    )

    SSRF_DEFAULT_WRITE_TIME_OUT: PositiveFloat = Field(
        description="The default write timeout period used for network requests (SSRF)",
        default=5,
    )

    RESPECT_XFORWARD_HEADERS_ENABLED: bool = Field(
        description="Enable handling of X-Forwarded-For, X-Forwarded-Proto, and X-Forwarded-Port headers"
                    " when the app is behind a single trusted reverse proxy.",
        default=False,
    )


class AuthConfig(BaseSettings):
    """
    Configuration for authentication and OAuth
    """

    OAUTH_REDIRECT_PATH: str = Field(
        description="Redirect path for OAuth authentication callbacks",
        default="/console/api/oauth/authorize",
    )

    GITHUB_CLIENT_ID: Optional[str] = Field(
        description="GitHub OAuth client ID",
        default=None,
    )

    GITHUB_CLIENT_SECRET: Optional[str] = Field(
        description="GitHub OAuth client secret",
        default=None,
    )

    GOOGLE_CLIENT_ID: Optional[str] = Field(
        description="Google OAuth client ID",
        default=None,
    )

    GOOGLE_CLIENT_SECRET: Optional[str] = Field(
        description="Google OAuth client secret",
        default=None,
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: PositiveInt = Field(
        description="Expiration time for access tokens in minutes",
        default=60,
    )

    REFRESH_TOKEN_EXPIRE_DAYS: PositiveFloat = Field(
        description="Expiration time for refresh tokens in days",
        default=30,
    )

    LOGIN_LOCKOUT_DURATION: PositiveInt = Field(
        description="Time (in seconds) a user must wait before retrying login after exceeding the rate limit.",
        default=86400,
    )

    FORGOT_PASSWORD_LOCKOUT_DURATION: PositiveInt = Field(
        description="Time (in seconds) a user must wait before retrying password reset after exceeding the rate limit.",
        default=86400,
    )


class MailConfig(BaseSettings):
    """
    Configuration for email services
    """

    MAIL_TYPE: Optional[str] = Field(
        description="Email service provider type ('smtp' or 'resend'), default to None.",
        default=None,
    )

    MAIL_DEFAULT_SEND_FROM: Optional[str] = Field(
        description="Default email address to use as the sender",
        default=None,
    )

    RESEND_API_KEY: Optional[str] = Field(
        description="API key for Resend email service",
        default=None,
    )

    RESEND_API_URL: Optional[str] = Field(
        description="API URL for Resend email service",
        default=None,
    )

    SMTP_SERVER: Optional[str] = Field(
        description="SMTP server hostname",
        default=None,
    )

    SMTP_PORT: Optional[int] = Field(
        description="SMTP server port number",
        default=465,
    )

    SMTP_USERNAME: Optional[str] = Field(
        description="Username for SMTP authentication",
        default=None,
    )

    SMTP_PASSWORD: Optional[str] = Field(
        description="Password for SMTP authentication",
        default=None,
    )

    SMTP_USE_TLS: bool = Field(
        description="Enable TLS encryption for SMTP connections",
        default=False,
    )

    SMTP_OPPORTUNISTIC_TLS: bool = Field(
        description="Enable opportunistic TLS for SMTP connections",
        default=False,
    )

    EMAIL_SEND_IP_LIMIT_PER_MINUTE: PositiveInt = Field(
        description="Maximum number of emails allowed to be sent from the same IP address in a minute",
        default=50,
    )


class BillingConfig(BaseSettings):
    """
    Configuration for platform billing features
    """

    BILLING_ENABLED: bool = Field(
        description="Enable or disable billing functionality",
        default=False,
    )


class FileAccessConfig(BaseSettings):
    """
    Configuration for file access and handling
    """

    FILES_URL: str = Field(
        description="Base URL for file preview or download,"
                    " used for frontend display and multi-model inputs"
                    "Url is signed and has expiration time.",
        validation_alias=AliasChoices("FILES_URL", "CONSOLE_API_URL"),
        alias_priority=1,
        default="",
    )

    FILES_ACCESS_TIMEOUT: int = Field(
        description="Expiration time in seconds for file access URLs",
        default=300,
    )


class EndpointConfig(BaseSettings):
    """
    Configuration for various application endpoints and URLs
    """

    CONSOLE_API_URL: str = Field(
        description="Base URL for the console API,"
                    "used for login authentication callback or notion integration callbacks",
        default="",
    )

    CONSOLE_WEB_URL: str = Field(
        description="Base URL for the console web interface,used for frontend references and CORS configuration",
        default="",
    )

    SERVICE_API_URL: str = Field(
        description="Base URL for the service API, displayed to users for API access",
        default="",
    )

    APP_WEB_URL: str = Field(
        description="Base URL for the web application, used for frontend references",
        default="",
    )

    ENDPOINT_URL_TEMPLATE: str = Field(
        description="Template url for endpoint plugin",
        default="http://localhost:5002/e/{hook_id}",
    )

    TGCOST_SERVICE_API_URL: str = Field(
        description="Base URL for the tgcost service API, used for tgcost account login decode token",
        default="",
    )

    TGCOST_SERVICE_API_KEY: str = Field(
        description="tgcost aip key for decode login token",
        default="",
    )

    DIFY_SERVICE_API_URL: str = Field(
        description="Base URL for the toone dify service API, used to chat 、knowledge and more for API accees",
        default="",
    )

    DIFY_SERVICE_API_CHAT_SK: str = Field(
        description="Base URL for the toone dify service API, used  CHAT_SK for API accees",
        default="",
    )

    DIFY_SERVICE_API_SIMILAR_QUESTIONS_SK: str = Field(
        description="Base URL for the toone dify service API, used  SIMILAR_QUESTIONS_SK for API accees",
        default="",
    )

    DIFY_DOCUMENT_API_SK: str = Field(
        description="Base URL for the toone dify document API, used  DIFY_DOCUMENT_API_SK for API accees",
        default="",
    )
    DIFY_ANNOTATION_API_URL: str = Field(
        description="Base URL for the toone dify service API, used to annotation",
        default="",
    )

    ANNOTATION_APP_KEY: str = Field(
        description="annotation aip key for decode login token",
        default="",
    )
    ANNOTATION_TENANT_ID: str = Field(
        description="annotation app tenant id for decode login token",
        default="",
    )
    ANNOTATION_UPDATED_BY: str = Field(
        description="annotation app updated by for decode login token",
        default="",
    )

    TONGJI_SERVICE_API_URL: str = Field(
        description="统计服务 api url",
        default="",
    )
    TONGJI_USER_NAME: str = Field(
        description="统计服务用户名",
        default="",
    )
    TONGJI_USER_PASSWORD: str = Field(
        description="统计服务密码",
        default="",
    )
    TONGJI_WEBSITE_ID: str = Field(
        description="统计服务website id",
        default="",
    )
    TONGJI_DATABASE_URL: str = Field(
        description="统计服数据库连接地址",
        default="",
    )
    DIFY_SERVICE_API_QA_SK: str = Field(
        description="Base URL for the Extract QA API, used  DIFY_SERVICE_API_QA_SK for API accees",
        default="",
    )
    MINERU_SERVICE_API_URL: str = Field(
        description="Base URL for the mineru service API, used knowledge and more for API accees",
        default="",
    )
    MINERU_SERVICE_API_KEY: str = Field(
        description="Base URL for the mineru online service key, used knowledge and more for API accees",
        default="",
    )
    DIFY_VL_API_SK: str = Field(
        description="Base URL for the Extract VL  API, used  DIFY_VL_API_SK for API accees",
        default="",
    )
    DIFY_PUSH_ROBOT_SK: str = Field(
        description="Base URL for the push robot API, used  DIFY_PUSH_ROBOT_SK for API accees",
        default="",
    )


class RagEtlConfig(BaseSettings):
    """
    Configuration for RAG ETL processes
    """

    # TODO: This config is not only for rag etl, it is also for file upload, we should move it to file upload config
    ETL_TYPE: str = Field(
        description="RAG ETL type ('dify' or 'Unstructured'), default to 'dify'",
        default="dify",
    )

    KEYWORD_DATA_SOURCE_TYPE: str = Field(
        description="Data source type for keyword extraction"
                    " ('database' or other supported types), default to 'database'",
        default="database",
    )

    UNSTRUCTURED_API_URL: Optional[str] = Field(
        description="API URL for Unstructured.io service",
        default=None,
    )

    UNSTRUCTURED_API_KEY: Optional[str] = Field(
        description="API key for Unstructured.io service",
        default="",
    )

    SCARF_NO_ANALYTICS: Optional[str] = Field(
        description="This is about whether to disable Scarf analytics in Unstructured library.",
        default="false",
    )


class ModelLoadBalanceConfig(BaseSettings):
    """
    Configuration for model load balancing and token counting
    """

    MODEL_LB_ENABLED: bool = Field(
        description="Enable or disable load balancing for models",
        default=False,
    )

    PLUGIN_BASED_TOKEN_COUNTING_ENABLED: bool = Field(
        description="Enable or disable plugin based token counting. If disabled, token counting will return 0.",
        default=False,
    )


class DataSetConfig(BaseSettings):
    """
    Configuration for dataset management
    """

    PLAN_SANDBOX_CLEAN_DAY_SETTING: PositiveInt = Field(
        description="Interval in days for dataset cleanup operations - plan: sandbox",
        default=30,
    )

    PLAN_PRO_CLEAN_DAY_SETTING: PositiveInt = Field(
        description="Interval in days for dataset cleanup operations - plan: pro and team",
        default=7,
    )

    DATASET_OPERATOR_ENABLED: bool = Field(
        description="Enable or disable dataset operator functionality",
        default=False,
    )

    TIDB_SERVERLESS_NUMBER: PositiveInt = Field(
        description="number of tidb serverless cluster",
        default=500,
    )

    CREATE_TIDB_SERVICE_JOB_ENABLED: bool = Field(
        description="Enable or disable create tidb service job",
        default=False,
    )

    PLAN_SANDBOX_CLEAN_MESSAGE_DAY_SETTING: PositiveInt = Field(
        description="Interval in days for message cleanup operations - plan: sandbox",
        default=30,
    )


class AccountConfig(BaseSettings):
    ACCOUNT_DELETION_TOKEN_EXPIRY_MINUTES: PositiveInt = Field(
        description="Duration in minutes for which a account deletion token remains valid",
        default=5,
    )

    EDUCATION_ENABLED: bool = Field(
        description="whether to enable education identity",
        default=False,
    )


class AlibabaCloudConfig(BaseSettings):
    ALIBABA_CLOUD_ACCESS_KEY_ID: str = Field(
        description="Access key ID for Alibaba Cloud services",
        default="",
    )
    ALIBABA_CLOUD_ACCESS_KEY_SECRET: str = Field(
        description="Access key secret for Alibaba Cloud services",
        default="",
    )
    ALIBABA_CLOUD_SMS_SIGN_NAME: str = Field(
        description="SMS sign name for Alibaba Cloud services",
        default="",
    )
    ALIBABA_CLOUD_SMS_TEMPLATE_CODE: str = Field(
        description="SMS template code for Alibaba Cloud services",
        default="",
    )


class RabbitMQConfig(BaseSettings):
    RABBITMQ_HOST: str = Field(
        description="RabbitMQ URL",
        default="",
    )
    RABBITMQ_PORT: int = Field(
        description="RabbitMQ port",
        default=5672,
    )
    RABBITMQ_USERNAME: str = Field(
        description="RabbitMQ username",
        default="",
    )
    RABBITMQ_PASSWORD: str = Field(
        description="RabbitMQ password",
        default="",
    )
    RABBITMQ_VIRTUAL_HOST: str = Field(
        description="RabbitMQ virtual host",
        default="/",
    )

class Neo4jConfig(BaseSettings):
    NEO4J_URI: str = Field(description="Neo4j URI")

    NEO4J_USERNAME: str = Field(description="Neo4j username")

    NEO4J_PASSWORD: str = Field(description="Neo4j password")

    NEO4J_DATABASE: str = Field(description="Neo4j database")


class CompletionConfig(BaseSettings):

    COMPLETION_API_KEY: str = Field(
        description="Completion API key",
        default="",
    )

    COMPLETION_API_BASE_URL: str = Field(
        description="Completion API base URL",
        default="",
    )

    COMPLETION_MODEL: str = Field(
        description="Completion model",
        default="",
    )

    COMPLETION_ENABLE_THINKING: bool = Field(
        description="Enable or disable thinking for completion",
        default=False,
    )

    COMPLETION_TEMPERATURE: float = Field(
        description="Temperature for completion",
        default=0.7,
    )

    COMPLETION_MAX_TOKEN: int = Field(
        description="Max token for completion",
        default=1024,
    )

    COMPLETION_STREAMING: bool = Field(
        description="Enable or disable streaming for completion",
        default=False,
    )

class KnowledgeConfig(BaseSettings):
    KNOWLEDGE_BASE_URI: str = Field(
        description="Knowledge库基础URI",
        default="",
    )

    KNOWLEDGE_API_KEY: str = Field(
        description="Knowledge库 API key",
        default="",
    )

    KNOWLEDGE_DATASET: str = Field(
        description="Knowledge库数据集",
        default="",
    )

    KNOWLEDGE_TOP_K: int = Field(
        description="Knowledge库Top-K",
        default=10,
    )


class FeatureConfig(
    LoggingConfig,
    KnowledgeConfig,
    LoginConfig,
    CeleryBeatConfig,
    SecurityConfig,
    HttpConfig,
    AuthConfig,
    MailConfig,
    BillingConfig,
    FileAccessConfig,
    EndpointConfig,
    RagEtlConfig,
    FileUploadConfig,
    ModelLoadBalanceConfig,
    DataSetConfig,
    AccountConfig,
    AlibabaCloudConfig,
    RabbitMQConfig,
    Neo4jConfig,
    CompletionConfig,
):
    pass

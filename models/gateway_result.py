from pydantic import Field, BaseModel

class GatewayResult(BaseModel):
    """
    网关结果
    """

    is_related: bool = Field(default=False, description="是否相关")

    reject_message: str = Field(default="", description="拒绝消息")

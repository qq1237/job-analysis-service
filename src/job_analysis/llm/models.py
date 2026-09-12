from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Message(BaseModel):
    """一条对话消息。"""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    """一次对话生成请求。"""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    response_format: Literal[
        "text",
        "json_object",
    ] = "text"
    max_output_tokens: int = Field(
        default=512,
        ge=1,
        le=4096,
    )
    messages: list[Message] = Field(min_length=1)
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

from openai import AsyncOpenAI

from job_analysis.exceptions import LLMResponseError
from job_analysis.llm.models import ChatRequest


class KimiLLMClient:
    """通过OpenAI兼容SDK调用Kimi。"""

    def __init__(
        self,
        sdk_client: AsyncOpenAI,
        model: str,
    ) -> None:
        self._sdk_client = sdk_client
        self._model = model

    async def generate(
        self,
        request: ChatRequest,
    ) -> str:
        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
        ]

        completion = await self._sdk_client.chat.completions.create(
            model=self._model,
            messages=messages,
            response_format={
                "type": request.response_format,
            },
            max_completion_tokens=request.max_output_tokens,
            extra_body={
                "thinking": {
                    "type": "disabled",
                }
            },
        )

        if not completion.choices:
            raise LLMResponseError("模型响应中没有choices")

        choice = completion.choices[0]
        content = choice.message.content

        if content is None or not content.strip():
            raise LLMResponseError("模型没有返回有效文本")

        if choice.finish_reason == "length":
            raise LLMResponseError("模型输出因长度限制被截断")

        return content

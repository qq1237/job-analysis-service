from typing import Protocol

from job_analysis.llm.models import ChatRequest


class ChatModelClient(Protocol):
    """业务Service需要的模型调用接口。"""

    async def generate(
        self,
        request: ChatRequest,
    ) -> str:
        ...

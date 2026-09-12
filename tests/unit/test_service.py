import asyncio
import json

import pytest

from job_analysis.exceptions import JobAnalysisParseError
from job_analysis.llm.models import ChatRequest
from job_analysis.service import JobAnalysisService


class SequenceLLMClient:
    """按照预设顺序返回模型文本。"""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.call_count = 0
        self.requests: list[ChatRequest] = []

    async def generate(self, request: ChatRequest) -> str:
        self.requests.append(request)
        response = self._responses[self.call_count]
        self.call_count += 1
        return response


def test_valid_model_text_returns_job_analysis() -> None:
    model_text = json.dumps(
        {
            "matched_skills": ["Python"],
            "missing_skills": ["RAG"],
            "summary": "需要补充RAG",
        },
        ensure_ascii=False,
    )
    client = SequenceLLMClient([model_text])
    service = JobAnalysisService(client, max_attempts=1)

    result = asyncio.run(
        service.analyze(
            job_text="招聘RAG工程师",
            candidate_skills=["Python"],
        )
    )

    assert result.matched_skills == ["Python"]
    assert client.call_count == 1
    assert client.requests[0].response_format == "json_object"
    assert client.requests[0].max_output_tokens == 512


def test_all_invalid_outputs_raise_parse_error() -> None:
    client = SequenceLLMClient(
        [
            "第一次不是JSON",
            "第二次也不是JSON",
        ]
    )
    service = JobAnalysisService(client, max_attempts=2)

    with pytest.raises(JobAnalysisParseError):
        asyncio.run(
            service.analyze(
                job_text="招聘RAG工程师",
                candidate_skills=["Python"],
            )
        )

    assert client.call_count == 2

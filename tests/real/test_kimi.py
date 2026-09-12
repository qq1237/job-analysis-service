import asyncio
import os

import pytest
from openai import AsyncOpenAI

from job_analysis.config import load_kimi_config
from job_analysis.llm.kimi import KimiLLMClient
from job_analysis.models import JobAnalysis
from job_analysis.service import JobAnalysisService


pytestmark = [
    pytest.mark.real_model,
    pytest.mark.skipif(
        os.getenv("RUN_REAL_MODEL_TESTS") != "1",
        reason="设置RUN_REAL_MODEL_TESTS=1后才调用真实模型",
    ),
]


def test_real_kimi_returns_job_analysis() -> None:
    async def run() -> JobAnalysis:
        config = load_kimi_config()
        sdk_client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )
        service = JobAnalysisService(
            KimiLLMClient(
                sdk_client=sdk_client,
                model=config.model,
            )
        )

        try:
            return await service.analyze(
                job_text=(
                    "招聘大模型应用开发工程师，"
                    "要求熟悉Python和RAG。"
                ),
                candidate_skills=["Python"],
            )
        finally:
            await sdk_client.close()

    result = asyncio.run(run())

    assert result.summary.strip()
    assert isinstance(result.matched_skills, list)
    assert isinstance(result.missing_skills, list)

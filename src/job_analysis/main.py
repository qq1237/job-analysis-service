from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from openai import AsyncOpenAI

from job_analysis.api import router
from job_analysis.config import load_kimi_config
from job_analysis.llm.kimi import KimiLLMClient
from job_analysis.service import JobAnalysisService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """创建并关闭应用共享资源。"""

    config = load_kimi_config()
    sdk_client = AsyncOpenAI(
        api_key=config.api_key,
        base_url=config.base_url,
    )
    llm_client = KimiLLMClient(
        sdk_client=sdk_client,
        model=config.model,
    )
    app.state.job_analysis_service = JobAnalysisService(
        llm_client=llm_client,
    )

    try:
        yield
    finally:
        await sdk_client.close()


app = FastAPI(
    title="岗位分析API",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)

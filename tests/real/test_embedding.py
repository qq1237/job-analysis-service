import asyncio
import os

import pytest
from openai import AsyncOpenAI

from job_analysis.config import load_embedding_config
from job_analysis.rag.openai_embedding import (
    OpenAICompatibleEmbeddingClient,
)


pytestmark = [
    pytest.mark.real_model,
    pytest.mark.skipif(
        os.getenv("RUN_REAL_EMBEDDING_TESTS") != "1",
        reason=(
            "设置RUN_REAL_EMBEDDING_TESTS=1后"
            "才调用真实Embedding模型"
        ),
    ),
]


def test_real_embedding_returns_expected_shape() -> None:
    async def run() -> tuple[
        list[list[float]],
        int,
    ]:
        config = load_embedding_config()
        sdk_client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )
        embedding_client = (
            OpenAICompatibleEmbeddingClient(
                sdk_client=sdk_client,
                model=config.model,
                dimensions=config.dimensions,
                batch_size=config.batch_size,
            )
        )

        try:
            vectors = await embedding_client.embed(
                [
                    "熟悉Python和FastAPI开发",
                    "提供五险一金和带薪年假",
                ]
            )
            return vectors, config.dimensions
        finally:
            await sdk_client.close()

    vectors, dimensions = asyncio.run(run())

    assert len(vectors) == 2
    assert all(
        len(vector) == dimensions
        for vector in vectors
    )
    assert all(
        isinstance(value, float)
        for vector in vectors
        for value in vector
    )

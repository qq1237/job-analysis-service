import asyncio
from dataclasses import dataclass

from job_analysis.rag.openai_embedding import (
    OpenAICompatibleEmbeddingClient,
)


@dataclass
class FakeEmbeddingItem:
    index: int
    embedding: list[float]


@dataclass
class FakeEmbeddingResponse:
    data: list[FakeEmbeddingItem]


class FakeEmbeddingsResource:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self._vectors_by_text = {
            "text-a": [1.0, 0.0],
            "text-b": [2.0, 0.0],
            "text-c": [3.0, 0.0],
        }

    async def create(
        self,
        *,
        model: str,
        input: list[str],
        dimensions: int,
        encoding_format: str,
    ) -> FakeEmbeddingResponse:
        self.calls.append(
            {
                "model": model,
                "input": input.copy(),
                "dimensions": dimensions,
                "encoding_format": encoding_format,
            }
        )

        items = [
            FakeEmbeddingItem(
                index=index,
                embedding=self._vectors_by_text[text],
            )
            for index, text in enumerate(input)
        ]
        items.reverse()

        return FakeEmbeddingResponse(data=items)


class FakeSDKClient:
    def __init__(self) -> None:
        self.embeddings = FakeEmbeddingsResource()


def test_embedding_client_batches_and_restores_order() -> None:
    sdk_client = FakeSDKClient()
    client = OpenAICompatibleEmbeddingClient(
        sdk_client=sdk_client,
        model="text-embedding-v4",
        dimensions=2,
        batch_size=2,
    )

    vectors = asyncio.run(
        client.embed(
            ["text-a", "text-b", "text-c"]
        )
    )

    assert sdk_client.embeddings.calls == [
        {
            "model": "text-embedding-v4",
            "input": ["text-a", "text-b"],
            "dimensions": 2,
            "encoding_format": "float",
        },
        {
            "model": "text-embedding-v4",
            "input": ["text-c"],
            "dimensions": 2,
            "encoding_format": "float",
        },
    ]
    assert vectors == [
        [1.0, 0.0],
        [2.0, 0.0],
        [3.0, 0.0],
    ]

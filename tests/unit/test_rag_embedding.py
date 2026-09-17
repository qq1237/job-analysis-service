import asyncio

from job_analysis.rag.embedding import embed_chunks
from job_analysis.rag.models import Chunk


class FakeEmbeddingClient:
    def __init__(
        self,
        vectors: list[list[float]],
    ) -> None:
        self.vectors = vectors
        self.received_texts: list[str] = []

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        self.received_texts = texts
        return self.vectors


def test_embed_chunks_combines_chunks_and_vectors() -> None:
    chunks = [
        Chunk(
            chunk_id="doc-001-chunk-0000",
            document_id="doc-001",
            content="要求熟悉 Python",
            chunk_index=0,
            metadata={"source": "job-001"},
        ),
        Chunk(
            chunk_id="doc-001-chunk-0001",
            document_id="doc-001",
            content="需要具有 RAG 项目经验",
            chunk_index=1,
            metadata={"source": "job-001"},
        ),
    ]

    vectors = [
        [1.0, 0.0],
        [0.0, 1.0],
    ]

    fake_client = FakeEmbeddingClient(vectors)

    embedded_chunks = asyncio.run(
        embed_chunks(
            chunks=chunks,
            embedding_client=fake_client,
        )
    )

    assert fake_client.received_texts == [
        "要求熟悉 Python",
        "需要具有 RAG 项目经验",
    ]

    assert len(embedded_chunks) == 2

    assert embedded_chunks[0].chunk == chunks[0]
    assert embedded_chunks[0].vector == [1.0, 0.0]

    assert embedded_chunks[1].chunk == chunks[1]
    assert embedded_chunks[1].vector == [0.0, 1.0]
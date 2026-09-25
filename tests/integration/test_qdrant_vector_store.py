import asyncio
from pathlib import Path

import pytest
from qdrant_client import AsyncQdrantClient

from job_analysis.rag.models import (
    Chunk,
    EmbeddedChunk,
)
from job_analysis.rag.qdrant_vector_store import (
    QdrantVectorStore,
)


def test_qdrant_store_persists_after_reopen(
    tmp_path: Path,
) -> None:
    storage_path = tmp_path / "qdrant"
    collection_name = "test_chunks"

    embedded_chunk = EmbeddedChunk(
        chunk=Chunk(
            chunk_id="doc-001-chunk-0000",
            document_id="doc-001",
            content="Python skills",
            chunk_index=0,
            metadata={"source": "test-source"},
        ),
        vector=[1.0, 0.0],
    )

    async def run_flow():
        first_client = AsyncQdrantClient(
            path=str(storage_path),
        )
        first_store = QdrantVectorStore(
            client=first_client,
            collection_name=collection_name,
            vector_size=2,
        )

        try:
            await first_store.initialize()
            await first_store.upsert(
                [embedded_chunk]
            )
        finally:
            await first_client.close()

        restarted_client = AsyncQdrantClient(
            path=str(storage_path),
        )
        restarted_store = QdrantVectorStore(
            client=restarted_client,
            collection_name=collection_name,
            vector_size=2,
        )

        try:
            await restarted_store.initialize()

            return await restarted_store.search(
                query_vector=[1.0, 0.0],
                top_k=1,
            )
        finally:
            await restarted_client.close()

    results = asyncio.run(run_flow())

    assert len(results) == 1
    assert results[0].chunk == embedded_chunk.chunk
    assert results[0].score == pytest.approx(1.0)
import asyncio

from job_analysis.rag.models import Chunk, EmbeddedChunk
from job_analysis.rag.vector_store import InMemoryVectorStore


def test_search_returns_most_similar_chunks() -> None:
    chunk_a = Chunk(
        chunk_id="doc-001-chunk-0000",
        document_id="doc-001",
        content="Chunk A",
        chunk_index=0,
    )
    chunk_b = Chunk(
        chunk_id="doc-001-chunk-0001",
        document_id="doc-001",
        content="Chunk B",
        chunk_index=1,
    )
    chunk_c = Chunk(
        chunk_id="doc-001-chunk-0002",
        document_id="doc-001",
        content="Chunk C",
        chunk_index=2,
    )

    embedded_chunks = [
        EmbeddedChunk(
            chunk=chunk_a,
            vector=[1.0, 0.0],
        ),
        EmbeddedChunk(
            chunk=chunk_b,
            vector=[0.7, 0.7],
        ),
        EmbeddedChunk(
            chunk=chunk_c,
            vector=[0.0, 1.0],
        ),
    ]

    async def run_search():
        store = InMemoryVectorStore()

        await store.upsert(embedded_chunks)

        return await store.search(
            query_vector=[1.0, 0.0],
            top_k=2,
        )

    results = asyncio.run(run_search())

    assert len(results) == 2
    assert results[0].chunk == chunk_a
    assert results[1].chunk == chunk_b
    assert results[0].score > results[1].score
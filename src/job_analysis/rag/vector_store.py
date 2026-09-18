from .models import EmbeddedChunk, SearchResult
from .similarity import cosine_similarity


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._records: dict[str, EmbeddedChunk] = {}

    async def upsert(
        self,
        embedded_chunks: list[EmbeddedChunk],
    ) -> None:
        for embedded_chunk in embedded_chunks:
            chunk_id = embedded_chunk.chunk.chunk_id
            self._records[chunk_id] = embedded_chunk

    async def search(
        self,
        query_vector: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        if not query_vector:
            raise ValueError("query_vector must not be empty")

        results: list[SearchResult] = []

        for embedded_chunk in self._records.values():
            score = cosine_similarity(
                query_vector,
                embedded_chunk.vector,
            )

            search_result = SearchResult(
                chunk=embedded_chunk.chunk,
                score=score,
            )
            results.append(search_result)

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]
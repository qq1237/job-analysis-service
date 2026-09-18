from typing import Protocol

from .models import EmbeddedChunk, SearchResult


class EmbeddingClient(Protocol):
    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        ...


class VectorStore(Protocol):
    async def upsert(
        self,
        embedded_chunks: list[EmbeddedChunk],
    ) -> None:
        ...

    async def search(
        self,
        query_vector: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        ...
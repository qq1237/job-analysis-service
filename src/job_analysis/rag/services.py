"""Application services for RAG indexing and retrieval."""

from .embedding import embed_chunks
from .models import Document, SearchResult
from .protocols import EmbeddingClient, VectorStore
from .splitter import split_document


class DocumentIndexer:
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        vector_store: VectorStore,
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        self._embedding_client = embedding_client
        self._vector_store = vector_store
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    async def index(
        self,
        document: Document,
    ) -> int:
        chunks = split_document(
            document=document,
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )

        embedded_chunks = await embed_chunks(
            chunks=chunks,
            embedding_client=self._embedding_client,
        )

        await self._vector_store.upsert(embedded_chunks)

        return len(embedded_chunks)

class Retriever:
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        vector_store: VectorStore,
    ) -> None:
        self._embedding_client = embedding_client
        self._vector_store = vector_store

    async def retrieve(
        self,
        question: str,
        top_k: int,
    ) -> list[SearchResult]:
        cleaned_question = question.strip()

        if not cleaned_question:
            raise ValueError("question must not be empty")

        vectors = await self._embedding_client.embed(
            [cleaned_question]
        )

        if len(vectors) != 1:
            raise ValueError(
                "embedding client must return exactly one query vector"
            )

        query_vector = vectors[0]

        return await self._vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
        )

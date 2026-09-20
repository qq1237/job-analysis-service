"""Application services for RAG indexing, retrieval, and answering."""

from job_analysis.llm.models import ChatRequest
from job_analysis.llm.protocols import ChatModelClient

from .context import build_context
from .embedding import embed_chunks
from .models import (
    Document,
    RAGAnswer,
    SearchResult,
)
from .prompts import build_rag_messages
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

'''
question
→ Retriever
→ list[SearchResult]
→ build_context
→ build_rag_messages
→ ChatRequest
→ ChatModelClient.generate
→ model_text
→ RAGAnswer(answer, sources)'''
class RAGAnswerService:
    def __init__(
        self,
        retriever: Retriever,
        chat_model_client: ChatModelClient,
        top_k: int,
        max_output_tokens: int,
    ) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        if not 1 <= max_output_tokens <= 4096:
            raise ValueError(
                "max_output_tokens must be between 1 and 4096"
            )

        self._retriever = retriever
        self._chat_model_client = chat_model_client
        self._top_k = top_k
        self._max_output_tokens = max_output_tokens

    async def answer(
        self,
        question: str,
    ) -> RAGAnswer:
        cleaned_question = question.strip()

        search_results = await self._retriever.retrieve(
            question=cleaned_question,
            top_k=self._top_k,
        )

        if not search_results:
            return RAGAnswer(
                answer="根据现有知识库无法回答该问题。",
                sources=[],
            )

        context = build_context(search_results)
        messages = build_rag_messages(
            question=cleaned_question,
            context=context,
        )

        request = ChatRequest(
            messages=messages,
            response_format="text",
            max_output_tokens=self._max_output_tokens,
        )

        model_text = await self._chat_model_client.generate(
            request
        )

        sources: list[str] = []
        seen_sources: set[str] = set()

        for result in search_results:
            source = (
                result.chunk.metadata.get("source")
                or result.chunk.document_id
            )

            if source not in seen_sources:
                seen_sources.add(source)
                sources.append(source)

        return RAGAnswer(
            answer=model_text,
            sources=sources,
        )
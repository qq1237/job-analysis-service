import asyncio

from job_analysis.llm.models import ChatRequest
from job_analysis.rag.models import Document
from job_analysis.rag.services import (
    DocumentIndexer,
    RAGAnswerService,
    Retriever,
)
from job_analysis.rag.vector_store import InMemoryVectorStore


class FakeEmbeddingClient:
    def __init__(self) -> None:
        self._vectors_by_text = {
            "Python skills": [1.0, 0.0],
            "Benefits info": [0.0, 1.0],
            "Python requirements": [1.0, 0.0],
        }

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [self._vectors_by_text[text] for text in texts]


class FakeChatModelClient:
    def __init__(self) -> None:
        self.requests: list[ChatRequest] = []

    async def generate(
        self,
        request: ChatRequest,
    ) -> str:
        self.requests.append(request)
        return "该岗位要求掌握 Python。"


def test_index_document_and_retrieve_relevant_chunk() -> None:
    embedding_client = FakeEmbeddingClient()
    vector_store = InMemoryVectorStore()

    indexer = DocumentIndexer(
        embedding_client=embedding_client,
        vector_store=vector_store,
        chunk_size=13,
        chunk_overlap=0,
    )
    retriever = Retriever(
        embedding_client=embedding_client,
        vector_store=vector_store,
    )

    document = Document(
        document_id="doc-001",
        content="Python skillsBenefits info",
        metadata={"source": "test"},
    )

    async def run_flow():
        chunk_count = await indexer.index(document)
        results = await retriever.retrieve(
            question="  Python requirements  ",
            top_k=1,
        )
        return chunk_count, results

    chunk_count, results = asyncio.run(run_flow())

    assert chunk_count == 2
    assert len(results) == 1
    assert results[0].chunk.content == "Python skills"
    assert results[0].chunk.document_id == "doc-001"


def test_rag_answer_service_uses_retrieved_context() -> None:
    embedding_client = FakeEmbeddingClient()
    chat_model_client = FakeChatModelClient()
    vector_store = InMemoryVectorStore()

    indexer = DocumentIndexer(
        embedding_client=embedding_client,
        vector_store=vector_store,
        chunk_size=13,
        chunk_overlap=0,
    )
    retriever = Retriever(
        embedding_client=embedding_client,
        vector_store=vector_store,
    )
    answer_service = RAGAnswerService(
        retriever=retriever,
        chat_model_client=chat_model_client,
        top_k=1,
        max_output_tokens=128,
    )

    document = Document(
        document_id="doc-001",
        content="Python skillsBenefits info",
        metadata={"source": "test-source"},
    )

    async def run_flow():
        answer_without_context = await answer_service.answer(
            "Python requirements"
        )

        await indexer.index(document)

        answer_with_context = await answer_service.answer(
            "Python requirements"
        )

        return answer_without_context, answer_with_context

    answer_without_context, answer_with_context = asyncio.run(
        run_flow()
    )

    assert answer_without_context.answer == (
        "根据现有知识库无法回答该问题。"
    )
    assert answer_without_context.sources == []

    assert answer_with_context.answer == "该岗位要求掌握 Python。"
    assert answer_with_context.sources == ["test-source"]

    assert len(chat_model_client.requests) == 1

    request = chat_model_client.requests[0]
    assert request.response_format == "text"
    assert "Python requirements" in request.messages[1].content
    assert "Python skills" in request.messages[1].content
    assert "test-source" in request.messages[1].content

from fastapi import FastAPI
from fastapi.testclient import TestClient

from job_analysis.rag.api import (
    get_document_indexer,
    get_rag_answer_service,
    router,
)
from job_analysis.rag.models import Document, RAGAnswer


class FakeDocumentIndexer:
    def __init__(self) -> None:
        self.received_document: Document | None = None

    async def index(self, document: Document) -> int:
        self.received_document = document
        return 2


class FakeRAGAnswerService:
    def __init__(self) -> None:
        self.received_question: str | None = None

    async def answer(self, question: str) -> RAGAnswer:
        self.received_question = question
        return RAGAnswer(
            answer="该岗位要求掌握 Python。",
            sources=["job-board"],
        )


def test_rag_api_calls_services_and_returns_responses() -> None:
    indexer = FakeDocumentIndexer()
    answer_service = FakeRAGAnswerService()

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_document_indexer] = lambda: indexer
    app.dependency_overrides[
        get_rag_answer_service
    ] = lambda: answer_service

    with TestClient(app) as client:
        index_response = client.post(
            "/rag/documents",
            json={
                "document_id": "job-001",
                "content": "要求熟悉 Python 和 FastAPI",
                "metadata": {"source": "job-board"},
            },
        )
        answer_response = client.post(
            "/rag/questions",
            json={"question": "需要哪些技能？"},
        )

    app.dependency_overrides.clear()

    assert index_response.status_code == 200
    assert index_response.json() == {
        "document_id": "job-001",
        "indexed_chunk_count": 2,
    }
    assert indexer.received_document is not None
    assert indexer.received_document.content == (
        "要求熟悉 Python 和 FastAPI"
    )

    assert answer_response.status_code == 200
    assert answer_response.json() == {
        "answer": "该岗位要求掌握 Python。",
        "sources": ["job-board"],
    }
    assert answer_service.received_question == "需要哪些技能？"

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from job_analysis.exceptions import LLMResponseError

from .api_models import (
    IndexDocumentRequest,
    IndexDocumentResponse,
    RAGQuestionRequest,
)
from .models import Document, RAGAnswer
from .services import DocumentIndexer, RAGAnswerService


router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


def get_document_indexer(
    http_request: Request,
) -> DocumentIndexer:
    return http_request.app.state.document_indexer


def get_rag_answer_service(
    http_request: Request,
) -> RAGAnswerService:
    return http_request.app.state.rag_answer_service


DocumentIndexerDep = Annotated[
    DocumentIndexer,
    Depends(get_document_indexer),
]
RAGAnswerServiceDep = Annotated[
    RAGAnswerService,
    Depends(get_rag_answer_service),
]


@router.post(
    "/documents",
    response_model=IndexDocumentResponse,
)
async def index_document(
    payload: IndexDocumentRequest,
    indexer: DocumentIndexerDep,
) -> IndexDocumentResponse:
    document = Document(
        document_id=payload.document_id,
        content=payload.content,
        metadata=payload.metadata.copy(),
    )

    indexed_chunk_count = await indexer.index(document)

    return IndexDocumentResponse(
        document_id=document.document_id,
        indexed_chunk_count=indexed_chunk_count,
    )


@router.post(
    "/questions",
    response_model=RAGAnswer,
)
async def answer_question(
    payload: RAGQuestionRequest,
    service: RAGAnswerServiceDep,
) -> RAGAnswer:
    try:
        return await service.answer(payload.question)
    except LLMResponseError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="模型返回了无法使用的结果",
        ) from exc

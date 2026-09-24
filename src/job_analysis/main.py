import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from openai import AsyncOpenAI

from job_analysis.api import router as job_router
from job_analysis.config import (
    load_embedding_config,
    load_kimi_config,
)
from job_analysis.llm.kimi import KimiLLMClient
from job_analysis.rag.api import router as rag_router
from job_analysis.rag.openai_embedding import (
    OpenAICompatibleEmbeddingClient,
)
from job_analysis.rag.services import (
    DocumentIndexer,
    RAGAnswerService,
    Retriever,
)
from job_analysis.rag.vector_store import (
    InMemoryVectorStore,
)
from job_analysis.service import JobAnalysisService


RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 50
RAG_TOP_K = 3
RAG_MAX_OUTPUT_TOKENS = 512


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """创建并关闭应用共享资源。"""

    kimi_config = load_kimi_config()
    embedding_config = load_embedding_config()

    kimi_sdk_client = AsyncOpenAI(
        api_key=kimi_config.api_key,
        base_url=kimi_config.base_url,
    )
    embedding_sdk_client = AsyncOpenAI(
        api_key=embedding_config.api_key,
        base_url=embedding_config.base_url,
    )

    llm_client = KimiLLMClient(
        sdk_client=kimi_sdk_client,
        model=kimi_config.model,
    )
    embedding_client = OpenAICompatibleEmbeddingClient(
        sdk_client=embedding_sdk_client,
        model=embedding_config.model,
        dimensions=embedding_config.dimensions,
        batch_size=embedding_config.batch_size,
    )

    vector_store = InMemoryVectorStore()

    job_analysis_service = JobAnalysisService(
        llm_client=llm_client,
    )
    document_indexer = DocumentIndexer(
        embedding_client=embedding_client,
        vector_store=vector_store,
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
    )
    retriever = Retriever(
        embedding_client=embedding_client,
        vector_store=vector_store,
    )
    rag_answer_service = RAGAnswerService(
        retriever=retriever,
        chat_model_client=llm_client,
        top_k=RAG_TOP_K,
        max_output_tokens=RAG_MAX_OUTPUT_TOKENS,
    )

    app.state.job_analysis_service = (
        job_analysis_service
    )
    app.state.document_indexer = document_indexer
    app.state.rag_answer_service = rag_answer_service

    try:
        yield
    finally:
        await asyncio.gather(
            kimi_sdk_client.close(),
            embedding_sdk_client.close(),
        )


app = FastAPI(
    title="岗位分析与RAG API",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(job_router)
app.include_router(rag_router)
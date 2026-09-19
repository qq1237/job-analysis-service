import asyncio

from job_analysis.rag.models import Document
from job_analysis.rag.services import DocumentIndexer, Retriever
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

import pytest
from pydantic import ValidationError

from job_analysis.rag.models import Chunk, Document


def test_valid_document_strips_whitespace() -> None:
    document = Document(
        document_id="  job-001  ",
        content="  招聘RAG工程师  ",
    )

    assert document.document_id == "job-001"
    assert document.content == "招聘RAG工程师"
    assert document.metadata == {}


def test_document_metadata_is_independent() -> None:
    document_a = Document(
        document_id="job-001",
        content="岗位A",
    )
    document_b = Document(
        document_id="job-002",
        content="岗位B",
    )

    document_a.metadata["company"] = "公司A"

    assert document_a.metadata == {
        "company": "公司A",
    }
    assert document_b.metadata == {}


def test_blank_document_content_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        Document(
            document_id="job-001",
            content="   ",
        )


def test_negative_chunk_index_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        Chunk(
            chunk_id="job-001:0",
            document_id="job-001",
            content="要求熟悉RAG",
            chunk_index=-1,
        )
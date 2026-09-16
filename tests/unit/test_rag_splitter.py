from contourpy import chunk

from job_analysis.rag.models import Document
from job_analysis.rag.splitter import split_document

import pytest

def test_split_document_creates_expected_chunks() -> None:
    document = Document(
        document_id="doc-001",
        content="abcdefghijklmnopqrstuv",
        metadata={"source": "test"},
    )

    chunks = split_document(
        document=document,
        chunk_size=10,
        chunk_overlap=2,
    )

    assert len(chunks) == 3

    assert [chunk.content for chunk in chunks] == [
        "abcdefghij",
        "ijklmnopqr",
        "qrstuv",
    ]

    assert [chunk.chunk_index for chunk in chunks] == [0, 1, 2]

    assert [chunk.chunk_id for chunk in chunks] == [
        "doc-001-chunk-0000",
        "doc-001-chunk-0001",
        "doc-001-chunk-0002",
    ]

    assert all(
        chunk.document_id == document.document_id
        for chunk in chunks
    )

@pytest.mark.parametrize(
    ("chunk_size", "chunk_overlap"),
    [
        (0, 0),  # chunk_size 不能等于 0
        (-1, 0),  # chunk_size 不能小于 0
        (10, -1),  # chunk_overlap 不能小于 0
        (10, 10),  # overlap 不能等于 size
        (10, 11),  # overlap 不能大于 size
    ],
)
def test_split_document_rejects_invalid_parameters(
        chunk_size: int,
        chunk_overlap: int,
) -> None:
    document = Document(
        document_id="doc-001",
        content="abcdefghijklmnopqrstuv",
    )

    with pytest.raises(ValueError):
        split_document(
            document=document,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
def test_split_document_one_chunk()-> None:
    document = Document(
        document_id="doc-001",
        content="abc",
        metadata={"source": "test"},
    )
    chunks = split_document(
        document=document,
        chunk_size=10,
        chunk_overlap=2,
    )
    assert len(chunks) == 1
    assert chunks[0].content == document.content
    assert chunks[0].chunk_index == 0

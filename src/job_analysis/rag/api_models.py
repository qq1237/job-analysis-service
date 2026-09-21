from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


NonBlankText = Annotated[
    str,
    Field(min_length=1),
]


class IndexDocumentRequest(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    document_id: NonBlankText
    content: NonBlankText
    metadata: dict[str, str] = Field(default_factory=dict)


class IndexDocumentResponse(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    document_id: NonBlankText
    indexed_chunk_count: int = Field(ge=0)


class RAGQuestionRequest(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    question: NonBlankText

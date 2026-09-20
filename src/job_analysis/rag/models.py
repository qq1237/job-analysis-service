from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


NonBlankText = Annotated[
    str,
    Field(min_length=1),
]


class Document(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    document_id: NonBlankText
    content: NonBlankText
    metadata: dict[str, str] = Field(
        default_factory=dict,
    )


class Chunk(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    chunk_id: NonBlankText
    document_id: NonBlankText
    content: NonBlankText
    chunk_index: int = Field(ge=0)
    metadata: dict[str, str] = Field(
        default_factory=dict,
    )

class EmbeddedChunk(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    chunk: Chunk
    vector: list[float] = Field(min_length=1)


class SearchResult(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
    )

    chunk: Chunk
    score: float
class RAGAnswer(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    answer: NonBlankText
    sources: list[NonBlankText] = Field(
        default_factory=list,
    )

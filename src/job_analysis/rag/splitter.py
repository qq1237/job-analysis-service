
from .models import Chunk, Document
def split_document(
    document: Document,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")
    if chunk_overlap>=chunk_size:
        raise ValueError("Chunk overlap must be less than chunk_size")
    chunks = []
    start = 0
    chunk_index = 0
    step = chunk_size - chunk_overlap
    while start < len(document.content):
        end = min(start + chunk_size, len(document.content))
        str1 = document.content[start:end]
        chunk =Chunk(
            content=str1,
            document_id=document.document_id,
            metadata=document.metadata.copy(),
            chunk_index=chunk_index,
            chunk_id=f"{document.document_id}-chunk-{chunk_index:04d}"        )
        chunks.append(chunk)
        if end >= len(document.content):
            break
        start += step
        chunk_index += 1
    return chunks



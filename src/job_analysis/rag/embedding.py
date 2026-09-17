'''
这个模块负责组织向量化流程：
list[Chunk]
→ 提取 list[str]
→ 调用 EmbeddingClient
→ 检查返回数量
→ 组合成 list[EmbeddedChunk]
'''
from .models import Chunk, EmbeddedChunk
from .protocols import EmbeddingClient


async def embed_chunks(
    chunks: list[Chunk],
    embedding_client: EmbeddingClient,
) -> list[EmbeddedChunk]:
    if not chunks:
        return []

    texts = [chunk.content for chunk in chunks]
    vectors = await embedding_client.embed(texts)

    if len(vectors) != len(chunks):
        raise ValueError(
            "embedding count does not match chunk count"
        )

    embedded_chunks: list[EmbeddedChunk] = []

    for chunk, vector in zip(chunks, vectors):
        embedded_chunk = EmbeddedChunk(
            chunk=chunk,
            vector=vector,
        )
        embedded_chunks.append(embedded_chunk)

    return embedded_chunks
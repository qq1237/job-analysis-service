from uuid import NAMESPACE_URL, uuid5

from qdrant_client import AsyncQdrantClient, models

from .models import Chunk, EmbeddedChunk, SearchResult


class QdrantVectorStore:
    def __init__(
        self,
        client: AsyncQdrantClient,
        collection_name: str,
        vector_size: int,
    ) -> None:
        cleaned_collection_name = collection_name.strip()

        if not cleaned_collection_name:
            raise ValueError(
                "collection_name must not be empty"
            )

        if vector_size <= 0:
            raise ValueError(
                "vector_size must be greater than 0"
            )

        self._client = client
        self._collection_name = cleaned_collection_name
        self._vector_size = vector_size

    async def initialize(self) -> None:
        collection_exists = (
            await self._client.collection_exists(
                collection_name=self._collection_name,
            )
        )

        if collection_exists:
            return

        await self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=models.VectorParams(
                size=self._vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    async def upsert(
        self,
        embedded_chunks: list[EmbeddedChunk],
    ) -> None:
        if not embedded_chunks:
            return

        points: list[models.PointStruct] = []

        for embedded_chunk in embedded_chunks:
            if (
                len(embedded_chunk.vector)
                != self._vector_size
            ):
                raise ValueError(
                    "embedded chunk vector dimension "
                    f"must be {self._vector_size}"
                )

            chunk = embedded_chunk.chunk

            point = models.PointStruct(
                id=self._build_point_id(chunk.chunk_id),
                vector=embedded_chunk.vector,
                payload=chunk.model_dump(mode="json"),
            )
            points.append(point)

        await self._client.upsert(
            collection_name=self._collection_name,
            points=points,
            wait=True,
        )

    async def search(
        self,
        query_vector: list[float],
        top_k: int,
    ) -> list[SearchResult]:
        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0"
            )

        if not query_vector:
            raise ValueError(
                "query_vector must not be empty"
            )

        if len(query_vector) != self._vector_size:
            raise ValueError(
                "query vector dimension "
                f"must be {self._vector_size}"
            )

        response = await self._client.query_points(
            collection_name=self._collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        results: list[SearchResult] = []

        for point in response.points:
            chunk = Chunk.model_validate(
                point.payload or {}
            )

            results.append(
                SearchResult(
                    chunk=chunk,
                    score=float(point.score),
                )
            )

        return results

    @staticmethod
    def _build_point_id(chunk_id: str) -> str:
        return str(
            uuid5(
                NAMESPACE_URL,
                chunk_id,
            )
        )
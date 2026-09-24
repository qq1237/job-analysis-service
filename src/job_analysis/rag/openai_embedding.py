"""Embedding adapter for OpenAI-compatible APIs."""

from openai import APIError, AsyncOpenAI

from job_analysis.exceptions import EmbeddingResponseError


class OpenAICompatibleEmbeddingClient:
    def __init__(
        self,
        sdk_client: AsyncOpenAI,
        model: str,
        dimensions: int,
        batch_size: int,
    ) -> None:
        if not model.strip():
            raise ValueError("embedding model must not be empty")

        if dimensions <= 0:
            raise ValueError(
                "embedding dimensions must be greater than 0"
            )

        if batch_size <= 0:
            raise ValueError(
                "embedding batch_size must be greater than 0"
            )

        self._sdk_client = sdk_client
        self._model = model
        self._dimensions = dimensions
        self._batch_size = batch_size

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        vectors: list[list[float]] = []

        for start in range(
            0,
            len(texts),
            self._batch_size,
        ):
            batch = texts[
                start : start + self._batch_size
            ]

            try:
                response = (
                    await self._sdk_client.embeddings.create(
                        model=self._model,
                        input=batch,
                        dimensions=self._dimensions,
                        encoding_format="float",
                    )
                )
            except APIError as exc:
                raise EmbeddingResponseError(
                    "Embedding服务调用失败"
                ) from exc

            items = sorted(
                response.data,
                key=lambda item: item.index,
            )

            if len(items) != len(batch):
                raise EmbeddingResponseError(
                    "Embedding返回数量与输入数量不一致"
                )

            expected_indices = list(range(len(batch)))
            actual_indices = [
                item.index
                for item in items
            ]

            if actual_indices != expected_indices:
                raise EmbeddingResponseError(
                    "Embedding响应索引无效"
                )

            for item in items:
                vector = item.embedding

                if len(vector) != self._dimensions:
                    raise EmbeddingResponseError(
                        "Embedding向量维度不符合配置"
                    )

                vectors.append(vector)

        return vectors

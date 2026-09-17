from typing import Protocol


class EmbeddingClient(Protocol):
    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        ...
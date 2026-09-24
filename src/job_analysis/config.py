import os
from dataclasses import dataclass, field


@dataclass
class KimiConfig:
    """Kimi模型连接配置。"""

    api_key: str = field(repr=False)
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "kimi-k2.6"


@dataclass
class EmbeddingConfig:
    """Embedding模型连接配置。"""

    api_key: str = field(repr=False)
    base_url: str = (
        "https://dashscope.aliyuncs.com/"
        "compatible-mode/v1"
    )
    model: str = "text-embedding-v4"
    dimensions: int = 1024
    batch_size: int = 10


def load_kimi_config() -> KimiConfig:
    """从环境变量加载Kimi配置并尽早验证密钥。"""

    api_key = os.getenv("MOONSHOT_API_KEY")

    if api_key is None or not api_key.strip():
        raise RuntimeError("未配置MOONSHOT_API_KEY")

    return KimiConfig(
        api_key=api_key.strip(),
        base_url=os.getenv(
            "MOONSHOT_BASE_URL",
            "https://api.moonshot.cn/v1",
        ).strip(),
        model=os.getenv(
            "MOONSHOT_MODEL",
            "kimi-k2.6",
        ).strip(),
    )


def _load_integer(
    name: str,
    default: int,
) -> int:
    raw_value = os.getenv(name, str(default))

    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(
            f"{name}必须是整数"
        ) from exc


def load_embedding_config() -> EmbeddingConfig:
    """从环境变量加载Embedding配置并尽早验证。"""

    api_key = os.getenv("EMBEDDING_API_KEY")

    if api_key is None or not api_key.strip():
        raise RuntimeError("未配置EMBEDDING_API_KEY")

    base_url = os.getenv(
        "EMBEDDING_BASE_URL",
        (
            "https://dashscope.aliyuncs.com/"
            "compatible-mode/v1"
        ),
    ).strip()
    model = os.getenv(
        "EMBEDDING_MODEL",
        "text-embedding-v4",
    ).strip()
    dimensions = _load_integer(
        "EMBEDDING_DIMENSIONS",
        1024,
    )
    batch_size = _load_integer(
        "EMBEDDING_BATCH_SIZE",
        10,
    )

    if not base_url:
        raise RuntimeError(
            "EMBEDDING_BASE_URL不能为空"
        )

    if not model:
        raise RuntimeError(
            "EMBEDDING_MODEL不能为空"
        )

    if dimensions <= 0:
        raise RuntimeError(
            "EMBEDDING_DIMENSIONS必须大于0"
        )

    if not 1 <= batch_size <= 10:
        raise RuntimeError(
            "EMBEDDING_BATCH_SIZE必须在1到10之间"
        )

    return EmbeddingConfig(
        api_key=api_key.strip(),
        base_url=base_url,
        model=model,
        dimensions=dimensions,
        batch_size=batch_size,
    )
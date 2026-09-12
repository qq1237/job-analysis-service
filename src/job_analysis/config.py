import os
from dataclasses import dataclass, field


@dataclass
class KimiConfig:
    """Kimi模型连接配置。"""

    api_key: str = field(repr=False)
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "kimi-k2.6"


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
        ),
        model=os.getenv(
            "MOONSHOT_MODEL",
            "kimi-k2.6",
        ),
    )

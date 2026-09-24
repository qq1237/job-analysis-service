class LLMResponseError(RuntimeError):
    """模型响应无法被应用使用。"""

    pass


class JobAnalysisParseError(RuntimeError):
    """模型输出无法解析为岗位分析结果。"""

    pass


class EmbeddingResponseError(RuntimeError):
    """Embedding服务返回了无法使用的结果。"""

    pass

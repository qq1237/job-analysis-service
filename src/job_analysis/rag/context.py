'''
文件位置：
src/job_analysis/rag/context.py

函数名称：
build_context

模块职责：
把按相关性排序的 SearchResult 转换为清晰、稳定的上下文字符串

输入类型：
list[SearchResult]

输出类型：
str

空列表行为：
    返回空字符串 ""

单个片段格式
    [资料 1]
来源：job-001
内容：要求熟悉 Python 和 FastAPI。
'''
from .models import SearchResult


def build_context(
    search_results: list[SearchResult],
) -> str:
    if not search_results:
        return ""

    sections: list[str] = []

    for index, result in enumerate(search_results, start=1):
        chunk = result.chunk
        source = (
            chunk.metadata.get("source")
            or chunk.document_id
        )

        section = (
            f"[资料 {index}]\n"
            f"来源：{source}\n"
            f"内容：{chunk.content}"
        )
        sections.append(section)

    return "\n\n".join(sections)
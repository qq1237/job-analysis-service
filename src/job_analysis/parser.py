import json

from pydantic import ValidationError

from job_analysis.exceptions import JobAnalysisParseError
from job_analysis.models import JobAnalysis


def parse_job_analysis(
    model_text: str,
) -> JobAnalysis:
    """将模型文本解析并验证为岗位分析结果。"""

    try:
        parsed_data = json.loads(model_text)
        return JobAnalysis.model_validate(parsed_data)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise JobAnalysisParseError(
            "模型输出不是有效的岗位分析结果"
        ) from exc

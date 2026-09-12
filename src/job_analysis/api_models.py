from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


NonBlankText = Annotated[
    str,
    Field(min_length=1),
]


class JobAnalysisRequest(BaseModel):
    """岗位分析接口的请求数据。"""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    job_text: NonBlankText
    candidate_skills: list[NonBlankText] = Field(
        min_length=1,
    )

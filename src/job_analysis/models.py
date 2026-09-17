from pydantic import BaseModel, ConfigDict, Field


class JobAnalysis(BaseModel):
    """岗位技能分析结果。"""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    matched_skills: list[str]
    missing_skills: list[str]
    summary: str = Field(min_length=1)



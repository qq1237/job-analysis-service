import json

import pytest
from pydantic import ValidationError

from job_analysis.exceptions import JobAnalysisParseError
from job_analysis.models import JobAnalysis
from job_analysis.parser import parse_job_analysis


def test_valid_json_returns_job_analysis() -> None:
    model_text = json.dumps(
        {
            "matched_skills": ["Python"],
            "missing_skills": ["RAG"],
            "summary": "需要补充RAG",
        },
        ensure_ascii=False,
    )

    result = parse_job_analysis(model_text)

    assert isinstance(result, JobAnalysis)
    assert result.matched_skills == ["Python"]
    assert result.missing_skills == ["RAG"]
    assert result.summary == "需要补充RAG"


def test_invalid_json_raises_job_analysis_parse_error() -> None:
    text = "我不是JSON"

    with pytest.raises(JobAnalysisParseError) as excinfo:
        parse_job_analysis(text)

    assert isinstance(
        excinfo.value.__cause__,
        json.JSONDecodeError,
    )


def test_missing_field_raises_job_analysis_parse_error() -> None:
    model_text = json.dumps(
        {
            "matched_skills": ["Python"],
            "summary": "缺少missing_skills字段",
        },
        ensure_ascii=False,
    )

    with pytest.raises(JobAnalysisParseError) as excinfo:
        parse_job_analysis(model_text)

    assert isinstance(
        excinfo.value.__cause__,
        ValidationError,
    )

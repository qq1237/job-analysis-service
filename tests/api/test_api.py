import pytest
from fastapi.testclient import TestClient

from job_analysis.api import get_job_analysis_service
from job_analysis.exceptions import JobAnalysisParseError, LLMResponseError
from job_analysis.main import app
from job_analysis.models import JobAnalysis


VALID_PAYLOAD = {
    "job_text": "招聘RAG工程师",
    "candidate_skills": ["Python"],
}


class SuccessfulJobAnalysisService:
    async def analyze(
        self,
        job_text: str,
        candidate_skills: list[str],
    ) -> JobAnalysis:
        return JobAnalysis(
            matched_skills=["Python"],
            missing_skills=["RAG"],
            summary="需要补充RAG",
        )


class ParseFailingJobAnalysisService:
    async def analyze(
        self,
        job_text: str,
        candidate_skills: list[str],
    ) -> JobAnalysis:
        raise JobAnalysisParseError("测试解析失败")


class LLMFailingJobAnalysisService:
    async def analyze(
        self,
        job_text: str,
        candidate_skills: list[str],
    ) -> JobAnalysis:
        raise LLMResponseError("测试模型响应失败")


class CountingJobAnalysisService:
    def __init__(self) -> None:
        self.call_count = 0

    async def analyze(
        self,
        job_text: str,
        candidate_skills: list[str],
    ) -> JobAnalysis:
        self.call_count += 1
        return JobAnalysis(
            matched_skills=[],
            missing_skills=[],
            summary="不应执行",
        )


def post_job_analysis_with_service(
    service: object,
    payload: dict[str, object] | None = None,
):
    def override_service() -> object:
        return service

    app.dependency_overrides[
        get_job_analysis_service
    ] = override_service
    client = TestClient(app)

    try:
        return client.post(
            "/job-analyses",
            json=payload or VALID_PAYLOAD,
        )
    finally:
        client.close()
        app.dependency_overrides.clear()


def test_health_returns_ok() -> None:
    client = TestClient(app)

    try:
        response = client.get("/health")
    finally:
        client.close()

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_successful_service_returns_200() -> None:
    response = post_job_analysis_with_service(
        SuccessfulJobAnalysisService()
    )

    assert response.status_code == 200
    assert response.json() == {
        "matched_skills": ["Python"],
        "missing_skills": ["RAG"],
        "summary": "需要补充RAG",
    }


def test_empty_skills_returns_422_without_calling_service() -> None:
    service = CountingJobAnalysisService()

    response = post_job_analysis_with_service(
        service,
        payload={
            "job_text": "招聘RAG工程师",
            "candidate_skills": [],
        },
    )

    assert response.status_code == 422
    assert service.call_count == 0


@pytest.mark.parametrize(
    "service",
    [
        ParseFailingJobAnalysisService(),
        LLMFailingJobAnalysisService(),
    ],
)
def test_known_model_failure_returns_502(service: object) -> None:
    response = post_job_analysis_with_service(service)

    assert response.status_code == 502
    assert response.json() == {
        "detail": "模型返回了无法使用的结果"
    }

import json

from fastapi.testclient import TestClient

from job_analysis.api import get_job_analysis_service
from job_analysis.llm.models import ChatRequest
from job_analysis.main import app
from job_analysis.service import JobAnalysisService


class StaticLLMClient:
    async def generate(self, request: ChatRequest) -> str:
        assert request.response_format == "json_object"
        assert "招聘RAG工程师" in request.messages[1].content

        return json.dumps(
            {
                "matched_skills": ["Python"],
                "missing_skills": ["RAG"],
                "summary": "需要补充RAG",
            },
            ensure_ascii=False,
        )


def test_http_request_runs_real_job_analysis_workflow() -> None:
    service = JobAnalysisService(
        StaticLLMClient(),
        max_attempts=1,
    )

    def override_service() -> JobAnalysisService:
        return service

    app.dependency_overrides[
        get_job_analysis_service
    ] = override_service
    client = TestClient(app)

    try:
        response = client.post(
            "/job-analyses",
            json={
                "job_text": "招聘RAG工程师",
                "candidate_skills": ["Python"],
            },
        )
    finally:
        client.close()
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["matched_skills"] == ["Python"]
    assert response.json()["missing_skills"] == ["RAG"]

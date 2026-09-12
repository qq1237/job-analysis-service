from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from job_analysis.api_models import JobAnalysisRequest
from job_analysis.exceptions import JobAnalysisParseError, LLMResponseError
from job_analysis.models import JobAnalysis
from job_analysis.service import JobAnalysisService


router = APIRouter()


def get_job_analysis_service(
    http_request: Request,
) -> JobAnalysisService:
    """取得应用启动时创建的共享Service。"""

    return http_request.app.state.job_analysis_service


JobAnalysisServiceDep = Annotated[
    JobAnalysisService,
    Depends(get_job_analysis_service),
]


@router.get("/health")
async def health() -> dict[str, str]:
    """检查Web服务是否正常运行。"""

    return {"status": "ok"}


@router.post(
    "/job-analysis-requests/validate",
    response_model=JobAnalysisRequest,
)
async def validate_job_analysis_request(
    payload: JobAnalysisRequest,
) -> JobAnalysisRequest:
    """只验证请求数据，不调用模型。"""

    return payload


@router.post(
    "/job-analyses",
    response_model=JobAnalysis,
)
async def analyze_job(
    payload: JobAnalysisRequest,
    service: JobAnalysisServiceDep,
) -> JobAnalysis:
    """分析岗位要求与候选人技能的匹配情况。"""

    try:
        return await service.analyze(
            job_text=payload.job_text,
            candidate_skills=payload.candidate_skills,
        )
    except (LLMResponseError, JobAnalysisParseError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="模型返回了无法使用的结果",
        ) from exc

from job_analysis.exceptions import JobAnalysisParseError
from job_analysis.llm.models import ChatRequest
from job_analysis.llm.protocols import ChatModelClient
from job_analysis.models import JobAnalysis
from job_analysis.parser import parse_job_analysis
from job_analysis.prompts import build_job_analysis_messages


class JobAnalysisService:
    """组织岗位分析业务工作流。"""

    def __init__(
        self,
        llm_client: ChatModelClient,
        max_attempts: int = 2,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts必须大于等于1")

        self._llm_client = llm_client
        self._max_attempts = max_attempts

    async def analyze(
        self,
        job_text: str,
        candidate_skills: list[str],
    ) -> JobAnalysis:
        messages = build_job_analysis_messages(
            job_text,
            candidate_skills,
        )
        request = ChatRequest(
            messages=messages,
            response_format="json_object",
            max_output_tokens=512,
        )

        for attempt in range(1, self._max_attempts + 1):
            model_text = await self._llm_client.generate(request)

            try:
                return parse_job_analysis(model_text)
            except JobAnalysisParseError:
                if attempt == self._max_attempts:
                    raise

        raise RuntimeError("岗位分析流程到达不可达分支")

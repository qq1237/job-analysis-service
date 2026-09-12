# Job Analysis Service

一个面向大模型应用开发学习与实践的岗位分析服务。客户端提交岗位描述和候选人技能后，服务调用Kimi模型，返回已匹配技能、缺失技能和简短总结。

## 功能

- 使用Pydantic验证岗位描述和候选人技能
- 构造受约束的岗位分析提示词
- 通过异步OpenAI兼容SDK调用Kimi
- 将模型JSON文本解析为结构化岗位分析结果
- 将已知模型错误转换为HTTP 502
- 通过依赖注入替换模型或Service，支持离线测试
- 区分单元、API、集成和真实模型测试

## 核心数据流

```text
HTTP JSON
→ JobAnalysisRequest
→ JobAnalysisService
→ list[Message]
→ ChatRequest
→ KimiLLMClient
→ Kimi API
→ 模型文本str
→ parse_job_analysis()
→ JobAnalysis
→ HTTP JSON
```

更完整的模块职责和依赖方向见 [架构说明](docs/architecture.md)。

## 技术栈

- Python 3.11+
- FastAPI
- Pydantic v2
- OpenAI兼容异步SDK
- Kimi
- pytest
- httpx / FastAPI TestClient

## 项目结构

```text
.
├── src/job_analysis/
│   ├── llm/
│   │   ├── kimi.py
│   │   ├── models.py
│   │   └── protocols.py
│   ├── api.py
│   ├── api_models.py
│   ├── config.py
│   ├── exceptions.py
│   ├── main.py
│   ├── models.py
│   ├── parser.py
│   ├── prompts.py
│   └── service.py
├── tests/
│   ├── api/
│   ├── integration/
│   ├── real/
│   └── unit/
├── docs/architecture.md
├── .env.example
└── pyproject.toml
```

## 安装

建议先创建并激活虚拟环境，然后在项目根目录执行：

```powershell
python -m pip install -e ".[dev]"
```

这是可编辑安装。修改 `src/job_analysis` 中的代码后，不需要重新安装项目。

## 配置

复制 `.env.example` 中的变量名称，并在运行环境中配置真实值。当前代码通过 `os.getenv()` 读取系统环境变量，不会自动加载 `.env` 文件。

PowerShell示例：

```powershell
$env:MOONSHOT_API_KEY="your-api-key"
$env:MOONSHOT_BASE_URL="https://api.moonshot.cn/v1"
$env:MOONSHOT_MODEL="kimi-k2.6"
```

不要把真实API Key写进代码、README、测试或Git提交。

## 启动服务

```powershell
uvicorn job_analysis.main:app --reload
```

默认地址：

```text
http://127.0.0.1:8000
```

健康检查：

```text
GET /health
```

岗位分析：

```text
POST /job-analyses
```

请求示例：

```json
{
  "job_text": "招聘大模型应用开发工程师，要求熟悉Python、FastAPI和RAG。",
  "candidate_skills": ["Python", "FastAPI"]
}
```

成功响应示例：

```json
{
  "matched_skills": ["Python", "FastAPI"],
  "missing_skills": ["RAG"],
  "summary": "候选人具备基础接口开发能力，需要补充RAG经验。"
}
```

## 测试

运行默认测试：

```powershell
python -m pytest
```

默认测试不会调用真实Kimi。

显式运行真实模型测试：

```powershell
$env:MOONSHOT_API_KEY="your-api-key"
$env:RUN_REAL_MODEL_TESTS="1"
python -m pytest tests/real -m real_model
```

真实模型测试需要网络和API额度，结果可能受外部服务影响。

## 测试分层

| 目录 | 验证范围 | 是否调用真实Kimi |
|---|---|---|
| `tests/unit` | Parser、Service等单个职责 | 否 |
| `tests/api` | 请求验证、状态码、响应和异常转换 | 否 |
| `tests/integration` | API、Service、Prompt和Parser协作 | 否 |
| `tests/real` | Kimi适配器与外部API | 仅显式开启 |

## 当前限制

- 结构化输出仍使用 `json_object` 加Pydantic验证
- 尚未接入JSON Schema Structured Output
- 尚未记录请求追踪ID、耗时、Token用量和模型指标
- 尚未实现流式输出
- 尚未接入RAG、Workflow和Agent

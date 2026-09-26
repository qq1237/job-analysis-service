# Job Analysis Service

一个用于学习和实践大模型应用开发的 FastAPI 服务。

项目目前包含两项主要能力：

1. 调用 Kimi 分析岗位要求与候选人技能的匹配情况。
2. 使用 DashScope Embedding 和 Qdrant 构建可持久化的 RAG 知识库问答服务。

## 功能

### 岗位匹配分析

- 验证岗位描述和候选人技能
- 构造岗位分析提示词
- 调用 Kimi 生成分析结果
- 将模型文本解析为结构化数据
- 返回已匹配技能、缺失技能和总结

### RAG 知识库问答

- 接收并切分文档
- 批量生成文本向量
- 将向量和文档片段写入 Qdrant
- 根据问题向量检索相关片段
- 构造受约束的 RAG 上下文和提示词
- 调用 Kimi 生成基于知识库的回答
- 返回答案及资料来源
- 服务重启后保留已索引数据

## RAG 核心流程

### 文档索引

```text
Document
→ split_document
→ list[Chunk]
→ EmbeddingClient
→ list[EmbeddedChunk]
→ VectorStore.upsert
→ Qdrant磁盘
```

### 问题回答

```text
Question
→ Retriever
→ 问题向量
→ VectorStore.search
→ list[SearchResult]
→ build_context
→ build_rag_messages
→ Kimi
→ RAGAnswer(answer, sources)
```

更完整的模块职责和依赖关系见
[架构说明](docs/architecture.md)。

## 技术栈

- Python 3.11+
- FastAPI
- Pydantic v2
- OpenAI 兼容异步 SDK
- Kimi
- DashScope `text-embedding-v4`
- Qdrant
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
│   ├── rag/
│   │   ├── api.py
│   │   ├── api_models.py
│   │   ├── context.py
│   │   ├── embedding.py
│   │   ├── models.py
│   │   ├── openai_embedding.py
│   │   ├── prompts.py
│   │   ├── protocols.py
│   │   ├── qdrant_vector_store.py
│   │   ├── services.py
│   │   ├── similarity.py
│   │   ├── splitter.py
│   │   └── vector_store.py
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
├── docs/
│   └── architecture.md
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

当前代码通过 `os.getenv()` 读取系统环境变量，不会自动加载 `.env` 文件。

可参考 `.env.example` 配置以下变量：

| 变量 | 默认值或用途 |
|---|---|
| `MOONSHOT_API_KEY` | Kimi API Key，必填 |
| `MOONSHOT_BASE_URL` | `https://api.moonshot.cn/v1` |
| `MOONSHOT_MODEL` | `kimi-k2.6` |
| `EMBEDDING_API_KEY` | DashScope API Key，必填 |
| `EMBEDDING_BASE_URL` | DashScope OpenAI 兼容地址 |
| `EMBEDDING_MODEL` | `text-embedding-v4` |
| `EMBEDDING_DIMENSIONS` | `1024` |
| `EMBEDDING_BATCH_SIZE` | `10` |
| `QDRANT_PATH` | `./data/qdrant` |
| `QDRANT_COLLECTION_NAME` | `job_documents` |

PowerShell 示例：

```powershell
$env:MOONSHOT_API_KEY="your-moonshot-api-key"
$env:EMBEDDING_API_KEY="your-dashscope-api-key"
```

不要把真实 API Key 写进代码、README、测试或 Git 提交。

## 启动服务

在项目根目录运行：

```powershell
python -m uvicorn job_analysis.main:app
```

默认地址：

```text
http://127.0.0.1:8000
```

Swagger API 文档：

```text
http://127.0.0.1:8000/docs
```

当前使用本地 Qdrant 存储。请使用单进程启动，不要让多个 Uvicorn worker 同时打开同一个 Qdrant 目录。

## API

### 健康检查

```text
GET /health
```

响应：

```json
{
  "status": "ok"
}
```

### 岗位匹配分析

```text
POST /job-analyses
```

请求：

```json
{
  "job_text": "招聘大模型应用开发工程师，要求熟悉Python、FastAPI和RAG。",
  "candidate_skills": [
    "Python",
    "FastAPI"
  ]
}
```

响应示例：

```json
{
  "matched_skills": [
    "Python",
    "FastAPI"
  ],
  "missing_skills": [
    "RAG"
  ],
  "summary": "候选人具备基础接口开发能力，需要补充RAG经验。"
}
```

### 写入 RAG 文档

```text
POST /rag/documents
```

请求：

```json
{
  "document_id": "job-001",
  "content": "该岗位要求掌握Python、FastAPI、RAG和向量数据库。",
  "metadata": {
    "source": "job-board"
  }
}
```

响应：

```json
{
  "document_id": "job-001",
  "indexed_chunk_count": 1
}
```

### RAG 问答

```text
POST /rag/questions
```

请求：

```json
{
  "question": "这个岗位要求掌握哪些技术？"
}
```

响应示例：

```json
{
  "answer": "该岗位要求掌握Python、FastAPI、RAG和向量数据库。",
  "sources": [
    "job-board"
  ]
}
```

当没有检索到可用资料时，服务返回：

```json
{
  "answer": "根据现有知识库无法回答该问题。",
  "sources": []
}
```

## 持久化行为

生产组装使用 `QdrantVectorStore`，数据默认保存在：

```text
./data/qdrant
```

服务关闭并重新启动后，只要以下配置保持一致，原有数据仍然可以检索：

- `QDRANT_PATH`
- `QDRANT_COLLECTION_NAME`
- `EMBEDDING_DIMENSIONS`

`data/qdrant` 是本地运行数据，已被 `.gitignore` 排除，不应提交到 Git。

## 测试

运行默认测试：

```powershell
python -m pytest -q
```

默认测试不调用真实模型服务。

运行真实 Kimi 测试：

```powershell
$env:RUN_REAL_MODEL_TESTS="1"
python -m pytest tests/real/test_kimi.py -m real_model
```

运行真实 Embedding 测试：

```powershell
$env:RUN_REAL_EMBEDDING_TESTS="1"
python -m pytest tests/real/test_embedding.py -m real_model
```

真实测试需要网络和 API 额度。

## 测试分层

| 目录 | 验证范围 | 是否调用外部服务 |
|---|---|---|
| `tests/unit` | 模型、切分、向量计算和单个职责 | 否 |
| `tests/api` | HTTP 请求、响应和异常转换 | 否 |
| `tests/integration` | Service、RAG 流程及 Qdrant 持久化 | 否 |
| `tests/real` | Kimi 与 DashScope 真实适配器 | 仅显式开启 |

## 关键设计

- Service 依赖协议，不直接依赖具体供应商。
- `DocumentIndexer` 和 `Retriever` 共享同一个向量库。
- Embedding 和 Qdrant Collection 使用相同向量维度。
- 测试可以注入假模型、假 Embedding 和内存向量库。
- Qdrant Point ID 根据 `chunk_id` 稳定生成，重复索引时执行更新。

## 当前限制

- 本地 Qdrant 适合学习、开发和单进程运行，尚未部署独立 Qdrant Server。
- 尚未提供删除文档和按文档整体更新的接口。
- 尚未实现关键词与向量混合检索。
- 尚未接入 Reranker 和 RAG 效果评估。
- 尚未实现对话历史和用户知识库隔离。
- 尚未记录 Token 用量、耗时和完整调用链。
- 尚未实现流式输出。
- 尚未接入 Workflow 和 Agent。
- 
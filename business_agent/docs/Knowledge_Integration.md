# Knowledge Integration

Business Agent 通过 `KnowledgeClient` 访问 Knowledge Capability，不直接依赖 Wiki、Repository、向量库或检索实现。

## Provider

- `mock`：本地 Contract Fixture
- `capability` / `http`：跨进程 HTTP 调用

## HTTP

- Health：`GET /health`
- Query：`POST /v1/knowledge/query`

推荐通过环境变量配置：

```text
KNOWLEDGE_PROVIDER
KNOWLEDGE_BASE_URL
KNOWLEDGE_SEARCH_ENDPOINT
KNOWLEDGE_TIMEOUT_SECONDS
KNOWLEDGE_API_TOKEN（可选）
```

联调前先执行：

```bash
python scripts/check_health.py
python scripts/check_contract.py
```

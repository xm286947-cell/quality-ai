# BUSINESS_AGENT_ENGINE_V1.2_M1_P02_Increment01

Scope:
Contract Adapter Layer

Files:
- adapters/__init__.py
- adapters/request_adapter.py
- adapters/response_adapter.py
- adapters/trace_adapter.py

Purpose:
Bridge QUALITY_AGENT_CONTRACT V1.0 models and runtime internal models.


# BUSINESS_AGENT_ENGINE

QUALITY_AGENT 平台的统一业务智能体运行时。当前工程已接入 `REPEAT_CASE` 插件，并具备通过 `QUALITY_AGENT_CONTRACT V1.0` 调用 Knowledge Capability 的基础能力。

## 当前版本

- Version：V1.1 RC
- Status：Ready for Integration Test
- Supported Agent：`repeat_case`
- Knowledge Provider：`mock` / `capability`
- Knowledge HTTP API：`POST /v1/knowledge/query`

## 1. 环境准备

建议使用 Python 3.10 或更高版本。

```bash
python -m pip install -r requirements.txt
```

## 2. 查看已注册 Agent

```bash
python main.py list-agents
```

预期可看到：

```text
repeat_case
```

## 3. 运行 REPEAT_CASE

最小命令：

```bash
python main.py run-agent --agent repeat_case --input input/new_cases.xlsx --mock
```

使用指定 Query：

```bash
python main.py run-agent --agent repeat_case --query-id <QUERY_ID> --mock
```

查看完整参数：

```bash
python main.py run-agent --help
```

运行结果与 Trace 默认写入 `output/`。

## 4. Knowledge Capability 联调

### 4.1 启动 Knowledge Capability

在 Knowledge Capability 工程目录执行：

```bash
python -m knowledge_capability.api
```

健康检查：

```bash
curl http://127.0.0.1:8080/health
```

### 4.2 配置 Business Agent

Linux/macOS：

```bash
export KNOWLEDGE_PROVIDER=capability
export KNOWLEDGE_BASE_URL=http://127.0.0.1:8080
export KNOWLEDGE_SEARCH_ENDPOINT=/v1/knowledge/query
export KNOWLEDGE_TIMEOUT_SECONDS=30
```

Windows PowerShell：

```powershell
$env:KNOWLEDGE_PROVIDER="capability"
$env:KNOWLEDGE_BASE_URL="http://127.0.0.1:8080"
$env:KNOWLEDGE_SEARCH_ENDPOINT="/v1/knowledge/query"
$env:KNOWLEDGE_TIMEOUT_SECONDS="30"
```

随后运行：

```bash
python main.py run-agent --agent repeat_case --input input/new_cases.xlsx --mock
```

> `--mock` 仅控制 REPEAT_CASE 内部 AI 阶段；Knowledge Provider 由上述环境变量控制。

也可参考：`config/knowledge.integration.example.yaml`。

## 5. 常用检查

```bash
python scripts/check_health.py
python scripts/check_contract.py
python scripts/run_e2e.py --input input/new_cases.xlsx
```

## 6. 工程结构

```text
business_agent/   平台 Runtime、Workflow、Knowledge、Result、Trace
plugins/          业务智能体插件
contracts/        QUALITY_AGENT_CONTRACT Schema
config/           业务与联调配置
examples/         最小运行示例
docs/             长期维护文档
scripts/          通用检查与联调脚本
tests/            自动化测试
main.py           统一 CLI 入口
```

## 7. 文档入口

- [架构概览](docs/Architecture.md)
- [Knowledge 联调](docs/Knowledge_Integration.md)
- [插件开发](docs/Plugin_Development.md)
- [开发与测试](docs/Development_Guide.md)

历史交付与旧版说明已归档到 `docs/history/`，不再作为当前工程使用入口。

### Contract 请求形态

Business Agent 通过 `POST /v1/knowledge/query` 发送冻结的 V1.0 请求。核心字段示例：

```json
{
  "contract_version": "V1.0",
  "request_id": "req-001",
  "service_id": "repeat_case_service",
  "query": {"text": "CAN接收拥堵导致软件保护重启"},
  "filters": {},
  "requested_fields": [],
  "options": {"top_k": 5},
  "caller": {"type": "business_agent", "agent_id": "repeat_case"}
}
```

## BUSINESS_AGENT Workflow V1

The REPEAT_CASE platform workflow is now fixed as:

```text
parse_input -> knowledge_search -> repeat_case_analysis
```

`input.parse` converts Excel/JSON input into stable `CaseInput` objects stored in `runtime context.cases`. Knowledge access is performed once per case using `case.query_text`; empty query text fails before any HTTP request.

## HTTP Service E2E（正式联调方式）

启动 Business Agent 服务：

```bash
python -m business_agent.api
```

默认监听 `0.0.0.0:8080`。健康检查：

```bash
curl http://127.0.0.1:8080/health
```

通过 HTTP 上传 Excel 并在服务侧完成解析、Knowledge 调用和分析：

```bash
python scripts/run_e2e.py \
  --base-url http://127.0.0.1:8080 \
  --input input/new_cases.xlsx \
  --top-k 5
```

等价 curl：

```bash
curl -X POST http://127.0.0.1:8080/v1/agents/repeat_case/run \
  -F "file=@input/new_cases.xlsx" \
  -F "top_k=5" \
  -F "overwrite=true" \
  -F "mock=false"
```

`run_e2e.py` 现在只通过 HTTP 与 Business Agent 通信，不再调用本地 `main.py run-agent`。旧本地执行脚本已更名为 `scripts/run_local_e2e.py`。

## REPEAT_CASE 真实 HTTP 联调

本版本默认要求 REPEAT_CASE 通过 Business Agent API 接收文件，并通过 HTTP 调用 Knowledge Capability。`scripts/run_e2e.py` 不再调用本地 Runtime。

```bash
# 终端1：启动 Knowledge Capability（默认 8000）
python -m knowledge_capability.api

# 终端2：启动 Business Agent（默认 8080）
python -m business_agent.api

# 终端3：真实 HTTP E2E
python scripts/run_e2e.py \
  --base-url http://127.0.0.1:8080 \
  --knowledge-base-url http://127.0.0.1:8000 \
  --input input/new_cases.xlsx \
  --top-k 5
```

链路：客户端上传 Excel → Business Agent 服务侧解析 → Knowledge Capability HTTP 查询 → REPEAT_CASE 分析 → Report/Trace。若 Knowledge 服务不可用，E2E 脚本会在运行前直接失败，不会静默降级为 Mock。

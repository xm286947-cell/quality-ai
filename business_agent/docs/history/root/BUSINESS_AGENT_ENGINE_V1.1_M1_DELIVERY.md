# BUSINESS_AGENT_ENGINE V1.1 M1 Delivery

## 目标

基于 REPEAT_CASE_ENGINE V2.4 M6 现有代码，建立 BUSINESS_AGENT_ENGINE V1.1 的第一版平台运行时基础，不重写现有业务链路。

## 本次交付

- Agent Profile Loader：从 `config/agents/*.yaml` 加载业务智能体定义。
- Agent Registry：支持列出已配置 Agent。
- Business Agent Runtime：统一接收请求、加载 Agent、执行 Workflow、返回结果。
- Workflow Engine：按配置顺序执行 Handler Node。
- Handler Registry：将平台 Workflow 与既有业务实现解耦。
- Trace Manager：输出请求级、节点级运行轨迹。
- REPEAT_CASE Adapter：将现有 `run_analysis_pipeline` 接入统一 Runtime。
- CLI：新增 `list-agents` 与 `run-agent`。
- 自动化测试：覆盖 Profile、Agent 列表、Runtime 和 Trace。

## 迁移策略

当前采用 `legacy_pipeline_adapter` 模式：

```text
BUSINESS_AGENT_RUNTIME
        ↓
Agent Profile
        ↓
Workflow Handler
        ↓
RepeatCaseAdapter
        ↓
Existing REPEAT_CASE Analysis Pipeline
```

因此，本阶段不会破坏或重写现有 M7/M8 分析链路。后续可以逐步将 Query、Knowledge、Prompt、LLM、Result 节点拆成公共 Workflow Node。

## 使用方式

列出 Agent：

```bash
python main.py list-agents
```

使用统一 Runtime 运行 REPEAT_CASE：

```bash
python main.py run-agent --agent repeat_case --input input/new_cases.xlsx --mock --overwrite
```

也可以使用 JSON 输入：

```bash
python main.py run-agent --agent repeat_case --input-json request.json
```

## M1 边界

本次完成 Platform Runtime Foundation，不包含：

- Knowledge Capability Contract 的真实远程接入；
- 通用 Prompt Node、Knowledge Node、LLM Node 的完全拆分；
- 并行、分支、条件 Workflow；
- Plugin SDK；
- Portal 接入。

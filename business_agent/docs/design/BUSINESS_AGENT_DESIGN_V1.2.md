# BUSINESS_AGENT_DESIGN

**Version：V1.2**  
**Status：Design Freeze**  
**Design Scope：Business Agent Platform**  
**Design Theme：QUALITY_AGENT_CONTRACT V1.0 Alignment**

---

## 1. Design Position

BUSINESS_AGENT 是 QUALITY_AGENT 平台的公共业务智能体能力。

本设计定义 Business Agent Platform 的统一运行架构，以及业务智能体如何通过配置、工作流和插件接入平台，并通过正式 Contract 消费 Knowledge Capability。

本设计输入包括：

- BUSINESS_AGENT_BASELINE V1.1
- BUSINESS_AGENT_REQUIREMENTS V1.1
- QUALITY_AGENT_CONTRACT V1.0
- BUSINESS_AGENT_ENGINE V1.1 RC 当前实现

本设计不定义：

- 具体业务智能体的业务判断规则
- Knowledge Capability 内部 Provider、Storage、Index 和 Retrieval 实现
- 具体 Prompt 内容
- 具体 LLM Provider
- 具体业务报告内容
- Engine 代码实现细节

本设计回答：

> Business Agent Platform 如何统一承载不同业务智能体，并按照 QUALITY_AGENT_CONTRACT 调用公共能力。

---

## 2. Design Goals

BUSINESS_AGENT Platform 应实现：

1. 统一业务智能体运行入口。
2. 统一 Agent Profile 和生命周期。
3. 统一 Workflow 执行机制。
4. 统一 Workflow Node 执行契约。
5. 统一 Runtime Context。
6. 统一 Plugin 接入方式。
7. 统一 Capability 消费方式。
8. 统一 Result 和 Trace。
9. 隔离业务逻辑与平台运行逻辑。
10. 隔离 Business Agent 与 Knowledge Capability 内部实现。
11. 支持不同业务智能体独立配置、独立接入和独立演进。
12. 支持 REPEAT_CASE、QUALITY_RISK 等业务智能体复用同一平台。

---

## 3. Design Principles

### 3.1 Business Neutral

Business Agent Platform 不写入具体业务规则。

平台只提供：

- Runtime
- Workflow
- Context
- Capability Gateway
- Plugin
- Result
- Trace
- Configuration

具体业务判断由业务 Plugin 完成。

### 3.2 Profile Driven

业务智能体通过 Agent Profile 描述。

```text
Agent = Profile + Workflow + Capability Binding + Plugin
```

Runtime 不应根据 `agent_id` 编写固定业务分支。

### 3.3 Workflow Driven

业务智能体执行过程由 Workflow 编排。

```text
Agent Profile
    ↓
Workflow
    ↓
Workflow Node
    ↓
Handler
```

### 3.4 Plugin Driven

具体业务能力通过 Plugin 接入。

例如：

```text
REPEAT_CASE Plugin
QUALITY_RISK Plugin
QUALITY_REVIEW Plugin
```

平台 Runtime 不实现重复问题判断、质量风险判断或评审结论。

### 3.5 Contract First

Business Agent 与其他 Capability 之间只通过正式 Contract 协作。

Business Agent 访问 Knowledge Capability 时，只能通过：

```text
QUALITY_AGENT_CONTRACT V1.0
```

不得直接访问：

- Provider
- Repository
- Storage
- Index
- Retrieval Strategy
- Knowledge Capability 内部目录

### 3.6 Configuration Driven

可变化内容优先通过配置表达，包括：

- Agent Profile
- Workflow
- Node Config
- Capability Binding
- Service Version
- Schema Version
- Requested Fields
- Runtime Policy

平台代码只实现公共机制。

### 3.7 Evidence and Trace First

所有关键 Capability 调用应支持：

- Request Trace
- Response Trace
- Evidence引用
- Warning
- Error
- 版本追溯

---

## 4. Platform Architecture

```text
External Client / Portal
          │
          ▼
Business Agent API
          │
          ▼
Business Agent Runtime
├── Agent Profile Loader
├── Runtime Identity
├── Context Builder
├── Workflow Engine
├── Node Registry
├── Plugin Loader
├── Capability Gateway
│   └── Knowledge Contract Gateway
├── Capability Result Store
├── Result Engine
└── Trace Manager
          │
          ▼
Business Plugin
          │
          ▼
Business Decision / Recommendation / Report
```

Capability 调用关系：

```text
Business Workflow Node
          │
          ▼
Capability Gateway
          │
          ▼
QUALITY_AGENT_CONTRACT
          │
          ▼
Knowledge Capability
```

---

## 5. Agent Model

### 5.1 Agent Profile

Agent Profile 至少包含：

```text
agent_id
name
version
description
workflow
input_schema
output_schema
capability_bindings
plugin
metadata
```

建议结构：

```yaml
agent:
  id: repeat_case
  name: Repeat Case Agent
  version: "2.4"
  description: 重复问题分析智能体

workflow:
  - input.parse
  - capability.knowledge.query
  - business.repeat_case.analysis
  - result.build

capability_bindings:
  knowledge:
    repeat_case:
      service_id: repeat_case_service
      service_version: "1.0"
      schema_version: "1.0"
      operation: query_knowledge
      requested_fields:
        - case_id
        - title
        - problem_description
        - root_cause
        - solution
      default_options:
        top_k: 10
        include_evidence: true
        allow_degraded_result: true

plugin:
  module: plugins.repeat_case
```

### 5.2 Capability Binding

Capability Binding 用于声明 Agent 依赖的公共能力。

Knowledge Capability Binding 至少包括：

| Field | Description |
|---|---|
| binding_name | Agent内部引用名称 |
| service_id | Knowledge Service唯一标识 |
| service_version | 目标Service版本 |
| schema_version | Query和Result Schema版本 |
| operation | Contract Operation |
| requested_fields | 默认返回字段 |
| default_options | 默认调用策略 |
| runtime_policy | Timeout、Retry和降级策略 |

Workflow Node 只引用 Binding Name。

```yaml
config:
  knowledge_binding: repeat_case
```

不得在多个Node或业务代码中重复硬编码：

- service_id
- service_version
- schema_version
- requested_fields
- Provider地址
- Index名称

---

## 6. Workflow Design

### 6.1 Workflow Position

Workflow 是 Agent 业务执行过程的配置化表达。

REPEAT_CASE 首个正式Workflow：

```text
input.parse
    ↓
capability.knowledge.query
    ↓
business.repeat_case.analysis
    ↓
result.build
```

### 6.2 Workflow Node

Workflow Node 至少包含：

```text
node_id
node_type
handler
enabled
config
runtime_policy
```

Node Type 建议分类：

```text
input.*
capability.*
business.*
result.*
control.*
```

### 6.3 Node Result Contract

所有Workflow Node统一返回：

```text
NodeResult
├── node_id
├── status
├── output
├── context_updates
├── warnings
├── error
├── metrics
└── trace
```

建议结构：

```json
{
  "node_id": "knowledge_query",
  "status": "success",
  "output": {},
  "context_updates": {},
  "warnings": [],
  "error": null,
  "metrics": {
    "duration_ms": 820
  },
  "trace": {}
}
```

Node状态统一为：

```text
success
partial_success
skipped
failed
```

Capability自身的Contract状态应在Node Result中单独保留，不得被覆盖。

### 6.4 Workflow Execution Rules

Workflow Engine负责：

1. 按顺序加载Node。
2. 通过Node Registry解析Handler。
3. 执行Node。
4. 校验Node Result。
5. 合并Context Updates。
6. 保存Node Trace。
7. 根据Node Policy处理失败、跳过和降级。
8. 将最终Node输出交给Result Engine。

Workflow Engine不得：

- 判断是否重复问题
- 判断质量风险是否成立
- 解释Knowledge结果的业务意义
- 生成具体业务结论

---

## 7. Runtime Identity

每次Agent运行必须建立统一Identity。

```text
RuntimeIdentity
├── trace_id
├── execution_id
├── request_id
├── agent_id
├── agent_version
├── tenant_id
├── domain_id
└── user_id
```

ID关系：

```text
trace_id
    └── execution_id
          ├── Business Request
          ├── Workflow Node Trace
          └── Knowledge request_id
                ├── response_id
                └── knowledge_trace_id
```

---

## 8. Runtime Context

Runtime Context正式冻结为：

```text
RuntimeContext
├── identity
├── request
├── profile
├── inputs
├── variables
├── workspace
├── capabilities
│   └── knowledge
│       ├── invocations
│       ├── items
│       ├── evidence
│       ├── warnings
│       └── errors
├── node_results
├── result
└── trace
```

规则：

1. Runtime Context 是Workflow Node之间唯一正式共享对象。
2. 业务Plugin不得通过读取其他Node内部文件获取运行结果。
3. Knowledge结果统一存入 `context.capabilities.knowledge`。
4. 旧的 `knowledge_response`、`knowledge_request`、`knowledge_items` 等字段只允许迁移期兼容。
5. 新业务Plugin不得依赖旧字段。

---

## 9. Capability Consumption Architecture

```text
Workflow Node
    ↓
Capability Gateway
    ↓
Contract Model
    ↓
Transport Client
    ↓
External Capability
```

Capability Gateway负责：

- Service Binding解析
- Contract Request构造
- Contract版本校验
- HTTP调用
- Response解析
- Error映射
- Warning映射
- Status映射
- Compatibility转换
- Capability Result写入Context

业务Plugin不得直接：

- 组装HTTP Body
- 解析原始HTTP Response
- 读取Capability地址
- 判断Contract版本
- 调用Provider

---

## 10. Knowledge Contract Gateway

Knowledge Contract Gateway 是Business Agent内部访问Knowledge Capability的统一入口。

```text
Knowledge Workflow Node
        ↓
Knowledge Contract Gateway
        ↓
Knowledge Client
        ↓
Knowledge Capability
```

支持操作：

```text
discover_services
describe_service
query_knowledge
batch_query_knowledge
health_check
```

V1.2首期必须实现：

```text
query_knowledge
describe_service
health_check
```

外部Contract Model：

```text
KnowledgeRequestEnvelope
KnowledgeResponseEnvelope
KnowledgeServiceReference
KnowledgeCaller
KnowledgeResult
KnowledgeResultItem
KnowledgeEvidence
KnowledgeTrace
KnowledgeWarning
KnowledgeError
```

内部Runtime Model：

```text
CapabilityInvocation
CapabilityResult
KnowledgeContext
SelectedKnowledge
EvidenceReference
```

业务Plugin只能消费内部标准模型，不直接依赖Knowledge Capability原始JSON。

---

## 11. Knowledge Request Mapping

统一Request Envelope：

```json
{
  "contract_version": "1.0",
  "request_id": "REQ-001",
  "trace_id": "TRACE-001",
  "operation": "query_knowledge",
  "service": {
    "service_id": "repeat_case_service",
    "service_version": "1.0",
    "schema_version": "1.0"
  },
  "caller": {
    "agent_id": "repeat_case",
    "agent_version": "2.4",
    "capability_id": "repeat_case",
    "execution_id": "EXEC-001"
  },
  "query": {},
  "filters": {},
  "requested_fields": [],
  "context": {},
  "options": {},
  "trace_options": {
    "enabled": true,
    "level": "standard"
  }
}
```

---

## 12. Knowledge Response Consumption

Business Agent必须完整支持：

```text
success
partial_success
no_result
failed
```

不得只转换为：

```text
SUCCESS
FAILED
```

状态规则：

- `success`：继续后续业务Node。
- `partial_success`：继续执行，但必须保存Warning并标记Degraded。
- `no_result`：不是Runtime异常，可进入无知识降级流程。
- `failed`：根据Node Policy执行retry、fail_fast、skip或降级。

内部标准Result Item至少包含：

```json
{
  "knowledge_id": "K-001",
  "knowledge_version": "1.0",
  "knowledge_type": "case",
  "rank": 1,
  "title": "Knowledge title",
  "summary": "Knowledge summary",
  "score": 0.82,
  "fields": {},
  "evidence_refs": [
    "EV-001"
  ]
}
```

规则：

1. score范围统一为`0.0–1.0`或`null`。
2. 不同Knowledge Service的score不得直接横向比较。
3. score不等于业务置信度。
4. knowledge_version必须保留。
5. Evidence通过evidence_refs关联。

---

## 13. Evidence Design

Evidence统一存入：

```text
context.capabilities.knowledge.evidence
```

引用链：

```text
Business Conclusion
    ↓
Knowledge Item
    ↓
Evidence Reference
    ↓
Original Source
```

Evidence用于说明知识来源和检索依据，不等同于业务结论。

---

## 14. Trace Design

Trace Manager统一记录：

- trace_id
- execution_id
- Agent ID
- Agent Version
- Workflow
- Node ID
- Node Status
- Contract Version
- Service Version
- Schema Version
- Profile Version
- Capability request_id
- response_id
- knowledge_trace_id
- Warning
- Error
- Retry
- Duration
- Degraded State

---

## 15. Error, Retry and Degradation

建议配置：

```yaml
runtime_policy:
  timeout_ms: 30000
  retry:
    max_attempts: 2
    backoff_ms: 1000
  allow_degraded_result: true
  fail_on_no_result: false
  fail_on_partial_success: false
```

规则：

1. 只对`error.retryable=true`的错误重试。
2. Contract和Schema错误不重试。
3. Service不存在或未启用不重试。
4. Provider临时超时可重试。
5. 不得无限重试。
6. 降级结果必须显式返回`partial_success`、Warning和Degraded标记。

---

## 16. Service Description and Startup Validation

Agent Profile加载后，可通过`describe_service`校验：

- Service是否存在
- Service是否Active
- Operation是否支持
- Service版本是否兼容
- Schema版本是否兼容
- requested_fields是否合法
- options是否合法
- Permission是否满足

建议流程：

```text
Load Agent Profile
    ↓
Resolve Capability Binding
    ↓
Describe Service
    ↓
Validate Compatibility
    ↓
Register Agent
```

---

## 17. Plugin Design

Plugin负责：

- 业务输入解释
- Query Mapping
- 业务分析
- Business Decision
- Recommendation
- Report业务内容

Plugin不得负责：

- Runtime生命周期
- Workflow调度
- Capability HTTP调用
- Contract序列化
- Trace基础设施
- Provider访问
- Knowledge存储访问

---

## 18. Result Design

Result Engine负责：

- 收集Workflow输出
- 标准化Agent执行状态
- 组织业务Output
- 附加Warning和Error
- 附加Evidence引用
- 附加Trace引用
- 按Output Schema校验

Result Engine不负责产生具体业务判断。

---

## 19. Current Implementation Mapping

当前Engine已经具备：

- Agent Profile Loader
- Runtime
- Workflow Engine
- Handler Registry
- Plugin Loader
- Runtime Context基础结构
- Input Parser
- Knowledge HTTP Client基础结构
- Result Engine
- Trace Manager
- Business Agent HTTP API
- REPEAT_CASE Plugin
- Mock与Capability Provider切换

当前需刷新：

1. 旧版扁平Knowledge Request。
2. `success`布尔响应解析。
3. `SUCCESS/FAILED`二态映射。
4. Knowledge Result Item字段。
5. Evidence结构。
6. Trace贯通。
7. Runtime Context正式结构。
8. Node Result统一契约。
9. Capability Binding。
10. Warning、Retry和Degraded处理。

当前状态：

```text
Platform Skeleton Completed
Contract Alignment Development
Real Integration Pending
```

---

## 20. Engine Development Packages

### Package 1：Contract Model Refresh

- Request Envelope
- Response Envelope
- Service Reference
- Caller
- Result Item
- Evidence
- Trace
- Warning
- Error

### Package 2：Knowledge Contract Gateway

- query_knowledge
- describe_service
- health_check
- Contract版本校验
- Request序列化
- Response解析
- Error与Warning映射

### Package 3：Runtime Model Refresh

- Runtime Identity
- Runtime Context
- Capability Result Store
- Node Result Contract
- Trace贯通

### Package 4：Knowledge Node Refresh

- Capability Binding
- Query Mapping
- Status聚合
- no_result处理
- partial_success处理
- Retry
- Degraded Result
- Case失败隔离

### Package 5：REPEAT_CASE Integration

```text
Excel Upload
    ↓
Business Agent API
    ↓
Input Parse
    ↓
query_knowledge
    ↓
Knowledge Capability
    ↓
Knowledge Response
    ↓
Repeat Case Analysis
    ↓
Report
    ↓
Trace
```

---

## 21. Design Acceptance Criteria

1. Business Agent按照统一Request Envelope调用Knowledge Capability。
2. Request包含trace_id、operation、service和完整caller。
3. Agent Profile支持Capability Binding。
4. Workflow Node具有统一Node Result。
5. Runtime Context具有稳定一级结构。
6. Plugin不直接处理Contract原始JSON。
7. Response支持success、partial_success、no_result和failed。
8. Result Item支持knowledge_version、rank、fields和evidence_refs。
9. Evidence统一进入Capability Result Store。
10. Warning不得被静默忽略。
11. Retry只针对retryable错误。
12. Trace贯通Business Agent和Knowledge Capability。
13. REPEAT_CASE不依赖Provider、Storage、Index和Retrieval实现。
14. REPEAT_CASE完成真实HTTP端到端运行。
15. QUALITY_RISK后续可复用相同Knowledge Contract Gateway。
16. Mock兼容逻辑仅用于测试，不成为正式Contract语义。

---

## 22. Design Freeze

正式冻结以下设计原则：

1. BUSINESS_AGENT是公共业务智能体平台，不属于具体业务Agent。
2. Agent采用Profile、Workflow、Capability Binding和Plugin组合。
3. Runtime不写入具体业务逻辑。
4. Workflow Node统一使用Node Result Contract。
5. Runtime Context采用稳定一级结构。
6. Capability调用统一通过Capability Gateway。
7. Knowledge调用统一通过Knowledge Contract Gateway。
8. Business Agent只通过QUALITY_AGENT_CONTRACT访问Knowledge Capability。
9. Plugin不得直接依赖Knowledge Capability原始HTTP JSON。
10. Contract Model与Runtime Model必须分层。
11. Knowledge结果统一进入Capability Result Store。
12. Contract状态、Warning、Error和Evidence必须完整保留。
13. score不得等同于业务置信度。
14. Evidence不得等同于业务结论。
15. Provider、Storage、Index和Retrieval差异不得进入业务Plugin。
16. REPEAT_CASE作为V1.2首个真实端到端验证对象。
17. 后续非平台级架构变化不得刷新Design，应进入Engine实现和缺陷处理。

---

# Design Freeze Conclusion

```text
BUSINESS_AGENT_DESIGN
Version：V1.2
Status：Design Freeze
```

本设计作为以下工作的共同输入：

- BUSINESS_AGENT_ENGINE V1.2 Contract Alignment Development
- REPEAT_CASE × Knowledge Capability端到端联调
- 后续业务智能体Plugin迁移
- Business Agent平台验收

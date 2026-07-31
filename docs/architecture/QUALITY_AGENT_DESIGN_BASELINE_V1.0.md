QUALITY_AGENT_DESIGN_BASELINE_V1.0

Version: V1.0
Status: Design Freeze
Scope: QUALITY_AGENT R1 Integration MVP

⸻

1. Baseline Purpose

本基线用于冻结 QUALITY_AGENT R1 阶段进入工程实现前的系统设计约束。

目标：

* 统一架构认知
* 明确模块职责边界
* 固化 Contract Driven 设计原则
* 作为 QUALITY_AGENT_ENGINE 的正式输入

设计链路：

Baseline
    ↓
Requirements
    ↓
Design
    ↓
Engine
    ↓
DryRun
    ↓
PMO

⸻

2. Platform Position

QUALITY_AGENT 是面向软件质量领域的 AI Native Quality Platform。

平台目标：

通过统一的平台能力，构建可持续沉淀、可持续复用、可持续演进的质量智能能力。

不是构建孤立的业务智能体。

⸻

3. Design Principles

3.1 Platform First

优先建设平台公共能力：

* Agent Runtime
* Knowledge Capability
* Contract Framework
* Integration Capability

业务能力基于平台能力扩展。

⸻

3.2 Contract Driven

所有能力之间通过统一 Contract 通信。

禁止：

* 模块直接依赖内部实现
* 跨能力直接调用内部接口

统一模式：

Request
↓
Contract
↓
Response

⸻

3.3 Capability Reuse

质量能力以 Capability 形式沉淀。

例如：

* Knowledge Capability
* Repeat Case Capability
* Quality Risk Capability
* Quality Review Capability

能力独立演进。

⸻

4. Architecture Baseline

QUALITY_AGENT R1 架构：

                    QUALITY_AGENT
                          |
                Business Agent Runtime
                          |
              Capability Orchestration
        --------------------------------
        |                              |
 Knowledge Capability          Repeat Case Capability
                          |
                 Quality Result

⸻

5. Capability Responsibility

5.1 Business Agent

定位：

QUALITY_AGENT 业务智能运行中心。

负责：

* 用户任务理解
* Task Planning
* Capability 调用
* Result 生成

不负责：

* 知识资产管理
* 历史案例管理

⸻

5.2 Knowledge Capability

定位：

统一质量知识能力。

负责：

* Knowledge Management
* Knowledge Service
* Knowledge Version
* Knowledge Evidence

设计约束：

Knowledge Layer
        ≠
Retrieval Strategy

Knowledge 不负责：

* 用户任务理解
* Agent决策
* 业务流程编排

⸻

5.3 Repeat Case Capability

定位：

历史质量经验复用能力。

负责：

* 历史问题管理
* 相似案例分析
* 经验关联

当前阶段：

Repeat Case 作为 Capability 接入。

未来根据复杂度演进为独立 Agent。

⸻

6. Integration Layer Baseline

R1 阶段新增 Integration Layer。

目录：

integration/
├── task_manager
├── capability_router
└── result_aggregator

⸻

6.1 Task Manager

职责：

管理质量任务生命周期。

核心对象：

Task

状态：

CREATED
↓
PLANNING
↓
EXECUTING
↓
COMPLETED

⸻

6.2 Capability Router

职责：

Business Agent 与 Capability 之间的统一调度层。

负责：

* Capability发现
* Capability调用
* 调用状态管理

不负责：

* 业务分析
* 专业判断

⸻

6.3 Result Aggregator

职责：

统一多个 Capability 输出。

输出：

* Summary
* Evidence
* Recommendation

形成结构化质量分析结果。

⸻

7. Contract Baseline

R1 冻结以下 Contract：

TASK_CONTRACT_V1.0
CAPABILITY_CONTRACT_V1.0
KNOWLEDGE_CONTRACT_V1.0
RESULT_CONTRACT_V1.0

⸻

8. E2E Target

R1 第一阶段目标：

形成：

User Question
↓
Task
↓
Business Agent
↓
Knowledge Capability
↓
Result
↓
Quality Analysis Report

⸻

9. Engineering Boundary

ENGINE 可以：

* 实现设计方案
* 优化代码结构
* 优化性能
* 修复缺陷

ENGINE 不允许：

* 修改架构边界
* 绕过 Contract
* 破坏 Capability 独立性

如需调整：

必须进入 Design Change。

⸻

10. Change Management

基线冻结后：

所有变化通过版本管理。

流程：

Design Change Request
↓
Design Update
↓
New Baseline
↓
Engine Migration

版本：

V1.0
↓
V1.1
↓
V2.0

⸻

11. Current Status

项目	状态
Architecture	Frozen
Design	Frozen
Contract	Baseline
Engine	Ready
DryRun	Pending

⸻

12. Next Step

进入：

QUALITY_AGENT_ENGINE

执行：

1. Contract落库
2. Integration Layer开发
3. Business Agent与Knowledge Capability集成
4. E2E DryRun验证

# QUALITY_AGENT_ENGINE_M1_CODE_STRUCTURE

Version: V1.0

Status: Code Structure Baseline

Scope: QUALITY_AGENT_ENGINE_M1 Runtime Foundation

------------------------------------------------------------------------

# 1. Purpose

本文档定义 QUALITY_AGENT_ENGINE V1.0 M1 阶段代码结构。

目标：

在不破坏已有 Business Agent 能力的前提下，逐步形成统一 QUALITY_AGENT
Engine。

原则：

-   渐进迁移
-   保持兼容
-   Engine 与业务能力分离
-   Capability 可复用

------------------------------------------------------------------------

# 2. Target Repository Structure

目标：

    quality-ai

    ├── engine

    │   ├── runtime
    │   │   ├── engine.py
    │   │   ├── lifecycle.py
    │   │   └── state.py
    │   │
    │   ├── agents
    │   │   ├── registry.py
    │   │   ├── definition.py
    │   │   └── executor.py
    │   │
    │   ├── capabilities
    │   │   ├── interface.py
    │   │   └── registry.py
    │   │
    │   ├── context
    │   │   └── context.py
    │   │
    │   ├── trace
    │   │   └── trace.py
    │   │
    │   ├── contracts
    │   │
    │   └── adapters
    │


    ├── business_agent

    ├── knowledge_capability

    ├── contracts

    └── docs

------------------------------------------------------------------------

# 3. Migration Mapping

## 3.1 Engine Runtime

Source:

    business_agent/business_agent/engine

Target:

    engine/runtime

Migration:

    BusinessAgentEngine

    ↓

    AgentEngine Runtime

保留：

-   initialize
-   start
-   stop
-   health

------------------------------------------------------------------------

# 3.2 Agent Registry

Source:

    business_agent/business_agent/agent/registry.py

Target:

    engine/agents/registry.py

能力：

-   Agent注册
-   Agent查询
-   Agent生命周期管理

------------------------------------------------------------------------

# 3.3 Runtime State

Source:

    business_agent/runtime

Target:

    engine/runtime/state.py

能力：

-   Engine状态
-   Runtime状态

------------------------------------------------------------------------

# 4. New Components

## 4.1 Capability Interface

新增：

    engine/capabilities/interface.py

定义：

    Capability

    - metadata()

    - execute()

    - health()

------------------------------------------------------------------------

## 4.2 Context Runtime

新增：

    engine/context/context.py

负责：

-   Task上下文
-   Agent上下文
-   Capability上下文

------------------------------------------------------------------------

## 4.3 Trace Runtime

新增：

    engine/trace/trace.py

记录：

-   Task Trace
-   Agent Trace
-   Capability Trace

------------------------------------------------------------------------

# 5. M1 Development Sequence

## Step 1

创建 engine package。

## Step 2

迁移 Runtime。

## Step 3

迁移 Agent Registry。

## Step 4

建立 Capability Interface。

## Step 5

完成 E2E 验证。

------------------------------------------------------------------------

# 6. Coding Rules

## Rule 1

禁止：

业务逻辑进入 engine/runtime。

## Rule 2

禁止：

Agent直接调用外部能力。

必须：

    Agent

    ↓

    Capability Interface

    ↓

    Capability

## Rule 3

保持：

Contract First。

------------------------------------------------------------------------

# 7. M1 Completion Criteria

完成：

    QUALITY_AGENT_ENGINE_V1.0_M1

    Runtime Foundation

具备：

-   Engine启动
-   Agent注册
-   Capability调用
-   Context传递
-   Trace输出

------------------------------------------------------------------------

# End

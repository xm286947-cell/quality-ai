# QUALITY_AGENT_ENGINE_V1.0_M3_REPEAT_CASE_ROADMAP

Version: V1.0

Status: M3 Planning Baseline

Scope: QUALITY_AGENT_ENGINE V1.0 M3

------------------------------------------------------------------------

# 1. Objective

M3 目标：

基于 M2 Engine Platform Foundation，快速建设第一个业务闭环 Agent。

优先选择：

    Repeat Case Agent

目标：

验证 QUALITY_AGENT 平台从"技术平台"向"业务价值平台"演进。

------------------------------------------------------------------------

# 2. M2 → M3 Evolution

## M2

解决：

    Engine 如何运行

能力：

    Portal

    ↓

    Engine

    ↓

    Task

    ↓

    Workflow

    ↓

    Agent

    ↓

    Capability

    ↓

    LLM

------------------------------------------------------------------------

## M3

解决：

    Engine 如何支撑质量业务

目标：

    Quality User

    ↓

    Repeat Case Agent

    ↓

    Knowledge Capability

    ↓

    Case Data

    ↓

    Analysis Result

------------------------------------------------------------------------

# 3. M3 Scope

## Priority 1

Repeat Case Agent

包含：

-   Case Retrieval
-   Similar Case Analysis
-   Solution Recommendation
-   Result Feedback

------------------------------------------------------------------------

# 4. Repeat Case Architecture

    Portal

    ↓

    Business Agent Runtime

    ↓

    Repeat Case Agent

    ↓

    Knowledge Capability

    ↓

    Repeat Case Repository

    ↓

    LLM Runtime

    ↓

    Result

------------------------------------------------------------------------

# 5. Engine Reuse

M3 基于 M2 已有能力：

  能力                    状态
  ----------------------- ------
  Agent Runtime           ✅
  Task Runtime            ✅
  Workflow Runtime        ✅
  API Foundation          ✅
  Permission Foundation   ✅

无需重新建设 Engine Core。

------------------------------------------------------------------------

# 6. M3 Phase Plan

## M3_P01 Repeat Case Agent Design

目标：

定义：

-   Agent职责
-   输入输出
-   Case检索流程

------------------------------------------------------------------------

## M3_P02 Knowledge Integration

目标：

接入：

-   历史问题
-   解决方案
-   经验案例

------------------------------------------------------------------------

## M3_P03 E2E Validation

验证：

    用户问题

    ↓

    Repeat Case Agent

    ↓

    案例检索

    ↓

    分析

    ↓

    推荐

    ↓

    反馈

------------------------------------------------------------------------

## M3_P04 Product Integration

接入：

    QUALITY_AGENT_PORTAL

形成用户闭环。

------------------------------------------------------------------------

# 7. Non Scope

M3 暂不包含：

-   Quality Risk Agent
-   Enterprise Deployment
-   Kubernetes
-   大规模运营平台

------------------------------------------------------------------------

# 8. Delivery Principle

保持：

    Design

    ↓

    Review

    ↓

    Freeze

    ↓

    Implementation

    ↓

    QAE

    ↓

    Verify

    ↓

    Release

------------------------------------------------------------------------

# 9. M3 Success Criteria

完成：

    第一个业务 Agent 闭环

验证：

-   Engine 可支撑业务 Agent
-   Knowledge 可产生业务价值
-   Portal 可展示结果

------------------------------------------------------------------------

# 10. Status

Current:

M3 Planning Baseline

Next:

Repeat Case Agent Design

------------------------------------------------------------------------

# End

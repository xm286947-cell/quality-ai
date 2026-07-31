# QUALITY_AGENT_PORTAL_DESIGN_V1.0

Version: V1.0\
Status: Design Draft\
Design Scope: QUALITY_AGENT 用户产品入口与 AI Quality Workbench 设计

------------------------------------------------------------------------

# 1. Design Purpose

## 1.1 Design Goal

设计 QUALITY_AGENT 统一用户入口 Portal，为用户提供面向软件质量工作的 AI
工作台。

Portal 负责：

-   用户交互
-   Workspace 管理
-   Task 管理
-   Agent 编排
-   Report 展示
-   质量资产沉淀

Portal 不负责：

-   Prompt实现
-   LLM调用
-   知识检索算法
-   质量分析逻辑

------------------------------------------------------------------------

# 2. Product Position

QUALITY_AGENT Portal 定位：

> AI Quality Workbench（AI质量工作台）

通过统一入口连接：

-   Business Agent
-   Repeat Case Agent
-   Knowledge Capability

帮助研发、质量、产品人员完成质量分析工作。

------------------------------------------------------------------------

# 3. Core Design Principles

## 3.1 Portal不是Chat，而是WorkBench

用户管理：

-   Workspace
-   Task
-   Report

而不是聊天记录。

## 3.2 Task Driven

所有AI执行必须形成Task。

流程：

用户任务 → Agent执行 → Report输出

## 3.3 Report First

所有Agent结果统一转换为QUALITY_REPORT。

结构：

-   Summary
-   Evidence
-   Analysis
-   Recommendation
-   Related Knowledge

## 3.4 Contract Driven

Portal通过Contract接入Agent。

Portal不感知Agent内部实现。

------------------------------------------------------------------------

# 4. Overall Architecture

    QUALITY_AGENT

            |

          Portal

            |

    ----------------------------

    Business Agent

    Repeat Case Agent

    Knowledge Capability

    ----------------------------

------------------------------------------------------------------------

# 5. Core Object Model

## Workspace

一次质量工作的上下文空间。

包含：

-   项目
-   版本
-   Task
-   Report
-   Knowledge
-   History

## Task

一次AI质量分析任务。

生命周期：

Created → Running → Completed → Reviewed → Archived

## Agent

可插拔质量能力单元。

## Report

统一质量分析交付物。

## Knowledge

由有效Report沉淀形成的质量资产。

## History

质量工作的历史记录。

------------------------------------------------------------------------

# 6. Information Architecture

    QUALITY_AGENT Portal

    ├── Home
    ├── Workspace
    ├── Task Center
    ├── Agent Center
    ├── Report Center
    ├── Knowledge Center
    └── History

------------------------------------------------------------------------

# 7. Functional Design

## Workspace Management

负责：

-   创建Workspace
-   管理上下文
-   查看任务和报告

## Task Management

负责：

-   创建任务
-   调用Agent
-   跟踪状态

## Agent Integration

流程：

Portal

↓

Agent Contract

↓

Agent Engine

↓

Report

## Report Management

负责：

-   保存报告
-   展示报告
-   管理版本

------------------------------------------------------------------------

# 8. API & Contract Design

## Agent Contract

示例：

``` json
{
  "agent_id":"repeat_case",
  "name":"Repeat Case Agent",
  "version":"1.0"
}
```

## Task Contract

包含：

-   task_id
-   workspace_id
-   agent_id
-   input
-   status

## Report Contract

统一：

    QUALITY_REPORT

    Summary

    Evidence

    Analysis

    Recommendation

    Related Knowledge

------------------------------------------------------------------------

# 9. UI/UX Design

设计方向：

参考汇川官网品牌视觉语言。

关键词：

-   工业科技
-   专业可信
-   简洁现代

## 首页

突出：

-   品牌表达
-   快速开始
-   工作空间

## Workspace

体现：

项目、版本、任务、报告关系。

## Report

采用工程分析报告风格。

避免聊天气泡形式。

------------------------------------------------------------------------

# 10. Technical Architecture

    Browser

    ↓

    Portal Frontend

    ↓

    Portal Backend

    ↓

    Agent Gateway

    ↓

    Agent Services

Backend模块：

-   Workspace Service
-   Task Service
-   Agent Gateway
-   Report Service
-   Knowledge Service
-   History Service

------------------------------------------------------------------------

# 11. MVP Scope

## P0

必须：

-   Portal框架
-   Workspace
-   Task
-   Agent调用
-   Report展示

## P1

增强：

-   文件上传
-   Report导出
-   Knowledge关联

## P2

未来：

-   权限
-   多人协作
-   流程编排

------------------------------------------------------------------------

# 12. Review Scope

评审窗口：

1.  QUALITY_AGENT_PRODUCT

关注： 产品定位、MVP范围

2.  QUALITY_AGENT_REFERENCE_ARCHITECTURE

关注： 架构边界、Contract

3.  BUSINESS_AGENT

关注： Agent接入方式

4.  REPEAT_CASE

关注： Engine接入方式

5.  KNOWLEDGE_CAPABILITY

关注： 知识关联设计

------------------------------------------------------------------------

# 13. Design Freeze Criteria

满足：

-   Portal定位明确
-   核心对象明确
-   Contract明确
-   UI方向明确
-   技术边界明确
-   MVP范围明确

进入：

QUALITY_AGENT_PORTAL_ENGINE V1.0

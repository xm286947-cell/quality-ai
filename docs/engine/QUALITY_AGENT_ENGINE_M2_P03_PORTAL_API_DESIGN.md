# QUALITY_AGENT_ENGINE_M2_P03_PORTAL_API_DESIGN

Version: V1.0

Status: Implementation Design Baseline

Scope: QUALITY_AGENT_ENGINE V1.0 M2_P03

------------------------------------------------------------------------

# 1. Purpose

本文档定义 QUALITY_AGENT_ENGINE V1.0 M2_P03 阶段 Portal API Foundation
设计。

输入：

-   QUALITY_AGENT_ENGINE_M2_DESIGN_V1.0
-   QUALITY_AGENT_ENGINE_M2_IMPLEMENTATION_PLAN_V1.0
-   M2_P01 Workflow Runtime
-   M2_P02 Task Runtime

目标：

建立 QUALITY_AGENT_PORTAL 与 ENGINE 的标准交互入口。

------------------------------------------------------------------------

# 2. Objective

M2_P01:

    Workflow 可以编排 Agent

M2_P02:

    Task 可以管理 Workflow 生命周期

M2_P03:

    Portal 可以调用 Engine

目标链路：

    User

    ↓

    Portal

    ↓

    Engine API

    ↓

    Task Runtime

    ↓

    Workflow Runtime

    ↓

    Agent

    ↓

    Result

------------------------------------------------------------------------

# 3. Scope

## 3.1 Engine Service API

新增：

    engine/api/

包含：

    service.py

职责：

-   Engine 服务入口
-   Task 提交
-   Task 查询
-   Result 获取

------------------------------------------------------------------------

# 4. Task API

新增：

    engine/api/task_api.py

能力：

## Submit Task

功能：

创建任务并触发执行。

输入：

    Task Request

输出：

    Task ID

------------------------------------------------------------------------

## Query Task

功能：

查询任务状态。

输入：

    Task ID

输出：

    Task Status

------------------------------------------------------------------------

# 5. Result API

新增：

    engine/api/result_api.py

能力：

获取执行结果。

输入：

    Task ID

输出：

    Execution Result

------------------------------------------------------------------------

# 6. Architecture

    QUALITY_AGENT_PORTAL

            |

            ↓

         Engine API

            |

            ↓

       Task Runtime

            |

            ↓

     Workflow Runtime

            |

            ↓

     Agent Runtime

            |

            ↓

     Result

------------------------------------------------------------------------

# 7. API Boundary

Portal 负责：

-   用户交互
-   请求提交
-   展示结果

Engine 负责：

-   Task管理
-   Workflow执行
-   Agent调用

禁止：

-   Portal执行Agent逻辑
-   API绕过Task Runtime直接调用Agent

------------------------------------------------------------------------

# 8. Acceptance Criteria

## API

-   Task 可以提交
-   Task 状态可以查询
-   Result 可以获取

## Integration

-   Portal 可以调用 Engine
-   Engine 可以返回 Task Result

## Trace

记录：

    User

    ↓

    Task

    ↓

    Workflow

    ↓

    Agent

    ↓

    Result

------------------------------------------------------------------------

# 9. Constraints

保持：

-   Contract First
-   Portal 与 Engine 解耦
-   API 不承载业务逻辑
-   QAE Delivery Workflow

------------------------------------------------------------------------

# 10. Delivery Process

遵循：

    Design

    ↓

    Review

    ↓

    Freeze

    ↓

    Implementation

    ↓

    Increment Package

    ↓

    QAE Install

    ↓

    Verify

    ↓

    Git Commit

------------------------------------------------------------------------

# 11. Deliverables

代码：

    QUALITY_AGENT_ENGINE_M2_P03_INCREMENT

包含：

-   Engine Service API
-   Task API
-   Result API

------------------------------------------------------------------------

# 12. Status

Current:

Ready For Review

Baseline:

QUALITY_AGENT_ENGINE_M2_P02_TASK_RUNTIME

------------------------------------------------------------------------

# End

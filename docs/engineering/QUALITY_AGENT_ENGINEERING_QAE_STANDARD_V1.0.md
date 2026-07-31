# QUALITY_AGENT_ENGINEERING_QAE_STANDARD_V1.0

Version: V1.0

Status: Engineering Standard Baseline

Scope: QUALITY_AGENT Engineering Delivery

------------------------------------------------------------------------

# 1. Purpose

本文档定义 QUALITY_AGENT 工程开发过程中的 QAE（Quality Automation
Engineering）使用规范。

目标：

-   提升 AI Coding 交付效率
-   降低人工覆盖代码风险
-   支持增量安装
-   支持变更验证
-   支持快速回滚

QAE 用于工程交付管理，不属于 QUALITY_AGENT Runtime Engine。

------------------------------------------------------------------------

# 2. QAE Position

整体关系：

    QUALITY_AGENT

            |

    QUALITY_AGENT_ENGINE

            |

    QUALITY_AGENT_ENGINEERING

            |

    QAE Tool

职责划分：

  模块         职责
  ------------ ------------------------
  ENGINE       AI Agent运行能力
  Capability   业务质量能力
  QAE          代码增量交付与安装管理
  DryRun       变更验证
  Git          版本管理

------------------------------------------------------------------------

# 3. QAE Responsibility

QAE负责：

-   Increment Package 安装
-   文件备份
-   安装状态记录
-   安装结果校验
-   最近版本回滚

QAE不负责：

-   Agent执行
-   Capability逻辑
-   业务规则
-   Runtime调度

------------------------------------------------------------------------

# 4. Increment Package Standard

标准增量包：

    XXX_INCREMENT.zip

    ├── manifest.json

    └── files/

        └── repository relative path

------------------------------------------------------------------------

# 5. Manifest Standard

必须包含：

``` json
{
  "package_name": "",
  "target_project": "quality-ai",
  "target_scope": "",
  "version": "",
  "milestone": "",
  "files": []
}
```

字段定义：

  字段             说明
  ---------------- --------------
  package_name     增量包名称
  target_project   目标仓库
  target_scope     影响范围
  version          版本号
  milestone        开发阶段
  files            变更文件列表

------------------------------------------------------------------------

# 6. AI Coding Delivery Flow

标准流程：

    Requirement

    ↓

    Design

    ↓

    Implementation Task

    ↓

    AI Coding

    ↓

    Increment Package

    ↓

    QAE Install

    ↓

    QAE Verify

    ↓

    DryRun

    ↓

    Git Commit

------------------------------------------------------------------------

# 7. Installation Process

执行：

    qae install XXX_INCREMENT.zip

流程：

    Increment Package

    ↓

    Read Manifest

    ↓

    Validate Target

    ↓

    Backup Existing Files

    ↓

    Install Files

    ↓

    Record State

    ↓

    Complete

------------------------------------------------------------------------

# 8. Verification Process

执行：

    qae verify

验证：

-   安装状态
-   文件完整性
-   变更记录

------------------------------------------------------------------------

# 9. Rollback Process

执行：

    qae rollback

目标：

恢复最近一次安装前状态。

流程：

    Backup

    ↓

    Restore Files

    ↓

    Update State

    ↓

    Complete

------------------------------------------------------------------------

# 10. Version Naming

推荐：

    <PROJECT>_<MODULE>_<MILESTONE>_<PATCH>_INCREMENT

示例：

    QUALITY_AGENT_ENGINE_M1_P01_INCREMENT

含义：

-   QUALITY_AGENT_ENGINE：项目
-   M1：里程碑
-   P01：第一个增量包

------------------------------------------------------------------------

# 11. Engineering Rules

## Rule 1

AI生成代码必须优先通过 Increment Package 交付。

------------------------------------------------------------------------

## Rule 2

禁止直接覆盖关键工程文件。

------------------------------------------------------------------------

## Rule 3

重要变更必须具备：

-   Manifest
-   Version
-   Verification
-   Rollback能力

------------------------------------------------------------------------

# 12. Relationship With ENGINE

ENGINE负责：

    运行

QAE负责：

    交付

二者边界：

    ENGINE

    ↓

    运行时能力


    QAE

    ↓

    工程变更管理

------------------------------------------------------------------------

# 13. Current Baseline

Version:

QUALITY_AGENT_ENGINEERING_QAE_STANDARD_V1.0

Status:

Engineering Standard Baseline

------------------------------------------------------------------------

# End

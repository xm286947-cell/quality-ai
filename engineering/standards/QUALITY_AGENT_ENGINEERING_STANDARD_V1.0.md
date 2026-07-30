# QUALITY_AGENT_ENGINEERING_STANDARD

Version：V1.0

Status：Freeze

Scope：QUALITY_AGENT Platform Engineering Standard

---

# 1. Position

QUALITY_AGENT_ENGINEERING_STANDARD（QAES）定义 QUALITY_AGENT 平台所有 Engine 的统一工程开发规范。

本规范用于统一平台工程行为，而不是定义业务能力。

目标：

- 统一开发方式
- 统一交付方式
- 统一安装方式
- 统一工程目录
- 统一增量交付规范

本规范不负责：

- Business Design
- Knowledge Design
- Capability Architecture
- Business Logic

---

# 2. Scope

本规范适用于：

- Business Agent Engine
- Knowledge Capability Engine
- Quality Risk Engine
- Repeat Case Engine
- Future Engine

所有 Engine 必须遵循本规范。

---

# 3. Repository Structure

QUALITY_AGENT 平台统一目录：

```text
quality-ai/

├── business_agent/
├── knowledge_capability/
├── quality_risk/
├── repeat_case/

└── engineering/
    ├── standards/
    ├── tools/
    └── templates/
```

说明：

- standards：平台工程规范
- tools：工程辅助工具（如 QAE）
- templates：公共模板

---

# 4. Development Workflow

所有 Engine 统一开发流程：

```text
Baseline
      ↓
Requirements
      ↓
Design
      ↓
Engine Development
      ↓
Increment Package
      ↓
Installation
      ↓
Verification
      ↓
Git Commit / Push
```

所有 Engine 应遵循统一开发流程。

---

# 5. Increment Standard

Engine 必须采用增量交付。

统一命名：

```text
<ENGINE>_V<Version>_<Milestone>_<Phase>_INCREMENT.zip
```

例如：

```text
BUSINESS_AGENT_ENGINE_V1.2_M1_P03_INCREMENT.zip

KNOWLEDGE_CAPABILITY_ENGINE_V2.0_M1_P02_INCREMENT.zip

QUALITY_RISK_ENGINE_V4.3_M2_P01_INCREMENT.zip
```

禁止直接交付整个源码目录。

---

# 6. Increment Package Structure

统一交付格式：

```text
Increment.zip

├── manifest.json

├── files/

└── README.md
```

所有 Engine 使用统一交付格式。

---

# 7. Manifest Standard

Manifest 建议字段：

```json
{
  "package_name": "",
  "target_project": "quality-ai",
  "target_scope": "",
  "version": "",
  "milestone": "",
  "summary": "",
  "files": []
}
```

Manifest 用于描述本次增量交付内容。

---

# 8. Installation Workflow

统一安装流程：

```text
Read Manifest
        ↓
Backup
        ↓
Install
        ↓
Verify
        ↓
Success
```

安装失败：

```text
Rollback
```

安装工具不限。

但安装流程必须符合本规范。

---

# 9. Engine Independence Principle

每个 Engine 必须能够：

- Independent Development
- Independent Testing
- Independent Packaging
- Independent Delivery
- Independent Installation

Engine 之间通过 Platform Contract 协作。

不得依赖直接修改其他 Engine 源码实现功能。

---

# 10. Tool Neutral Principle

Engineering Standard 定义工程行为。

不定义具体工程工具。

任何符合本规范的安装工具均可替换。

例如：

- QAE
- Python Script
- CI/CD Pipeline

均可实现本规范。

---

# 11. Rollback First Principle

任何安装流程必须遵循：

```text
Backup

↓

Install

↓

Verify
```

安装失败必须支持：

```text
Rollback
```

不得覆盖安装后无法恢复。

---

# 12. Increment Only Principle

所有 Engine 统一采用 Increment Delivery。

禁止：

- 整个工程覆盖
- 手工复制源码目录
- 非标准交付方式

所有交付均应采用标准 Increment Package。

---

# 13. Engineering Compliance

所有 Engine Design 文档必须引用：

QUALITY_AGENT_ENGINEERING_STANDARD

例如：

```text
Engineering Compliance

This Engine complies with:

• QUALITY_AGENT_ENGINEERING_STANDARD V1.0
```

所有 Engine Development 应遵循本规范。

---

# Status

Version：V1.0

Status：Freeze

QUALITY_AGENT_ENGINEERING_STANDARD 是 QUALITY_AGENT 平台唯一工程开发规范。

所有 Engine 开发均应遵循本规范。
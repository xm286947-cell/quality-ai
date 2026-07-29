# QUALITY_AGENT

> **AI Native Quality Platform**
>
> **Build reusable AI quality capabilities through a unified platform.**

---

# Vision

QUALITY_AGENT 是面向软件质量领域的 AI 原生平台。

平台以统一的平台能力为基础，构建可持续沉淀、可持续复用、可持续演进的质量智能能力，而不是构建一个个孤立的业务智能体。

核心理念：

- Platform First
- Contract Driven
- Configuration Driven
- Knowledge Driven
- Capability Reuse

---

# Platform Overview

QUALITY_AGENT 当前由两项核心平台能力组成：

- **Business Agent**
- **Knowledge Capability**

其中：

- Business Agent 负责统一业务智能体运行。
- Knowledge Capability 提供统一知识管理与知识消费能力。

所有业务能力均建立在统一的平台能力之上。

---

# Reference Architecture

```text
                    QUALITY_AGENT
             AI Native Quality Platform

══════════════════════════════════════════════════════

Platform Office
──────────────────────────────────────────────
Documentation
Architecture
Contract
Governance
Standards

                    │
                    ▼

Platform Runtime
──────────────────────────────────────────────
Agent Framework
Knowledge Framework
Configuration
Context Engine
Prompt Engine
LLM Adapter
SDK

                    │
                    ▼

Capability Layer
──────────────────────────────────────────────
Business Agent
Knowledge Capability
```

---

# Platform Capability

## Business Agent

Business Agent 是平台统一的业务智能体能力。

负责：

- Context Building
- Knowledge Consumption
- Prompt Execution
- Result Processing
- Business Function Orchestration

当前已支持业务功能：

- Repeat Case Analysis

---

## Knowledge Capability

Knowledge Capability 是平台统一知识能力。

负责：

- Knowledge Management
- Knowledge Retrieval
- Knowledge Service
- Knowledge Version
- Knowledge Evidence

Business Agent 通过统一 Contract 使用 Knowledge Capability，不直接依赖具体实现。

---

# Repository Structure

```text
quality-ai/
├── README.md
├── business_agent/
├── knowledge_capability/
└── docs/
    ├── README.md
    ├── architecture/
    ├── capabilities/
    ├── contracts/
    ├── governance/
    └── standards/
```

---

# Development Principles

QUALITY_AGENT 遵循统一的平台开发原则：

- Contract First
- Configuration Driven
- Capability Reuse
- Knowledge Driven
- Documentation First
- Architecture First

---

# Documentation

平台文档统一维护于：

```text
docs/
```

包括：

- Architecture
- Capability
- Contract
- Governance
- Standards

---

# Development Workflow

所有 Capability 统一遵循：

```text
Baseline
    ↓
Requirements
    ↓
Design
    ↓
Engine
    ↓
PMO
```

Platform Foundation 保持稳定，Capability 独立演进。

---

# Current Status

| Capability | Status |
|------------|--------|
| Business Agent | Development |
| Knowledge Capability | Development |

---

# License

Internal Project

QUALITY_AGENT Platform
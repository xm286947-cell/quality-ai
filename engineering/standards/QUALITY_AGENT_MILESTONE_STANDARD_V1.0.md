# QUALITY_AGENT_MILESTONE_STANDARD

Version：V1.0

Status：Freeze

Scope：QUALITY_AGENT Platform Milestone Management Standard

---

# 1. Position

QUALITY_AGENT_MILESTONE_STANDARD 定义 QUALITY_AGENT 平台所有 Capability、Engine、Agent 的统一 Milestone 管理规范。

本规范回答四个问题：

- 当前建设到哪里；
- 本阶段交付什么；
- 本阶段明确不做什么；
- 如何判断本阶段完成。

本规范不定义业务能力、架构设计或工程实现，仅定义平台统一的里程碑管理方式。

---

# 2. Scope

适用于 QUALITY_AGENT 平台所有项目，包括但不限于：

- Business Agent
- Knowledge Capability
- Quality Risk
- Repeat Case
- Quality Check
- Future Capability
- Future Engine

所有项目均应遵循统一的 Milestone 管理模式。

---

# 3. Milestone Structure

每个 Milestone 必须包含以下内容：

| 字段 | 说明 |
|------|------|
| Version | 当前 Milestone 版本 |
| Status | 当前状态 |
| Goal | 本阶段目标 |
| In Scope | 本阶段建设范围 |
| Out of Scope | 本阶段明确不建设内容 |
| Deliverables | 本阶段交付件 |
| Definition of Done | 完成标准 |
| Next Milestone | 下一阶段规划 |

---

# 4. Milestone Lifecycle

统一生命周期如下：

Planning

↓

Development

↓

Verification

↓

Regression

↓

Freeze

↓

Release

↓

Next Milestone

所有 Capability、Engine 必须遵循统一生命周期。

---

# 5. Deliverables

每个 Milestone 至少应包含以下交付件：

- Baseline（如有更新）
- Requirements（如有更新）
- Design（如有更新）
- Engine
- Test Report
- Release Notes
- CHANGELOG
- Release Package

交付件应保持版本一致。

---

# 6. Definition of Done

Milestone 完成必须满足以下全部条件。

## 6.1 Document

如本阶段涉及文档更新，应完成：

- Baseline Freeze
- Requirements Freeze
- Design Freeze
- Contract Freeze

---

## 6.2 Engineering

Engine 开发完成。

完成对应功能开发。

---

## 6.3 Verification

必须完成：

- Unit Test PASS
- Integration Test PASS（如适用）
- Regression PASS

---

## 6.4 Package

必须完成：

- QAE Install PASS
- QAE Verify PASS
- Release Package Generated

---

## 6.5 Repository

必须完成：

- Git Repository Updated
- CHANGELOG Updated
- Release Notes Updated

---

满足以上全部条件后，Milestone 方可进入 Release 状态。

---

# 7. Release Rule

每个 Milestone 完成后，应形成正式 Release。

Release 至少包含：

- Release Notes
- CHANGELOG
- Release Package
- PMO Status Update

Release 是平台正式交付单位。

Package 仅作为工程交付单位。

---

# 8. PMO Integration

PMO 仅记录项目状态，不记录设计内容。

推荐记录如下：

Current Release

Current Milestone

Current Status

Current Deliverables

Next Milestone

PMO 不记录：

- Baseline 内容
- Requirements 内容
- Design 内容
- Engine 实现细节

---

# 9. Version Rule

Milestone Version 与 Engine Version 相互独立。

示例：

Business Agent

Engine：

V1.3

Milestone：

M1

Release：

R1

版本之间通过 Release 建立关联。

---

# 10. Standard Principles

QUALITY_AGENT 平台遵循以下统一原则：

- Contract Driven Development
- Milestone Driven Delivery
- Release Driven Management

平台建设遵循：

Baseline

↓

Requirements

↓

Design

↓

Contract

↓

Milestone

↓

Engine

↓

Verification

↓

Release

↓

PMO

各阶段职责明确、边界清晰，不跨阶段承担职责。

---

# 11. Compliance

QUALITY_AGENT 平台所有 Capability、Engine 必须遵循本规范。

新增项目默认采用本标准。

未满足 Definition of Done 的 Milestone 不得进入 Release。

---

# Change History

| Version | Status | Description |
|----------|--------|-------------|
| V1.0 | Freeze | Initial platform milestone management standard. |
---
title: Intent Classification (v14)
version: v14
impact: MEDIUM
when: "确定用户请求应路由到哪个模式"
---

# Intent Classification (v14)

## Overview

意图分类决定用户请求应路由到哪个模式处理器。

## Intent Types

### Scaffold (代码生成)

**Keywords**: 创建, 生成, scaffold, 模块, CRUD, API, 新增, 添加

**Examples**:
- "创建 Product 模块"
- "生成 User CRUD"
- "scaffold Order API"

**Priority**: HIGH - 包含明确生成关键词时优先

### Guide (开发指南)

**Keywords**: 如何, 怎样, ?, 怎么, 什么, 为什么, 使用, 实现

**Examples**:
- "如何实现 CRUD?"
- "怎样配置表单验证?"
- "ListBuilder 怎么用?"

**Priority**: MEDIUM - 默认模式

### Debug (问题排查)

**Keywords**: 报错, 错误, 失败, bug, 不工作, 异常, 问题

**Examples**:
- "CRUD 报错"
- "表单提交失败"
- "为什么不工作?"

**Priority**: HIGH - 包含错误关键词时优先

### Learn (模式提取)

**Keywords**: /qscmf-learn

**Examples**:
- "/qscmf-learn"

**Priority**: MAX - 命令触发

## Classification Rules

1. 命令触发 (/qscmf-learn) → Learn 模式
2. 包含 Scaffold 关键词 → Scaffold 模式
3. 包含 Debug 关键词 → Debug 模式 (待实现)
4. 包含 Guide 关键词 → Guide 模式
5. 默认 → Guide 模式

## Version Differences

v13 和 v14 使用相同的意图分类规则。

---

**Related Rules**:
- [Scaffold 工作流](workflow/workflow-create-module.md) - 完整模块创建流程
- [CRUD 开发](crud/crud-table-columns.md) - 表格列配置
- [API 开发](api/api-response-format.md) - API 响应格式
- [字段类型推断](field-type-inference.md) - 表单字段类型映射

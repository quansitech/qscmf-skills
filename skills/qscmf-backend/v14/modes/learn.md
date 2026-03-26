---
title: Learn Mode (v14)
version: v14
impact: MEDIUM
when: "通过 /qscmf-learn 命令从开发会话中提取可复用模式"
---

# Learn Mode (v14)

## Trigger

```
/qscmf-learn
```

Run after a QSCMF development session to extract reusable patterns and detect documentation issues.

---

## Overview

Learn mode analyzes the conversation to:

1. **Extract Patterns** - Reusable code patterns (Redis Lock, Queue Job, etc.)
2. **Capture API Usage** - New methods/parameters discovered
3. **Learn Field Types** - Field name → type mappings
4. **Detect Issues** - Documentation vs. actual usage discrepancies

---

## Workflow

完整工作流请参考:

**→ [../../_shared/learn/workflow.md](../../_shared/learn/workflow.md)**

---

## Quick Reference

### Step Summary

| Step | Action | Output |
|------|--------|--------|
| 1 | Detect Version | v13 or v14 |
| 2 | Analyze Conversation | Candidate learnings |
| 2.5 | Correction Scan | Issues found |
| 3 | Categorize | Pattern/API/Field Type |
| 4 | Check Idempotency | Skip duplicates |
| 5 | Generate Proposals | User confirmation |
| 6 | Group by Risk | Review priority |
| 7 | User Confirmation | Apply or skip |
| 8 | Update Log | Traceable record |

### Learning Types

| Type | Target Path |
|------|-------------|
| Pattern | `v14/rules/pattern/pattern-{name}.md` |
| API Usage | `v14/rules/{api}.md` |
| Field Type | `v14/rules/field-type-inference.md` |
| Template | `v14/templates/{component}.php.tpl` |

---

## Related Files

- [workflow.md](../../_shared/learn/workflow.md) - 完整工作流
- [log.yaml](../../_shared/learn/log.yaml) - 学习日志
- [cache.yaml](../../_shared/learn/cache.yaml) - 学习缓存

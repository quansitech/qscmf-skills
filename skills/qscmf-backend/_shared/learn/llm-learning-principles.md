# LLM Learning Principles for Skill Documentation

This document records key principles for designing skill documentation that optimizes LLM learning efficiency.

## Core Principle: Concrete Over Abstract

### The Problem

When designing multi-version skill documentation, there's a tension between:
- **Extensibility**: Using abstract terms like `{version}`, `>=modern`, `legacy`
- **LLM Learning**: Using concrete terms like `v13`, `v14`, `>=v14`

### The Solution

**Use concrete version numbers in learning content, with centralized mapping for extensibility.**

```
✅ Good: target: "v14/rules/pattern/pattern-redis-lock.md"
❌ Bad:  target: "{version}/rules/pattern/pattern-redis-lock.md"
```

## Analysis

### Comparison

| Dimension | Concrete (v13/v14) | Abstract ({version}) |
|-----------|-------------------|---------------------|
| Precision | ✅ High - Clear version boundary | ⚠️ Medium - Requires inference |
| Token Efficiency | ✅ Short, unambiguous | ⚠️ Needs context explanation |
| Extensibility | ❌ Global changes for new versions | ✅ Auto-compatible |
| Knowledge Transfer | ❌ Version-specific hard to reuse | ✅ Patterns reusable |
| Few-shot Reasoning | ✅ Direct example matching | ⚠️ Requires version resolution first |

### Why Concrete Wins for LLM

1. **Reduced Reasoning Chain**
   - LLM sees `v14` → immediately knows scope
   - LLM sees `>=modern` → must first query "what is modern?"

2. **Few-shot Learning Efficiency**
   - Concrete version examples can be directly reused
   - Abstract examples must first be instantiated

3. **Lower Error Rate**
   - `{version}` placeholders easily mistaken as literal values
   - Version numbers produce no ambiguity

4. **Clearer Knowledge Graph**
   ```
   v14 → React → AntdAdmin → setDataSource()
   v13 → jQuery → ListBuilder → setTableDataList()
   ```
   Explicit mappings are easier to learn than implicit rules.

## Implementation Pattern

### Directory Structure

```
qscmf-backend/
├── SKILL.md                    # Entry point with version detection
├── _shared/
│   └── learn/
│       ├── version-mapping.yaml    # Centralized version config
│       └── llm-learning-principles.md
├── v13/                        # Version-specific content
│   ├── SKILL.md
│   └── rules/
└── v14/
    ├── SKILL.md
    └── rules/
```

### Version Mapping Config

```yaml
# _shared/learn/version-mapping.yaml
detection:
  source: "composer.json"
  package: "tiderjian/think-core"
  mapping:
    "^14.0": "v14"
    "^13.0": "v13"
  default: "v14"

features:
  v14:
    rendering: "react"
    primary_api: "AntdAdmin\\Component\\Table"
  v13:
    rendering: "jquery"
    primary_api: "Qscmf\\Builder\\ListBuilder"
```

### Learning Content Pattern

```yaml
# In cache.yaml, log.yaml, etc.
learnings:
  - id: "L001"
    target: "v14/rules/pattern/pattern-redis-lock.md"  # Concrete version
    version_constraint: ">=v14"                         # Concrete constraint
```

## Adding New Versions

When adding a new version (e.g., v15):

1. Update `version-mapping.yaml`:
   ```yaml
   detection:
     mapping:
       "^15.0": "v15"

   features:
     v15:
       rendering: "react"
       primary_api: "AntdAdmin\\Component\\Table"
   ```

2. Create `v15/` directory with version-specific content

3. Learning content with `>=v14` constraints will need manual review for v15 compatibility

## Trade-offs Accepted

1. **Global updates needed for new versions** - Acceptable because versions change infrequently
2. **Some duplication across version directories** - Acceptable for learning clarity

## Anti-patterns to Avoid

1. **Don't use placeholders in learning content**
   ```yaml
   # ❌ Bad
   target: "{version}/rules/api.md"

   # ✅ Good
   target: "v14/rules/api.md"
   ```

2. **Don't use abstract mode names without version mapping**
   ```yaml
   # ❌ Bad
   version_constraint: ">=modern"

   # ✅ Good
   version_constraint: ">=v14"
   ```

3. **Don't duplicate version detection logic**
   - Keep it in one place (SKILL.md entry point)
   - Use version-mapping.yaml as single source of truth

## Related Files

- [version-mapping.yaml](./version-mapping.yaml) - Centralized version configuration
- [workflow.md](./workflow.md) - Learning workflow
- [cache.yaml](./cache.yaml) - Learning cache structure

---
name: qscmf
description: QSCMF framework intelligent dispatcher - automatically detects project version and routes to appropriate specialized skills. Use for ANY QSCMF-related tasks including version upgrades, backend CRUD development, admin panel generation, API development, database operations, and feature implementation. Triggers on QSCMF project context, qs_cmf framework references, or explicit requests for QSCMF development work.
---

# QSCMF Intelligent Dispatcher

## Overview

QSCMF skill is the central coordinator that intelligently analyzes user intent and routes requests to specialized sub-skills with appropriate version parameters. It automatically detects the current QSCMF version from composer files and eliminates manual version specification.

## Decision Workflow

### Step 1: Detect User Intent

Analyze the user's request to categorize into one of two primary intents:

#### Upgrade Intent
**Indicators:** 升级, upgrade, update, migrate, 迁移, version numbers (v13, v14, v15), "从...到..."

**Examples:**
- "帮我升级到 v15"
- "项目需要从 v13 升级到 v15"
- "升级 qscmf"

#### Development Intent
**Indicators:** 创建, 生成, 添加, 实现, build, create, generate, add, implement, 模块, module, CRUD, 后台, backend, admin, Controller, Model, API, 功能

**Examples:**
- "创建一个 User 模块"
- "生成后台管理界面"
- "添加 CRUD 功能"
- "实现用户管理"

### Step 2: Auto-Detect Version

Execute version detection script to determine current project version:

```bash
php scripts/detect_version.php --format=json
```

**Detection Priority:**
1. `composer.lock` - reads exact installed version from `tiderjian/qscmf` package
2. `composer.json` - fallback to version constraint in require section
3. **Manual询问** - if both files missing or package not found

**Version Format:**
- 13.x.x → v13
- 14.x.x → v14
- 15.x.x → v15

**Output Example:**
```json
{
  "version": "v14",
  "source": "composer.lock",
  "raw": "14.5.2"
}
```

### Step 3: Route to Appropriate Skill

#### For Upgrade Intent → Invoke `qscmf-upgrade`

**Parameter Format:** `{source_version}_{target_version}`

**Examples:**
- v13 → v14: `qscmf-upgrade v13_v14`
- v14 → v15: `qscmf-upgrade v14_v15`
- v13 → v15: `qscmf-upgrade v13_v15`

**Version Resolution:**
- Source version: Auto-detected from composer files
- Target version: Extracted from user input OR ask if ambiguous

**Ambiguous Input Handling:**

| User Input | Detected | Action |
|------------|----------|--------|
| "升级 qscmf" | v14 | Ask: "升级到哪个版本？(v15)" |
| "帮我升级" | v14 | Ask: "升级到哪个版本？(v15)" |
| "从 v13 升级" | v14 | Ask: "目标版本是？(v14/v15)" |

#### For Development Intent → Invoke `qscmf-backend`

**Parameter Format:** `{version}`

**Examples:**
- Detected v14: `qscmf-backend v14`
- Detected v15: `qscmf-backend v15`

**Version Resolution:**
- Use auto-detected version directly
- No manual specification needed

## Handling Edge Cases

### No Composer Files Found

When version detection fails:

```
❌ composer.lock not found
❌ composer.json not found
```

**Ask user:**
```
"无法检测到 QSCMF 版本。请提供当前版本号 (v13/v14/v15)"
```

### Version Mismatch Detected

When auto-detected version contradicts user input:

| Detected | User Says | Action |
|----------|-----------|--------|
| v14 | "从 v13 升级" | Warn: "检测到当前版本 v14，但您提到 v13。是否继续从 v13 升级？" |
| v14 | "v13 项目开发" | Warn: "检测到当前版本 v14，是否使用 v14 开发？" |

### Multiple Projects in Workspace

When workspace contains multiple QSCMF projects:
1. Use current working directory (CWD) for detection
2. If ambiguous, ask user to specify target project
3. Present detected versions for each project directory

## Decision Flowchart

```
User Request
     ↓
Analyze Intent
     ↓
┌────────────────┐
│ Intent Type?   │
└────────────────┘
     ↓
┌────────────┴────────────┐
↓                         ↓
Upgrade?              Development?
↓                         ↓
Detect Current          Detect Current
↓                         ↓
Infer Target            qscmf-backend
↓                         ↓
qscmf-upgrade           (with version)
{source}_{target}
```

## Keyword Detection Patterns

### Upgrade Patterns
```regex
/升级|upgrade|update|migrate|迁移/
/v\d+/
/从.*到/
```

### Development Patterns
```regex
/创建|生成|添加|实现|build|create|generate|add|implement/
/模块|module|CRUD|后台|backend|admin/
/Controller|Model|API|功能|feature/
```

## Resources

### scripts/detect_version.php

PHP script that detects QSCMF version from composer files.

**Usage:**
```bash
# Text output (default)
php scripts/detect_version.php

# JSON output
php scripts/detect_version.php --format=json
```

**Returns:**
- Text mode: `v14`
- JSON mode: `{"version": "v14", "source": "composer.lock", "raw": "14.5.2"}`

### references/decision-logic.md

Complete decision logic reference including:
- Detailed intent classification rules
- Version detection algorithms
- Edge case handling strategies
- Implementation patterns

Load this reference when dealing with ambiguous user input or complex version scenarios.

## Integration with Sub-Skills

This dispatcher coordinates with specialized skills:

1. **qscmf-upgrade** - Handles version migration with breaking changes documentation
2. **qscmf-backend** - Manages CRUD development, admin panels, APIs for specific versions

Each sub-skill receives pre-detected version information, eliminating redundant version queries.

## Implementation Notes

- **Always run version detection before routing** - ensures accurate skill selection
- **Validate version detection success** - handle failures gracefully with user prompts
- **Check for version conflicts** - warn users when detected version differs from their stated version
- **Support incremental upgrades** - v13→v14→v15 is preferred over v13→v15 directly

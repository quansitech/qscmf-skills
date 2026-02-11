# QSCMF Decision Logic

## Intent Detection Decision Tree

### Step 1: Analyze User Input

Identify keywords and patterns in the user's request to determine the intent category.

#### Version Upgrade Indicators

**Common keywords:**
- 升级, upgrade, update, migrate, 迁移
- Version numbers: v13, v14, v15, etc.
- "从...到..." (from...to...), "升级到" (upgrade to)

**Examples:**
- "帮我升级到 v15" → Version upgrade
- "项目需要从 v13 升级到 v15" → Version upgrade
- "升级 qscmf" → Version upgrade (requires version clarification)

#### Backend Development Indicators

**Common keywords:**
- 创建, 生成, 添加, 实现, build, create, generate, add, implement
- 模块, module, CRUD, 后台, backend, admin
- Controller, Model, API, 功能, feature

**Examples:**
- "创建一个 User 模块" → Backend development
- "生成后台管理界面" → Backend development
- "添加 CRUD 功能" → Backend development
- "实现用户管理" → Backend development

### Step 2: Version Detection

#### Auto-Detection Priority

1. **composer.lock** (highest priority)
   - Contains exact installed versions
   - Most reliable source

2. **composer.json** (fallback)
   - Contains version constraints
   - May have range operators (^, ~, *)

3. **Manual询问** (when auto-detection fails)
   - Ask user for current version
   - Ask user for target version (if upgrade)

#### Version Format

QSCMF uses semantic versioning:
- 13.x.x → v13
- 14.x.x → v14
- 15.x.x → v15

### Step 3: Skill Routing

#### Version Upgrade Route

**Skill:** `qscmf-upgrade`

**Parameters:**
- Format: `{source_version}_{target_version}`
- Examples:
  - v13 → v14: `qscmf-upgrade v13_v14`
  - v14 → v15: `qscmf-upgrade v14_v15`
  - v13 → v15: `qscmf-upgrade v13_v15`

**Version Inference:**
- Source version: Auto-detect from composer files
- Target version: Infer from user input or ask

**Ambiguous Cases Requiring Clarification:**

| User Input | Detected Current | Action |
|------------|------------------|--------|
| "升级 qscmf" | v14 | Ask: "升级到哪个版本？(v15)" |
| "升级项目" | v14 | Ask: "升级到哪个版本？(v15)" |
| "帮我升级" | v14 | Ask: "升级到哪个版本？(v15)" |
| "从 v13 升级" | v14 | Ask: "目标版本是？(v14/v15)" |

#### Backend Development Route

**Skill:** `qscmf-backend`

**Parameters:**
- Format: `{version}`
- Examples:
  - v14: `qscmf-backend v14`
  - v15: `qscmf-backend v15`

**Version Inference:**
- Auto-detect from composer files
- No version parameter needed if detected successfully

### Step 4: Handle Edge Cases

#### No Composer Files

**Detection fails:**
```
❌ composer.lock not found
❌ composer.json not found
```

**Action:** Ask user for current version

```
"无法检测到 QSCMF 版本。请提供当前版本号 (v13/v14/v15)"
```

#### Version Mismatch

**Detected version contradicts user input:**

| Detected | User Says | Action |
|----------|-----------|--------|
| v14 | "从 v13 升级" | Warn: "检测到当前版本 v14，但您提到 v13。是否继续从 v13 升级？" |
| v14 | "v13 项目开发" | Warn: "检测到当前版本 v14，是否使用 v14 开发？" |

#### Multiple Projects

**Workspace contains multiple QSCMF projects:**

1. Check current working directory
2. If ambiguous, ask user to specify
3. Suggest detected versions

## Decision Flowchart

```
          User Input
               ↓
        ┌──────────────┐
        │ Intent Type? │
        └──────────────┘
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
Upgrade?          Development?
    ↓                   ↓
Detect Current     Detect Current
    ↓                   ↓
Infer Target      Use qscmf-backend
    ↓                   ↓
qscmf-upgrade     (with version)
{source}_{target}
```

## Implementation Notes

### Keyword Matching Patterns

```php
// Upgrade patterns
/升级|upgrade|update|migrate|迁移/
/v\d+/
/从.*到/

// Development patterns
/创建|生成|添加|实现|build|create|generate|add|implement/
/模块|module|CRUD|后台|backend|admin/
/Controller|Model|API|功能|feature/
```

### Version Detection Algorithm

1. Search for `tiderjian/qscmf` in composer.lock
2. If not found, search in composer.json require section
3. Extract version string (e.g., "13.0.0", "14.5.2")
4. Normalize to v{major} format
5. Return with source information

### Error Handling

- **File not found:** Return null, trigger manual询问
- **Invalid JSON:** Log error, trigger manual询问
- **Package not found:** Return null, trigger manual询问
- **Version parse error:** Log error, trigger manual询问

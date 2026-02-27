# Deep Scan Implementation

Detailed implementation for `/qscmf-learn --deep-scan` Phase 1-5.

> **Design Note**: Uses concrete version numbers (v13, v14) for better LLM learning efficiency. See [llm-learning-principles.md](./llm-learning-principles.md) for rationale.

---

## Phase 1: 文档清单扫描

### Implementation Steps

```
P1.1 版本检测
├── 读取 composer.json 检测 "tiderjian/think-core" 版本
└── "^13.0" → v13, "^14.0" → v14

P1.2 路径构建
├── SKILL_ROOT = ~/.claude/skills/qscmf-backend/
├── SCAN_PATHS = [
│     v13/rules/**/*.md,        # v13 规则文件
│     v13/references/**/*.md,   # v13 参考文档
│     v14/rules/**/*.md,        # v14 规则文件
│     v14/references/**/*.md,   # v14 参考文档
│     _shared/references/*.md,  # 共享参考
│     _shared/concepts/*.md     # 共享概念
│   ]
└── 排除: archive/, *.bak, .git/

P1.3 文件扫描
├── 对每个 SCAN_PATH 执行 Glob 匹配
└── 输出: file_list[]

P1.4 哈希计算
├── SHA256(file_content)
├── 与 cache.yaml 比对
│   ├── 相同 → 标记 CACHED, 跳过
│   └── 不同/不存在 → 标记 NEEDS_SCAN
└── 输出: file_manifest[] (path, hash, status)

P1.5 缓存更新
└── 将新哈希写入 cache.yaml
```

### Output Format

```yaml
# phase1_manifest.yaml
scan_metadata:
  version: "v14"                    # 检测到的具体版本
  scanned_at: "2025-02-27T10:00:00Z"
  total_files: 48
  cached_files: 35
  new_or_changed: 13

files:
  - path: "v14/rules/antdadmin.md"  # 具体版本路径
    hash: "sha256:a1b2c3d4..."
    status: "NEEDS_SCAN"
    size_bytes: 8192
    doc_type: "rules"
```

---

## Phase 2: 规则提取

### Implementation Steps

```
P2.1 代码块提取
├── 正则: /```php\n([\s\S]*?)\n```/g
└── 输出: code_blocks[] (content, line_range)

P2.2 API 签名解析
├── 解析: 类实例化、方法调用、静态调用、链式调用
└── 输出: api_calls[] (class, method, params, return_type)

P2.3 配置项识别
├── 正则: /C\s*\(\s*['"]([A-Z_]+)['"]\s*\)/
├── 正则: /env\s*\(\s*['"]([A-Z_]+)['"]\s*\)/
└── 输出: config_refs[]

P2.4 最佳实践识别
├── 关键词: "应该", "必须", "注意", "重要", "SHOULD", "MUST"
├── 版本标记: "v14-only", "v13-only", "deprecated"
└── 输出: best_practices[]
```

### Rule Types

| 类型 | 匹配模式 | 提取字段 |
|------|----------|----------|
| `code_example` | \`\`\`php ... \`\`\` | content, line_range, apis |
| `api_signature` | Markdown 表格中的方法定义 | method, params, return_type |
| `config_ref` | C('CONFIG_KEY') | key, context |
| `best_practice` | 关键词标记的段落 | content, severity, version |

### Output Format

```yaml
document: "v14/rules/antdadmin.md"   # 具体版本路径
file_hash: "sha256:a1b2c3d4..."
extracted_at: "2025-02-27T10:00:00Z"

rules:
  - id: "R001"
    type: "code_example"
    line_start: 27
    line_end: 41
    content: |
      $table = new Table();
      $table->setMetaTitle('商品列表')
          ->columns(function (Table\ColumnsContainer $container) {...})
    apis:
      - class: "AntdAdmin\\Component\\Table"
        method: "setMetaTitle"
        params: ["string"]
        return_type: "self"

  - id: "R002"
    type: "api_signature"
    line_start: 106
    content: "| `text($field, $title)` | Text column |"
    apis:
      - class: "AntdAdmin\\Component\\Table\\ColumnsContainer"
        method: "text"
        params: ["$field:string", "$title:string"]
        return_type: "Column"

  - id: "R003"
    type: "best_practice"
    line_start: 320
    content: "v14 projects should use AntdAdmin\\Component\\Table"
    severity: "recommendation"
    version_constraint: ">=v14"
```

> 完整 Schema 见 [schema/extracted_rules.yaml](./schema/extracted_rules.yaml)

---

## Phase 3: 代码库验证

### Verification Matrix

| 验证类型 | 搜索策略 | 匹配条件 |
|---------|---------|---------|
| 类存在 | grep "class.*{ClassName}" app/ | 命名空间 + 类名双匹配 |
| 方法调用 | grep "->{methodName}" app/ | 至少1处实际使用 |
| 参数顺序 | 正则提取调用参数 | 类型 + 顺序一致 |
| 配置引用 | grep "C('{config_key}')" app/ | 配置项被使用 |

### Implementation Steps

```
P3.1 搜索策略选择
├── code_example → 代码搜索验证
├── api_signature → 类定义 + 调用验证
├── config_ref → 配置使用验证
└── best_practice → 模式匹配验证

P3.2 类存在性验证
├── grep -r "class ClassName" app/ package/
├── 验证命名空间与文档一致
└── 结果: FOUND | NAMESPACE_MISMATCH | NOT_FOUND | AMBIGUOUS

P3.3 方法调用验证
├── grep -r "->methodName" app/
├── 统计使用次数
└── 验证参数模式

P3.4 配置项验证
├── grep -r "C('CONFIG_KEY')" app/
└── 验证配置项是否定义
```

### Verification Status

| 状态 | 含义 | 后续动作 |
|------|------|----------|
| `VERIFIED` | 文档与代码完全一致 | 无需修改 |
| `MISMATCH` | 文档与代码存在差异 | 标记为 [FIX] |
| `NOT_FOUND_IN_CODE` | 文档有但代码无 | 标记为 [DEPRECATE] |
| `NOT_FOUND_IN_DOC` | 代码有但文档无 | 标记为 [ADD] |
| `AMBIGUOUS` | 多个匹配，无法确定 | 需人工审核 |

### Output Format

```yaml
# validation_report.yaml
validation_metadata:
  codebase_root: "/var/www/zt-action"
  scanned_at: "2025-02-27T10:00:00Z"
  total_rules: 156
  validated: 142

validations:
  - rule_id: "R001"
    document: "v14/rules/antdadmin.md"
    type: "api_signature"
    api: "AntdAdmin\\Component\\Table::setMetaTitle"
    status: "VERIFIED"
    evidence:
      - file: "app/Admin/Controller/ProductController.class.php"
        line: 45
        snippet: "$table->setMetaTitle('商品管理')"
    usage_count: 12

  - rule_id: "R015"
    document: "v14/rules/test/test-wall-mock.md"
    type: "code_example"
    api: "Common\\Lib\\Wall\\PaymentWall"
    status: "MISMATCH"
    evidence:
      expected: "Common\\Lib\\Wall\\PaymentWall"
      actual: "Common\\Lib\\BusinessWall\\NoLogClient"
      file: "app/Common/Lib/BusinessWall/NoLogClient.class.php"
    proposal_type: "FIX"
```

---

## Phase 4: 差异分类

### Decision Tree

```
文档有规则?
├── 是 → 代码中存在?
│   ├── 是 → 行为一致?
│   │   ├── 是 → [CONFIRM]
│   │   └── 否 → [FIX]
│   └── 否 → [DEPRECATE]
└── 否 → 代码有此功能?
    ├── 是 → [ADD]
    └── 否 → 跳过
```

### Classification Types

#### [ADD] - 新功能
- **条件:** 代码有但文档没有
- **置信度要求:** >= 60
- **输出:** 添加新章节

#### [FIX] - 纠错
- **条件:** 文档与代码不一致
- **置信度要求:** >= 70
- **输出:** 修正文档内容

#### [DEPRECATE] - 废弃
- **条件:** 文档有但代码已移除
- **置信度要求:** >= 80
- **输出:** 标记为废弃或删除

#### [CONFIRM] - 确认
- **条件:** 文档与代码一致
- **输出:** 无需修改

### Confidence Algorithm

```python
def calculate_confidence(result):
    score = 50  # 基础分

    # 代码证据 (+50)
    if result.has_class_definition: score += 15
    if result.has_method_call: score += 15
    if result.usage_count >= 3: score += 10
    if result.signature_matches: score += 10

    # 对话证据 (+35)
    if result.has_user_statement: score += 20
    if result.has_code_block_evidence: score += 15

    # 版本匹配 (+10)
    if result.version_matches: score += 10

    return min(100, max(0, score))
```

| 评分 | 建议 |
|------|------|
| HIGH (80+) | 自动生成提案，用户确认 |
| MEDIUM (50-79) | 生成提案，需要详细审核 |
| LOW (<50) | 标记为可选，默认跳过 |

### Output Format

```markdown
## Deep Scan Results

### Summary
- Documents scanned: 48
- Rules extracted: 156
- [ADD] New features: 5
- [FIX] Corrections: 12
- [DEPRECATE] Deprecated: 2
- [CONFIRM] Verified: 137

### [ADD] New Features (5)
#### 1. ContentHelperTrait::formItemFilter()
- **Found in**: `app/Admin/Controller/PostController.class.php:163`
- **Evidence**: `$table->setFormItemFilter($this->formItemFilter())`
- **Proposal**: Add to `v14/rules/crud/crud-form-validation.md`

### [FIX] Corrections (12)
#### 1. NoLogClient namespace mismatch
- **Document**: `v14/rules/test/test-wall-mock.md:32`
- **Claims**: `Common\Lib\Wall\PaymentWall`
- **Actual**: `Common\Lib\BusinessWall\NoLogClient`
- **Proposal**: Update examples to use actual project classes

### [DEPRECATE] Deprecated (2)
...
```

---

## Phase 5: 安全防护

### Content Redaction Patterns

```regex
# API Key
/(api[_-]?key|apikey|api_secret)\s*[:=]\s*['"]?[a-zA-Z0-9]{20,}/gi
→ <REDACTED:API_KEY>

# Password
/(password|passwd|pwd)\s*[:=]\s*['"]?[^\s'"]+/gi
→ <REDACTED:PASSWORD>

# Token
/(token|access_token|auth_token)\s*[:=]\s*['"]?[a-zA-Z0-9_-]{20,}/gi
→ <REDACTED:TOKEN>

# Database connection
/mysql:\/\/[^:]+:[^@]+@/gi
→ <REDACTED:DB_CONNECTION>

# Private key (PEM)
/-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----/gi
→ <REDACTED:PRIVATE_KEY>

# AWS Keys
/(aws_access_key_id|aws_secret_access_key)\s*[:=]\s*['"]?[a-zA-Z0-9\/+=]+/gi
→ <REDACTED:AWS_KEY>

# JWT tokens
/eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*/gi
→ <REDACTED:JWT>

# Generic secrets
/(secret|secret_key|private_key)\s*[:=]\s*['"]?[a-zA-Z0-9_\-]{16,}/gi
→ <REDACTED:SECRET>
```

### File Exclusion Patterns

```yaml
exclude_patterns:
  # Environment files
  - ".env*"
  - ".env.local"
  - ".env.production"

  # Configuration with credentials
  - "config/database.php"
  - "config/credentials.php"
  - "config/secrets.php"

  # Key and certificate files
  - "*.pem"
  - "*.key"
  - "*.crt"

  # Dependencies
  - "vendor/*"
  - "node_modules/*"

  # Logs and cache
  - "storage/logs/*"
  - "runtime/cache/*"

  # IDE files
  - ".idea/*"
  - ".vscode/*"

  # Build artifacts
  - "dist/*"
  - "build/*"

  # Git
  - ".git/*"
```

### Prompt Injection Prevention

All code content sent to LLM is wrapped in boundary tags:

```
<code_content>
{actual_code_content_here}
</code_content>
```

### Supported Redaction Types

| Type | Pattern | Example |
|------|---------|---------|
| `api_key` | API keys (20+ chars) | `api_key = "sk-abc..."` |
| `password` | Password fields | `password = "secret"` |
| `token` | Auth tokens (20+ chars) | `token = "ghp_..."` |
| `db_connection` | MySQL connection strings | `mysql://user:pass@host` |
| `private_key` | PEM private keys | `-----BEGIN RSA PRIVATE KEY-----` |
| `aws_key` | AWS credentials | `aws_access_key_id = "AKIA..."` |
| `jwt` | JWT tokens | `eyJhbGci...` |
| `secret` | Generic secrets (16+ chars) | `secret_key = "..."` |

### Integration Points

| Phase | Security Action |
|-------|-----------------|
| Phase 1 | Filter files with FileExcluder |
| Phase 2 | Wrap extracted code in boundary tags |
| Phase 3 | Sanitize code before LLM analysis |
| Output | Verify no sensitive data in reports |

---

## Related Files

- [version-mapping.yaml](./version-mapping.yaml) - Version detection and feature mapping
- [llm-learning-principles.md](./llm-learning-principles.md) - Design decisions for LLM learning
- [cache.yaml](./cache.yaml) - Learning cache structure
- [schema/extracted_rules.yaml](./schema/extracted_rules.yaml) - Rule extraction schema

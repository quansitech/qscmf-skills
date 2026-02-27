# QSCMF Learning Workflow

Triggered by `/qscmf-learn` after a QSCMF development session.

## Step 1: Detect QSCMF Version

1. Read `composer.json` for `tiderjian/think-core` version
2. Fallback: scan conversation for markers (Inertia.js/AntdAdmin → v14, ListBuilder/jQuery → v13)
3. If uncertain, ask user

**Output:** `$qscmfVersion` ("v13" or "v14"), `$basePath` = `skills/qscmf-backend/{version}/`

---

## Step 2: Analyze Conversation

Scan conversation for:
- QSCMF code blocks (```php)
- Problem → solution patterns
- Undocumented API usage
- Reusable patterns, field type mappings, version differences
- "Good to know", "Important", "Just discovered" markers

**Output:** Candidate learnings + potential correction issues (from Step 2.5)

---

## Step 2.5: Correction Scan

**Progressive Verification Strategy:**

| Level | Trigger | Token Cost | Content |
|-------|---------|------------|---------|
| 1 | Default | ~0 | Dialogue evidence extraction |
| 2 | Default | ~1k | Document cross-validation |
| 3 | On-demand | ~2-5k | Single file read |
| 4 | Opt-in | ~50k+ | Deep scan (with warning) |

### Level 1: Dialogue Evidence (Default)

Extract from conversation:
- PHP code blocks → compare with documented APIs
- User contradictions ("文档说X但我发现Y")
- Version-specific keywords in wrong version docs

### Level 2: Document Cross-Validation (Default)

Scan `skills/qscmf-backend/{version}/rules/` and `references/` for:
- API consistency across files
- Version-specific content in wrong version
- Field-type rule conflicts
- Template-documentation completeness

### Level 3: Single File Read (On-demand)

When dialogue mentions specific file, read to verify evidence.

### Level 4: Deep Scan (Opt-in)

**Trigger:** `/qscmf-learn --deep-scan`

**Warning:**
```
⚠️ Deep Scan Warning
• 将扫描所有技能文档 (~50+ 个文件)
• 逐条与代码库进行比对验证
• 预计耗时: 2-5 分钟
• 额外 Token: 100,000-200,000
• 是否继续? [Yes] [No]
```

**Workflow:**
```
Phase 1: 文档清单扫描 → 输出文件列表 + 哈希
Phase 2: 规则提取 → 提取代码块、API签名、配置项、最佳实践
Phase 3: 代码库验证 → 在代码中验证每个规则
Phase 4: 差异分类 → [ADD]/[FIX]/[DEPRECATE]/[CONFIRM]
Phase 5: 安全防护 → 敏感数据脱敏、敏感文件排除
```

> 详细实现见 [deep-scan-impl.md](./deep-scan-impl.md)

---

## Step 3: Categorize Learnings

| Learning Type | Detection Pattern | Target Path |
|---------------|-------------------|-------------|
| Pattern | Reusable code (Redis Lock, Queue Job) | `$basePath/rules/pattern/pattern-{name}.md` |
| API Usage | New methods/parameters | `$basePath/rules/{api}.md` or `references/{topic}.md` |
| Field Type | Field name → type mapping | `$basePath/rules/field-type-inference.md` |
| Template | Missing boilerplate | `$basePath/templates/{component}.php.tpl` |

---

## Step 4: Check Idempotency

For each learning:
1. Check if target file exists
2. Generate content hash
3. Scan for similar content (semantic similarity)
4. >80% similarity → skip; 60-80% → propose update; <60% → new addition

---

## Step 5: Generate Proposals

### Learning Proposals (Additive)

```markdown
## Learning Proposals ({total} items)

### Minor Updates ({count}) - Batch Apply
- [ ] {description}
[Apply Minor] [Review All]

### New Content ({count}) - Review & Confirm
- [ ] {title} → Target: {path}

### Modifications ({count}) - Show Diff
- [ ] {title} → Target: {path}
```

### Issues Found (Corrective)

```markdown
## Issues Found ({total} items)

### High Confidence ({count})
⚠️ **[Type]** `{target_file}:{line}`
   **Document Claims**: {what doc states}
   **Evidence**: {code/user statement}
   **Proposed Correction**: {specific change}
   [Review] [Propose Fix] [Skip]

### Medium Confidence ({count})
...

### Low Confidence ({count}) - Optional
...
```

**Issue Types:** `api-mismatch`, `parameter-necessity`, `version-confusion`, `outdated-content`, `inconsistent`

---

## Step 6: Group by Risk Level

**Learning Proposals** (Lower Risk):
- Minor: batch apply (spelling, formatting)
- New: review individually
- Modification: show diff preview

**Correction Issues** (Higher Risk):
- HIGH: individual review required
- MEDIUM: review recommended
- LOW: optional (can skip all)

---

## Step 7: User Confirmation & Application

**Learning Proposals:** Can batch minor updates; others need individual review.

**Correction Issues:** ALWAYS require individual review.
1. Show full evidence (document claim + dialogue evidence)
2. User selects [Propose Fix] or [Skip]
3. If [Propose Fix]: show diff preview → confirm → apply with Edit tool
4. Log to `log.yaml`

---

## Step 8: Update Learning Log

```yaml
# _shared/learn/log.yaml
learnings:
  - id: "L001"
    hash: "sha256:abc123"
    extracted_at: "2025-02-26T10:00:00Z"
    confidence: "high"
    type: "pattern"
    target: "v14/rules/pattern/pattern-redis-lock.md"
    status: "applied"

corrections:
  - id: "C001"
    type: "api-mismatch"
    confidence: "high"
    target_file: "v14/rules/api-controllers.md"
    target_line: 45
    evidence:
      dialogue_code: "$table->setDataSource()"
      dialogue_statement: "文档说是 setDataList"
    proposed_correction: "Replace setDataList() with setDataSource()"
    status: "applied"
```

---

## Quick Reference

| Aspect | Value |
|--------|-------|
| **Trigger** | `/qscmf-learn` |
| **Prerequisites** | QSCMF project, conversation with QSCMF work |
| **Output** | Structured proposals → user selects → changes written → log updated |

### Key Principles

1. **Version-first**: Detect version before analysis
2. **Non-intrusive**: Post-hoc analysis
3. **Always confirm**: No auto-apply
4. **Idempotent**: Content hash prevents duplicates
5. **Traceable**: All changes logged
6. **Progressive verification**: Level 1-2 default, Level 3-4 opt-in
7. **Evidence-based**: Corrections require dialogue evidence

### Correction vs Addition

| Aspect | Addition (Learning) | Correction (Issues) |
|--------|---------------------|---------------------|
| Risk | Low-Medium | High |
| Evidence | New discovery | Contradiction |
| Default | Batch minor items | Individual review only |
| Operation | Write/Append | Edit (replace) |

### Confidence Scoring

| Level | Score | Criteria |
|-------|-------|----------|
| HIGH | ≥80 | Code evidence + User statement + Verification agree |
| MEDIUM | 50-79 | Single evidence type OR partial verification |
| LOW | <50 | Pattern match only, no direct evidence |

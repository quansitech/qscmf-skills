# QSCMF Learning Workflow

This workflow is triggered when the user invokes `/qscmf-learn` after a QSCMF development session.

## Purpose

Analyze the conversation context to extract QSCMF-related knowledge and propose improvements to the skill documentation.

## Workflow Steps

### Step 1: Detect QSCMF Version

**Goal**: Determine which version (v13 or v14) the work targets.

**Actions**:
1. Read `composer.json` from working directory if available
2. Check for `tiderjian/think-core ^13.0` → v13
3. Check for `tiderjian/think-core ^14.0` → v14
4. If not found, scan conversation for version markers:
   - "Inertia.js", "AntdAdmin", "React" → v14
   - "ListBuilder API", "jQuery" → v13
5. If still uncertain, ask user: "Which QSCMF version? (v13/v14)"

**Output**:
- `$qscmfVersion` = "v13" or "v14"
- `$basePath` = `skills/qsmcf-backend/{version}/`

---

### Step 2: Analyze Conversation

**Goal**: Extract QSCMF-related learnings from the conversation.

**Actions**:
1. Scan the **entire conversation history** for:
   - QSCMF code blocks (```php)
   - Problem → solution discovery patterns
   - API usage not documented in references/
   - Reusable code patterns
   - Field name → type mappings
   - Version differences mentioned
   - "Good to know", "Important", "Just discovered" markers

2. For each finding, extract:
   - Code snippet or description
   - Context (what problem it solved)
   - Confidence level (high/medium/low)

**Output**:
- List of candidate learnings with metadata
- List of potential correction issues (from Step 2.5)

---

### Step 2.5: Correction Scan (NEW)

**Goal**: Detect documentation issues from dialogue evidence and cross-validation.

**Progressive Verification Strategy**:

| Level | Trigger | Token Cost | Content |
|-------|---------|------------|---------|
| **Level 1** | Default | ~0 | Dialogue evidence extraction |
| **Level 2** | Default | ~1k | Document cross-validation |
| **Level 3** | On-demand | ~2-5k | Single file read (when mentioned) |
| **Level 4** | Opt-in | ~50k+ | Deep scan (with warning) |

**Actions**:

**Level 1: Dialogue Evidence Extraction** (Default)
1. Scan conversation for:
   - PHP code blocks → compare with documented APIs
   - User contradiction statements ("文档说X但我发现Y")
   - Version-specific keywords (jQuery in v14, Inertia in v13)
2. Extract evidence:
   - `code_block_evidence`: Actual code from dialogue
   - `user_statement_evidence`: User's explicit contradiction
   - `version_keyword_evidence`: Keywords in wrong version docs

**Level 2: Document Cross-Validation** (Default)
1. Scan skill documentation for:
   - API consistency across multiple files
   - Version-specific content in wrong version (v13 in v14, vice versa)
   - Field-type rule conflicts (duplicate patterns)
   - Template-documentation completeness
2. Target: `skills/qscmf-backend/{version}/rules/` and `references/` only (< 50 files)

**Level 3: Single File Read** (On-demand)
1. When dialogue mentions specific file (e.g., "ProductController.class.php:123")
2. Read that file to verify evidence
3. Update confidence score based on verification

**Level 4: Deep Scan** (Opt-in only)
1. Trigger: `/qscmf-learn --deep-scan` OR user explicit request
2. Show warning:
   ```
   ⚠️ Deep Scan Warning
   • 将扫描当前项目所有代码文件
   • 预计耗时: 30-60 秒
   • 额外 Token: 50,000-100,000
   • 是否继续? [Yes] [No]
   ```
3. If confirmed: scan `app/` directory (.php files only)
4. Verify API usage and parameter requirements against actual code

**Confidence Scoring**:
```
HIGH (>= 80): Code evidence + User statement + Verification all agree
MEDIUM (50-79): Single evidence type OR partial verification
LOW (< 50): Pattern match only, no direct evidence
```

**Output**:
- List of correction issues grouped by confidence (HIGH/MEDIUM/LOW)
- Each issue includes: type, target file, evidence, proposed correction

---

### Step 3: Categorize Learnings

**Goal**: Map each learning to its target location.

| Learning Type | Detection Pattern | Target Path |
|---------------|-------------------|-------------|
| **Pattern** | Reusable code (Redis Lock, Queue Job, Wall Class) | `$basePath/rules/pattern/pattern-{name}.md` |
| **API Usage** | New methods/parameters (ListBuilder, FormBuilder) | `$basePath/rules/{api}.md` or `$basePath/references/{topic}.md` |
| **Field Type** | Field name → type mapping (`*_price` → number) | `$basePath/rules/field-type-inference.md` |
| **Template** | Missing boilerplate code | `$basePath/templates/{component}.php.tpl` |
| **Version Diff** | v13 vs v14 behavioral difference | `$basePath/_shared/references/migration-v13-to-v14.md` |

**Optional Tags**: For multi-dimensional classification (e.g., `#v14-only`, `#workaround`)

---

### Step 4: Check Idempotency

**Goal**: Prevent duplicate proposals.

**For each learning**:
1. Check if target file exists
2. If exists, generate content hash of the learning
3. Scan file for similar content (semantic similarity)
4. If similarity > 80%, skip with note
5. If similarity 60-80%, propose update
6. If similarity < 60%, propose new addition

---

### Step 5: Generate Proposals

**Goal**: Present learnings AND corrections in structured, actionable formats.

**Two Separate Outputs**:

#### 1. Learning Proposals (Additive)

```markdown
## Learning Proposals ({total} items found)

### Minor Updates ({count}) - Batch Apply
- [ ] {description}
- [ ] {description}
[Apply Minor] [Review All]

### New Content ({count}) - Review & Confirm
- [ ] {title}
  Target: {path}
  [Preview diff]

### Modifications ({count}) - Show Diff & Confirm
- [ ] {title}
  Target: {path}
  [Show full diff]

[Apply Selected] [Select Individual] [Cancel]
```

#### 2. Issues Found (Corrective)

```markdown
## Issues Found ({total} items)

### High Confidence ({count})
⚠️ **[Type]** `{target_file}:{line}`

   **Document Claims**: {what documentation states}

   **Evidence from Dialogue**:
   ```php
   {code snippet or user statement}
   ```

   **Proposed Correction**: {specific change}

   [Review] [Propose Fix] [Skip]

### Medium Confidence ({count})
⚠️ **[Type]** `{target_file}:{line}`
   ...
   [Review] [Propose Fix] [Skip]

### Low Confidence ({count}) - Optional
ℹ️ **[Type]** `{target_file}:{line}`
   ...
   [Expand] [Skip All]
```

**Issue Types**:
- `api-mismatch`: Documented API name differs from actual usage
- `parameter-necessity`: Required/optional parameter mismatch
- `version-confusion`: v13 content in v14 docs (or vice versa)
- `outdated-content`: Information no longer accurate
- `inconsistent`: Contradiction between documentation files

---

### Step 6: Group by Risk Level

---

### Step 6: Group by Risk Level

**Goal**: Reduce confirmation fatigue through smart grouping.

**Separate Groups for Learning and Corrections**:

**Learning Proposals** (Additive - Lower Risk):
- Can batch minor updates
- New content requires review
- Modifications need diff preview

**Correction Issues** (Corrective - Higher Risk):
- **HIGH confidence**: Must review individually
- **MEDIUM confidence**: Review recommended
- **LOW confidence**: Optional (can skip all)

**Risk Definitions**:
- **Learning - Minor**: Spelling fixes, formatting, small additions to examples
- **Learning - New**: New patterns, API documentation, field type rules
- **Learning - Modification**: Changes to existing content, template changes
- **Correction - HIGH**: Strong evidence contradicts documentation
- **Correction - MEDIUM**: Single evidence source or partial verification
- **Correction - LOW**: Pattern match only, may be false positive

---

### Step 7: User Confirmation & Application

**Goal**: Apply selected changes with user approval.

**Two Workflows**:

#### 1. Learning Proposals (Additive)
- Can batch apply minor updates
- New content: review individually
- Modifications: show diff preview

#### 2. Correction Issues (Corrective)
- **ALWAYS require individual review** (no batch apply)
- Show full evidence before proposing fix
- Show diff preview before final confirmation
- Options: [Review] [Propose Fix] [Skip] [Mark False Positive]

**For each correction issue**:
1. User clicks [Review]
2. Show full evidence:
   - Document claim
   - Dialogue evidence (code + statements)
   - Proposed correction
3. User selects [Propose Fix] or [Skip]
4. If [Propose Fix]:
   - Generate exact Edit operation
   - Show diff preview
   - Ask "Apply this correction? (y/n)"
5. If yes: Apply with Edit tool, log to `log.yaml`
6. If [Skip]: Log as "skipped"
7. If [Mark False Positive]: Log as "false-positive"

---

### Step 8: Update Learning Log

**Goal**: Maintain traceability of all learnings AND corrections.

```yaml
# _shared/learn/log.yaml
learnings:
  - id: "L001"
    hash: "sha256:abc123"
    extracted_at: "2025-02-26T10:00:00Z"
    confidence: "high"
    sources:
      - conversation: "Session about Product module"
    type: "pattern"
    target: "v14/rules/pattern/pattern-redis-lock.md"
    tags: ["pattern", "admin", "concurrent"]
    versions: ["v13", "v14"]
    status: "applied"

corrections:
  - id: "C001"
    type: "api-mismatch" | "parameter-necessity" | "version-confusion" | "outdated-content"
    confidence: "high" | "medium" | "low"
    target_file: "v14/rules/api-controllers.md"
    target_line: 45

    evidence:
      dialogue_code: "$table->setDataSource()"
      dialogue_statement: "文档说是 setDataList"
      codebase_verification: "optional - only if Level 3 or 4 used"

    proposed_correction: |
      Replace setDataList() with setDataSource()

    status: "applied" | "skipped" | "false-positive"
    reviewed_at: "2025-02-26T10:00:00Z"
```

---

## Quick Reference

### Trigger
User invokes: `/qscmf-learn`

### Prerequisites
- Working in a QSCMF project directory
- Conversation contains QSCMF-related work

### Output
- Structured proposals grouped by risk
- User selects which to apply
- Changes written to skill files
- Log updated with traceability

### Key Principles
1. **Version-first**: Detect version before analysis
2. **Non-intrusive**: Post-hoc analysis, no inline annotations
3. **Always confirm**: No auto-apply, even for "safe" items
4. **Idempotent**: Content hash prevents duplicates
5. **Traceable**: All learnings and corrections logged with metadata
6. **Progressive verification**: Level 1-2 by default, Level 3-4 opt-in
7. **Evidence-based**: Corrections require dialogue evidence, never guess

### Correction vs Addition

| Aspect | Addition (Learning) | Correction (Issues Found) |
|--------|---------------------|---------------------------|
| **Risk Level** | Low-Medium | High |
| **Evidence Required** | New discovery | Contradiction evidence |
| **Default Action** | Batch minor items | Individual review only |
| **Confirmation** | Required | Required with evidence review |
| **Operation** | Write (new) or Edit (append) | Edit (replace) |

### Confidence Scoring Reference

**HIGH Confidence (>= 80 points)**:
- Code block evidence in dialogue: +40
- User statement evidence: +30
- Codebase verification: +30
- Evidence agreement: +20
- Version match: +10

**MEDIUM Confidence (50-79 points)**:
- Single evidence type OR partial verification
- Requires user review but likely correct

**LOW Confidence (< 50 points)**:
- Pattern match only, no direct evidence
- Optional to review, may be false positive

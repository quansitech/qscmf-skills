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

**Goal**: Present learnings in a structured, actionable format.

**Proposal Format**:

```markdown
## [N]. [Risk Level]: [Learning Type] - [Brief Title]

**Target File**: `{path}`

**Summary**: {One-line description}

**Confidence**: high | medium | low

**Source**: {conversation context}

**Content Hash**: `{sha256}`

**Content to Add**:
```php
{code example}
```

**Existing Content**: {Note if file exists and what's there}

**Status**: pending | update-required | new
```

---

### Step 6: Group by Risk Level

**Goal**: Reduce confirmation fatigue through smart grouping.

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

**Risk Definitions**:
- **Minor**: Spelling fixes, formatting, small additions to examples
- **New**: New patterns, API documentation, field type rules
- **Modification**: Changes to existing content, template changes

---

### Step 7: User Confirmation & Application

**Goal**: Apply selected changes with user approval.

**For each selected proposal**:
1. Show exact content to be added/modified
2. Show target file path
3. Ask "Apply this change? (y/n)"
4. If yes:
   - Use Edit tool for existing files
   - Use Write tool for new files
5. Log to `log.yaml`

---

### Step 8: Update Learning Log

**Goal**: Maintain traceability of all learnings.

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
5. **Traceable**: All learnings logged with metadata

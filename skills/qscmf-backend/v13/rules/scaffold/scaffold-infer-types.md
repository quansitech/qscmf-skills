---
title: Scaffold Infer Types (v13)
impact: HIGH
impactDescription: Required for accurate code generation
tags: scaffold, infer, types, v13
---

## Scaffold Infer Types (v13)

Three-layer strategy for inferring form field types from database schema.

### When to Use This Rule

- Generating code without @metadata
- Inferring types from field names
- Understanding inference priority

---

## Three-Layer Strategy

```
┌─────────────────────────────────────┐
│  Layer 1: Configuration (Highest)   │
│  .claude/qscmf/field-rules.yaml     │
└─────────────────┬───────────────────┘
                  │ Not matched
                  ▼
┌─────────────────────────────────────┐
│  Layer 2: Learning                  │
│  .claude/qscmf/learned-field-types.json │
└─────────────────┬───────────────────┘
                  │ Not matched
                  ▼
┌─────────────────────────────────────┐
│  Layer 3: Default Patterns          │
│  Field name suffix matching         │
└─────────────────────────────────────┘
```

---

## Layer 1: Configuration

Create `.claude/qscmf/field-rules.yaml`:

```yaml
# Project-specific field rules
product_content:
  type: ueditor
  title: 产品内容

cover_id:
  type: picture
  crop: "866/490"
  title: 封面图

status:
  type: select
  options: DBCont::getStatusList()
  title: 状态

user_id:
  type: select
  options: D('User')->getFieldOptions()
  title: 用户
```

---

## Layer 2: Learning

Scan existing controllers to learn patterns:

```json
// .claude/qscmf/learned-field-types.json
{
  "product_name": {
    "inferred_type": "text",
    "confidence": "high",
    "sources": ["ProductController"]
  },
  "category_id": {
    "inferred_type": "select",
    "confidence": "high",
    "foreign_key": true
  },
  "article_content": {
    "inferred_type": "ueditor",
    "confidence": "high"
  }
}
```

---

## Layer 3: Default Patterns

### Field Name Suffix Patterns

| Pattern | Type | Priority |
|---------|------|----------|
| `*_content` | ueditor | 90 |
| `*_desc` | textarea | 80 |
| `*_date` | date | 95 |
| `*_time` | datetime | 95 |
| `status` | select | 100 |
| `*_status` | select | 85 |
| `is_*` | radio | 85 |
| `*_id` | select | 90 |
| `cover` | picture | 90 |
| `*_image` | picture | 85 |
| `file_id` | file | 90 |
| `sort` | num | 90 |
| `*_price` | num | 90 |
| `email` | text | 95 |
| `phone` | text | 90 |

### Database Type Fallback

| Laravel Type | Default Type |
|-------------|--------------|
| `string` | text |
| `text` | textarea |
| `integer` | num |
| `decimal` | num |
| `date` | date |
| `datetime` | datetime |
| `boolean` | radio |

---

## Implementation

```php
class FieldTypeInferrer
{
    public function infer(string $fieldName, string $dbType, array $metadata = []): array
    {
        // Check metadata first
        if (!empty($metadata['type'])) {
            return ['type' => $metadata['type'], 'source' => 'metadata'];
        }

        // Check suffix patterns
        $patterns = [
            '/^status$/' => 'select',
            '/_content$/' => 'ueditor',
            '/_date$/' => 'date',
            '/_time$/' => 'datetime',
            '/_id$/' => 'select',
            '/^cover$/' => 'picture',
            '/^sort$/' => 'num',
        ];

        foreach ($patterns as $pattern => $type) {
            if (preg_match($pattern, $fieldName)) {
                return ['type' => $type, 'source' => 'pattern'];
            }
        }

        // Fallback to database type
        $fallbacks = [
            'string' => 'text',
            'text' => 'textarea',
            'integer' => 'num',
            'date' => 'date',
            'datetime' => 'datetime',
        ];

        return ['type' => $fallbacks[$dbType] ?? 'text', 'source' => 'fallback'];
    }
}
```

---

## Related Rules

- [Field Type Inference](../field-type-inference.md) - Complete inference guide
- [Scaffold Parse Metadata](scaffold-parse-metadata.md) - Metadata parsing
- [Scaffold Generate Code](scaffold-generate-code.md) - Code generation

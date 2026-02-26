---
title: Scaffold Infer Types (v14)
impact: HIGH
impactDescription: Required for accurate code generation
tags: scaffold, infer, types, v14
---

## Scaffold Infer Types (v14)

Three-layer strategy for inferring form field types from database schema for AntdAdmin Component API.

### When to Use This Rule

- Generating code without @metadata
- Inferring types from field names
- Understanding inference priority

---

## Three-Layer Strategy

```
+-------------------------------------+
|  Layer 1: Configuration (Highest)   |
|  .claude/qscmf/field-rules.yaml     |
+-----------------+-------------------+
                  | Not matched
                  v
+-------------------------------------+
|  Layer 2: Learning                  |
|  .claude/qscmf/learned-field-types.json |
+-----------------+-------------------+
                  | Not matched
                  v
+-------------------------------------+
|  Layer 3: Default Patterns          |
|  Field name suffix matching         |
+-------------------------------------+
```

---

## Layer 1: Configuration

Create `.claude/qscmf/field-rules.yaml`:

```yaml
# Project-specific field rules
product_content:
  type: ueditor
  title: Product Content

cover_id:
  type: picture
  crop: "866/490"
  title: Cover Image

status:
  type: select
  options: DBCont::getStatusList()
  title: Status
  badge:
    1: success
    0: default

user_id:
  type: select
  options: D('User')->getFieldOptions()
  title: User

price:
  type: money
  title: Price
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
| `*_price` | money | 90 |
| `email` | text | 95 |
| `phone` | text | 90 |

### Database Type Fallback

| Laravel Type | Default Type |
|-------------|--------------|
| `string` | text |
| `text` | textarea |
| `integer` | num |
| `decimal` | money |
| `date` | date |
| `datetime` | datetime |
| `boolean` | radio |

---

## v14 Type to AntdAdmin Component Mapping

### Table Column Types

| Inferred Type | v14 Table Code |
|--------------|----------------|
| text | `$container->text('field', 'Title')` |
| textarea | `$container->text('field', 'Title')` |
| select | `$container->select('field', 'Title')->setValueEnum($options)` |
| radio | `$container->select('field', 'Title')->setValueEnum($options)` |
| date | `$container->date('field', 'Title')` |
| datetime | `$container->datetime('field', 'Title')` |
| picture | `$container->image('field', 'Title')` |
| num | `$container->number('field', 'Title')` |
| money | `$container->money('field', 'Title')` |
| ueditor | (not shown in table) |

### Form Column Types

| Inferred Type | v14 Form Code |
|--------------|---------------|
| text | `$columns->text('field', 'Title')` |
| textarea | `$columns->textarea('field', 'Title')` |
| ueditor | `$columns->ueditor('field', 'Title')` |
| select | `$columns->select('field', 'Title')->setValueEnum($options)` |
| radio | `$columns->radio('field', 'Title')->setValueEnum($options)` |
| date | `$columns->date('field', 'Title')` |
| datetime | `$columns->datetime('field', 'Title')` |
| picture | `$columns->image('field', 'Title')` |
| pictures | `$columns->images('field', 'Title')` |
| num | `$columns->number('field', 'Title')` |
| money | `$columns->money('field', 'Title')` |
| file | `$columns->file('field', 'Title')` |

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
            '/_image$/' => 'picture',
            '/_price$/' => 'money',
            '/^sort$/' => 'num',
            '/^is_/' => 'radio',
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
            'decimal' => 'money',
            'date' => 'date',
            'datetime' => 'datetime',
        ];

        return ['type' => $fallbacks[$dbType] ?? 'text', 'source' => 'fallback'];
    }
}
```

---

## v14-Specific Inference Rules

### Status Fields with Badge

```php
// Field: status
// Inferred: select with badge colors
$container->select('status', 'Status')
    ->setValueEnum(DBCont::getStatusList())
    ->setBadge([1 => 'success', 0 => 'default']);
```

### Foreign Keys

```php
// Field: category_id
// Inferred: select with relation options
$container->select('category_id', 'Category')
    ->setValueEnum(D('Category')->getField('id,name'))
    ->setSearch(true);

// Form
$columns->select('category_id', 'Category')
    ->setValueEnum(D('Category')->getField('id,name'))
    ->addRule(new Required());
```

### Sort Fields

```php
// Field: sort
// Inferred: number with inline edit
$container->number('sort', 'Sort')
    ->editable()
    ->setSearch(false);
```

### Money Fields

```php
// Field: product_price
// Inferred: money type
$container->money('product_price', 'Price');

// Form
$columns->money('product_price', 'Price');
```

### Content Fields

```php
// Field: article_content
// Inferred: ueditor (not shown in table)
// Table: skip this field
// Form:
$columns->ueditor('article_content', 'Content')
    ->setFormItemWidth(24);
```

---

## Complete Inference Example

```php
// Database schema
$table->string('product_name', 200);
$table->integer('cate_id');
$table->decimal('price', 10, 2);
$table->string('cover_id', 50);
$table->text('content');
$table->integer('sort');
$table->tinyInteger('status');

// Inferred v14 Table columns
$container->text('product_name', 'Product Name')->setSearch(true);
$container->select('cate_id', 'Category')->setValueEnum(D('Cate')->getField('id,name'));
$container->money('price', 'Price');
$container->image('cover_id', 'Cover');
// content: not shown in table
$container->number('sort', 'Sort')->editable();
$container->select('status', 'Status')
    ->setValueEnum(DBCont::getStatusList())
    ->setBadge([1 => 'success', 0 => 'default']);

// Inferred v14 Form columns
$columns->text('product_name', 'Product Name')
    ->addRule(new Required())
    ->setFormItemWidth(24);
$columns->select('cate_id', 'Category')
    ->setValueEnum(D('Cate')->getField('id,name'))
    ->addRule(new Required())
    ->setFormItemWidth(24);
$columns->money('price', 'Price')->setFormItemWidth(12);
$columns->image('cover_id', 'Cover')
    ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
    ->setFormItemWidth(24);
$columns->ueditor('content', 'Content')->setFormItemWidth(24);
$columns->number('sort', 'Sort')->setFormItemWidth(12);
$columns->select('status', 'Status')
    ->setValueEnum(DBCont::getStatusList())
    ->setFormItemWidth(12);
```

---

## Related Rules

- [Field Type Inference](../field-type-inference.md) - Complete inference guide
- [Scaffold Parse Metadata](scaffold-parse-metadata.md) - Metadata parsing
- [Scaffold Generate Code](scaffold-generate-code.md) - Code generation

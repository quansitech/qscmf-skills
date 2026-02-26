---
title: Field Type Inference (v13)
impact: HIGH
impactDescription: Improves scaffold accuracy by 80%
tags: scaffold, type-inference, v13
---

## Field Type Inference (v13)

Use three-layer strategy to infer form field types from database schema.

### When to Use This Rule

- Generating CRUD code from migration
- Inferring field types when @metadata is missing
- Understanding type inference priority

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
│  Patterns from existing code        │
└─────────────────┬───────────────────┘
                  │ Not matched
                  ▼
┌─────────────────────────────────────┐
│  Layer 3: Default Patterns          │
│  Field name suffix matching         │
│  Database type fallback             │
└─────────────────────────────────────┘
```

---

## Layer 1: Configuration

Create `.claude/qscmf/field-rules.yaml` for project-specific rules:

```yaml
# Field type rules
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

Scan existing controllers to learn patterns. Results saved to `.claude/qscmf/learned-field-types.json`:

```json
{
  "product_name": {
    "inferred_type": "text",
    "confidence": "high",
    "sources": ["ProductController", "CategoryController"]
  },
  "category_id": {
    "inferred_type": "select",
    "confidence": "high",
    "foreign_key": true,
    "foreign_table": "category"
  },
  "article_content": {
    "inferred_type": "ueditor",
    "confidence": "high",
    "sources": ["ArticleController"]
  }
}
```

---

## Layer 3: Default Patterns

### Field Name Suffix Patterns

| Pattern | Type | Priority | Example |
|---------|------|----------|---------|
| `*_content` | ueditor | 90 | article_content |
| `*_desc` | textarea | 80 | product_desc |
| `*_description` | textarea | 80 | category_description |
| `*_remark` | textarea | 80 | order_remark |
| `*_summary` | textarea | 80 | article_summary |
| `*_date` | date | 95 | publish_date |
| `*_time` | datetime | 95 | create_time, update_time |
| `*_at` | datetime | 95 | deleted_at, published_at |
| `status` | select | 100 | status |
| `*_status` | select | 85 | order_status, audit_status |
| `is_*` | radio | 85 | is_active, is_top |
| `has_*` | radio | 85 | has_stock, has_discount |
| `*_id` | select | 90 | category_id, user_id |
| `cate_id` | select | 95 | cate_id |
| `user_id` | select | 95 | user_id |
| `cover` | picture | 90 | cover |
| `cover_id` | picture | 90 | cover_id |
| `thumb` | picture | 90 | thumb |
| `*_image` | picture | 85 | product_image |
| `*_images` | pictures | 85 | product_images |
| `avatar` | picture | 90 | avatar |
| `logo` | picture | 90 | logo |
| `file_id` | file | 90 | file_id |
| `*_file` | file | 80 | attachment_file |
| `*_files` | files | 80 | attachment_files |
| `sort` | num | 90 | sort |
| `*_sort` | num | 85 | display_sort |
| `*_count` | num | 85 | view_count, click_count |
| `*_price` | num | 90 | unit_price, sale_price |
| `*_amount` | num | 90 | total_amount |
| `*_qty` | num | 85 | stock_qty |
| `url` | text | 90 | url |
| `*_url` | text | 85 | site_url |
| `phone` | text | 90 | phone |
| `mobile` | text | 90 | mobile |
| `*_phone` | text | 85 | contact_phone |
| `email` | text | 90 | email |
| `*_email` | text | 85 | contact_email |
| `address` | district | 85 | address |
| `*_address` | district | 80 | shipping_address |

### Database Type Fallback

| Laravel Type | Default Type |
|-------------|--------------|
| `string` | text |
| `char` | text |
| `text` | textarea |
| `longText` | textarea |
| `integer` | num |
| `bigInteger` | num |
| `unsignedBigInteger` | select (foreign key) |
| `tinyInteger` | select (status) |
| `smallInteger` | num |
| `decimal` | num |
| `float` | num |
| `double` | num |
| `date` | date |
| `datetime` | datetime |
| `timestamp` | datetime |
| `time` | time |
| `boolean` | radio |

---

## Migration Metadata Format

Use @metadata in migration comments for explicit type hints:

```php
// Format: @key=value; (semicolon-separated)
$table->string('name', 200)->comment('@title=名称;@type=text;@require=true;');
$table->text('content')->comment('@title=内容;@type=ueditor;');
$table->integer('status')->comment('@title=状态;@type=select;@options=DBCont::getStatusList();');
$table->integer('cate_id')->comment('@title=分类;@type=select;@options=D(\'Cate\')->getFieldOptions();');
$table->string('cover_id')->comment('@title=封面图;@type=picture;@crop=866/490;');
$table->integer('sort')->comment('@title=排序;@type=num;@default=0;');
```

### Metadata Keys

| Key | Description | Example |
|-----|-------------|---------|
| `@title` | Display label | `@title=商品名称` |
| `@type` | Field type | `@type=ueditor` |
| `@require` | Required field | `@require=true` |
| `@options` | Select options | `@options=DBCont::getStatusList()` |
| `@default` | Default value | `@default=0` |
| `@crop` | Image crop ratio | `@crop=866/490` |
| `@length` | Validation length | `@length=1,200` |
| `@placeholder` | Placeholder text | `@placeholder=请输入名称` |
| `@tips` | Help text | `@tips=推荐尺寸16:9` |

---

## Inference Implementation

```php
class FieldTypeInferrer
{
    const FIELD_PATTERNS = [
        ['pattern' => '/^status$/', 'type' => 'select', 'priority' => 100],
        ['pattern' => '/_content$/', 'type' => 'ueditor', 'priority' => 90],
        ['pattern' => '/_desc$/', 'type' => 'textarea', 'priority' => 80],
        ['pattern' => '/_description$/', 'type' => 'textarea', 'priority' => 80],
        ['pattern' => '/_date$/', 'type' => 'date', 'priority' => 95],
        ['pattern' => '/_time$/', 'type' => 'datetime', 'priority' => 95],
        ['pattern' => '/_at$/', 'type' => 'datetime', 'priority' => 95],
        ['pattern' => '/_status$/', 'type' => 'select', 'priority' => 85],
        ['pattern' => '/^is_/', 'type' => 'radio', 'priority' => 85],
        ['pattern' => '/_id$/', 'type' => 'select', 'priority' => 90],
        ['pattern' => '/^cover$/', 'type' => 'picture', 'priority' => 90],
        ['pattern' => '/^cover_id$/', 'type' => 'picture', 'priority' => 90],
        ['pattern' => '/_images$/', 'type' => 'pictures', 'priority' => 85],
        ['pattern' => '/_image$/', 'type' => 'picture', 'priority' => 85],
        ['pattern' => '/^file_id$/', 'type' => 'file', 'priority' => 90],
        ['pattern' => '/^sort$/', 'type' => 'num', 'priority' => 90],
        ['pattern' => '/_price$/', 'type' => 'num', 'priority' => 90],
        ['pattern' => '/_amount$/', 'type' => 'num', 'priority' => 90],
        ['pattern' => '/_count$/', 'type' => 'num', 'priority' => 85],
        ['pattern' => '/^email$/', 'type' => 'text', 'priority' => 95],
        ['pattern' => '/^phone$/', 'type' => 'text', 'priority' => 90],
        ['pattern' => '/^mobile$/', 'type' => 'text', 'priority' => 90],
        ['pattern' => '/_address$/', 'type' => 'district', 'priority' => 80],
    ];

    const DB_TYPE_FALLBACK = [
        'string' => 'text',
        'text' => 'textarea',
        'longText' => 'textarea',
        'integer' => 'num',
        'bigInteger' => 'num',
        'tinyInteger' => 'select',
        'decimal' => 'num',
        'float' => 'num',
        'date' => 'date',
        'datetime' => 'datetime',
        'timestamp' => 'datetime',
        'boolean' => 'radio',
    ];

    public function infer(string $field_name, string $db_type, array $metadata = []): array
    {
        // Check metadata first
        if (!empty($metadata['type'])) {
            return [
                'type' => $metadata['type'],
                'source' => 'metadata',
                'confidence' => 'high'
            ];
        }

        // Check field patterns
        foreach (self::FIELD_PATTERNS as $pattern) {
            if (preg_match($pattern['pattern'], $field_name)) {
                return [
                    'type' => $pattern['type'],
                    'source' => 'pattern',
                    'confidence' => 'medium',
                    'priority' => $pattern['priority']
                ];
            }
        }

        // Fallback to database type
        if (isset(self::DB_TYPE_FALLBACK[$db_type])) {
            return [
                'type' => self::DB_TYPE_FALLBACK[$db_type],
                'source' => 'db_type',
                'confidence' => 'low'
            ];
        }

        // Final fallback
        return [
            'type' => 'text',
            'source' => 'default',
            'confidence' => 'low'
        ];
    }
}
```

---

## Type to Code Mapping

| Inferred Type | ListBuilder Column | FormBuilder Item |
|---------------|--------------------| -----------------|
| `text` | `addTableColumn('name', '标题')` | `addFormItem('name', 'text', '标题')` |
| `textarea` | `addTableColumn('desc', '描述', 'textarea')` | `addFormItem('desc', 'textarea', '描述')` |
| `ueditor` | N/A (detail only) | `addFormItem('content', 'editor', '内容')` |
| `select` | `addTableColumn('status', '状态', $options)` | `addFormItem('status', 'select', '状态', $options)` |
| `radio` | `addTableColumn('is_top', '置顶', 'checkbox')` | `addFormItem('is_top', 'radio', '置顶', $options)` |
| `date` | `addTableColumn('date', '日期', 'date_format', 'Y-m-d')` | `addFormItem('date', 'date', '日期')` |
| `datetime` | `addTableColumn('time', '时间', 'time')` | `addFormItem('time', 'datetime', '时间')` |
| `picture` | `addTableColumn('cover', '封面', 'picture')` | `addFormItem('cover', 'picture', '封面')` |
| `pictures` | `addTableColumn('images', '图片', 'pictures')` | `addFormItem('images', 'pictures', '图片')` |
| `file` | N/A (detail only) | `addFormItem('file', 'file', '附件')` |
| `num` | `addTableColumn('sort', '排序', 'num')` | `addFormItem('sort', 'num', '排序')` |
| `district` | N/A (detail only) | `addFormItem('address', 'district', '地址')` |

---

## Related Rules

- [Scaffold Generate Code](scaffold/scaffold-generate-code.md) - Code generation workflow
- [Scaffold Parse Metadata](scaffold/scaffold-parse-metadata.md) - Migration metadata parsing
- [ListBuilder API](listbuilder-api.md) - ListBuilder methods
- [FormBuilder API](formbuilder-api.md) - FormBuilder methods

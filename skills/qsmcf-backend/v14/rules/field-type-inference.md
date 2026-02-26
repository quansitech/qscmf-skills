# Field Type Inference Strategy

Three-layer strategy for inferring form field types from database schema.

## Inference Layers

```
Layer 1: Configuration (.claude/qscmf/field-rules.yaml)
    ↓ (not found)
Layer 2: Learning (scan existing controllers)
    ↓ (not found)
Layer 3: Default rules (field name suffix patterns)
```

---

## Layer 1: Configuration Override

Create `.claude/qscmf/field-rules.yaml` in your project:

```yaml
# Field-specific overrides
product_content: ueditor
cover_id:
  type: image
  crop: "16/9"
  tips: "推荐尺寸 16:9"
status:
  type: select
  options: DBCont::getStatusList()
  badge:
    1: success
    0: default
cate_id:
  type: select
  options: D('Category')->getFieldOptions()
price:
  type: number
  min: 0
  step: 0.01
publish_date:
  type: date
  format: Y-m-d
tags:
  type: checkbox
  options:
    tag1: 标签1
    tag2: 标签2
is_featured:
  type: switch
  onText: 是
  offText: 否
```

---

## Layer 2: Learning from Existing Code

Scan existing controllers to learn patterns:

```bash
php scripts/infer_types.php --scan app/Admin/Controller/
```

Results saved to `.claude/qscmf/learned-field-types.json`:

```json
{
  "product_name": "text",
  "product_code": "text",
  "cover_id": "image",
  "status": "select",
  "sort": "number",
  "content": "ueditor"
}
```

---

## Layer 3: Default Suffix Rules

| Pattern | Form Type | Table Type | Notes |
|---------|-----------|------------|-------|
| `*_content` | ueditor | text (truncated) | Rich text content |
| `*_date` | date | date | Date field |
| `*_time` | datetime | datetime | DateTime field |
| `*_id` (FK) | select | select | Foreign key |
| `status` | select | select + badge | Status field |
| `cover` | image | image | Cover image |
| `*_img` | image | image | Image field |
| `*_image` | image | image | Image field |
| `file_id` | file | text | File field |
| `*_file` | file | text | File field |
| `sort` | number | number (editable) | Sort order |
| `*_sort` | number | number (editable) | Sort field |
| `*_url` | text | link | URL field |
| `*_email` | text | text | Email field |
| `*_phone` | text | text | Phone field |
| `*_mobile` | text | text | Mobile field |
| `is_*` | checkbox | select | Boolean flag |
| `has_*` | checkbox | select | Boolean flag |
| `*_count` | number | number | Count field |
| `*_amount` | number | number | Amount field |
| `*_price` | money | money | Price field |
| `*_rate` | number | number | Rate field |
| `create_time` | - | datetime | Created at |
| `update_time` | - | datetime | Updated at |
| `delete_time` | - | - | Soft delete |
| `description` | textarea | text (truncated) | Description |
| `summary` | textarea | text (truncated) | Summary |
| `remark` | textarea | text | Remark |
| `note` | textarea | text | Note |

---

## Schema Metadata Parsing

Migration comments can include type hints:

```php
// In migration file
$table->string('cover_id')->comment('封面图 @type=image @crop=16/9 @tips=推荐尺寸 16:9');
$table->string('content')->comment('内容 @type=ueditor');
$table->tinyInteger('status')->comment('状态 @type=select @options=DBCont::getStatusList()');
$table->integer('cate_id')->comment('分类 @type=select @options=D("Category")->getFieldOptions()');
```

### Supported Metadata

| Metadata | Description | Example |
|----------|-------------|---------|
| `@type` | Field type | `@type=image` |
| `@title` | Field label | `@title=产品名称` |
| `@crop` | Image crop ratio | `@crop=16/9` |
| `@tips` | Field tips | `@tips=推荐尺寸 16:9` |
| `@options` | Options source | `@options=DBCont::getStatusList()` |
| `@badge` | Badge colors | `@badge=1:success,0:default` |
| `@editable` | Inline editable | `@editable=true` |
| `@search` | Searchable | `@search=true` |
| `@required` | Required field | `@required=true` |
| `@hidden` | Hidden in table | `@hidden=true` |

---

## Inference Examples

### Example 1: Product Table

```sql
CREATE TABLE `product` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_name` varchar(200) NOT NULL COMMENT '商品名称',
  `product_code` varchar(50) NOT NULL COMMENT '商品编码',
  `cate_id` int(11) NOT NULL COMMENT '分类ID',
  `price` decimal(10,2) NOT NULL COMMENT '价格',
  `stock` int(11) DEFAULT '0' COMMENT '库存',
  `cover_id` int(11) DEFAULT NULL COMMENT '封面图 @type=image',
  `content` text COMMENT '详情内容 @type=ueditor',
  `status` tinyint(1) DEFAULT '1' COMMENT '状态',
  `sort` int(11) DEFAULT '99' COMMENT '排序',
  `create_time` int(11) DEFAULT NULL COMMENT '创建时间',
  `update_time` int(11) DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
);
```

**Inferred Form Fields:**

| Field | Form Type | Table Type |
|-------|-----------|------------|
| product_name | text | text |
| product_code | text | text |
| cate_id | select | select |
| price | money | money |
| stock | number | number |
| cover_id | image | image |
| content | ueditor | text |
| status | select | select + badge |
| sort | number | number (editable) |

### Example 2: Article Table

```sql
CREATE TABLE `article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL COMMENT '标题',
  `author` varchar(50) DEFAULT NULL COMMENT '作者',
  `cate_id` int(11) DEFAULT NULL COMMENT '分类',
  `cover` varchar(255) DEFAULT NULL COMMENT '封面',
  `summary` text COMMENT '摘要',
  `article_content` text COMMENT '内容',
  `publish_date` date DEFAULT NULL COMMENT '发布日期',
  `view_count` int(11) DEFAULT '0' COMMENT '浏览量',
  `is_top` tinyint(1) DEFAULT '0' COMMENT '是否置顶',
  `status` tinyint(1) DEFAULT '1' COMMENT '状态',
  `create_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
);
```

**Inferred Form Fields:**

| Field | Form Type | Table Type |
|-------|-----------|------------|
| title | text | text |
| author | text | text |
| cate_id | select | select |
| cover | image | image |
| summary | textarea | text (truncated) |
| article_content | ueditor | text |
| publish_date | date | date |
| view_count | number | number |
| is_top | checkbox | select |
| status | select | select + badge |

---

## Related Documentation

- [Scaffold Generate Code](scaffold/scaffold-generate-code.md) - Code generation
- [Scaffold Parse Metadata](scaffold/scaffold-parse-metadata.md) - Metadata parsing
- [ListBuilder API](listbuilder-api.md) - List building API
- [FormBuilder API](formbuilder-api.md) - Form building API

---
title: Scaffold Parse Metadata (v13)
impact: HIGH
impactDescription: Required for code generation from migrations
tags: scaffold, parse, metadata, v13
---

## Scaffold Parse Metadata (v13)

Parse @metadata from migration file comments for code generation.

### When to Use This Rule

- Reading field metadata from migrations
- Extracting type hints for code generation
- Understanding metadata format

---

## Metadata Format

```php
$table->string('name', 200)->comment('@title=名称;@type=text;@require=true;');
$table->integer('status')->comment('@title=状态;@type=select;@options=DBCont::getStatusList();');
$table->string('cover_id', 50)->comment('@title=封面图;@type=picture;@crop=866/490;');
```

Format: `@key=value;` (semicolon-separated)

---

## Metadata Keys

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
| `@save` | Inline editable | `@save=true` |
| `@search` | Searchable | `@search=true` |

---

## Parsing Implementation

```php
function parseMetadata(string $comment): array
{
    $metadata = [];

    // Remove surrounding comment markers
    $comment = trim($comment);

    // Split by semicolon
    $parts = explode(';', $comment);

    foreach ($parts as $part) {
        $part = trim($part);
        if (empty($part)) continue;

        // Split key=value
        if (strpos($part, '=') !== false) {
            list($key, $value) = explode('=', $part, 2);
            $key = trim($key);
            $value = trim($value);

            // Remove @ prefix
            if (strpos($key, '@') === 0) {
                $key = substr($key, 1);
            }

            $metadata[$key] = $value;
        }
    }

    return $metadata;
}
```

---

## Usage Example

```php
// Migration
$table->string('product_name', 200)->comment('@title=商品名称;@type=text;@require=true;@length=1,200;');

// Parsed result
$metadata = [
    'title' => '商品名称',
    'type' => 'text',
    'require' => 'true',
    'length' => '1,200'
];

// Generated code
$builder->addFormItem('product_name', 'text', '商品名称', '请输入商品名称', true);

// Validation rule
$_validate[] = ['product_name', 'require', '商品名称不能为空', self::MUST_VALIDATE];
$_validate[] = ['product_name', '1,200', '商品名称长度不正确', self::VALUE_VALIDATE, 'length'];
```

---

## Complete Field Example

```php
// Migration
$table->integer('cate_id')->comment('@title=分类;@type=select;@options=D(\'Cate\')->getFieldOptions();@require=true;');

// Generated ListBuilder code
$builder->addTableColumn('cate_id', '分类', D('Cate')->getFieldOptions());

// Generated FormBuilder code
$builder->addFormItem('cate_id', 'select', '分类', D('Cate')->getFieldOptions(), true);

// Generated validation
$_validate[] = ['cate_id', 'require', '分类不能为空', self::MUST_VALIDATE];
```

---

## Related Rules

- [Scaffold Generate Code](scaffold-generate-code.md) - Code generation workflow
- [Scaffold Infer Types](scaffold-infer-types.md) - Type inference
- [Field Type Inference](../field-type-inference.md) - Complete inference strategy

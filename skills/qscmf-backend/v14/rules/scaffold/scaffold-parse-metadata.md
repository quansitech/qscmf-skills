---
title: Scaffold Parse Metadata (v14)
impact: HIGH
impactDescription: Required for code generation from migrations
tags: scaffold, parse, metadata, v14
---

## Scaffold Parse Metadata (v14)

Parse @metadata from migration file comments for code generation.

### When to Use This Rule

- Reading field metadata from migrations
- Extracting type hints for code generation
- Understanding metadata format

---

## Metadata Format

```php
$table->string('name', 200)->comment('@title=Name;@type=text;@require=true;');
$table->integer('status')->comment('@title=Status;@type=select;@options=DBCont::getStatusList();');
$table->string('cover_id', 50)->comment('@title=Cover Image;@type=picture;@crop=866/490;');
```

Format: `@key=value;` (semicolon-separated)

---

## Metadata Keys

| Key | Description | Example |
|-----|-------------|---------|
| `@title` | Display label | `@title=Product Name` |
| `@type` | Field type | `@type=ueditor` |
| `@require` | Required field | `@require=true` |
| `@options` | Select options | `@options=DBCont::getStatusList()` |
| `@default` | Default value | `@default=0` |
| `@crop` | Image crop ratio | `@crop=866/490` |
| `@length` | Validation length | `@length=1,200` |
| `@placeholder` | Placeholder text | `@placeholder=Enter name` |
| `@tips` | Help text | `@tips=Recommended size 16:9` |
| `@save` | Inline editable | `@save=true` |
| `@search` | Searchable | `@search=true` |
| `@badge` | Badge colors | `@badge=1:success,0:default` |
| `@width` | Form width | `@width=24` |

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

## Usage Example (v14)

```php
// Migration
$table->string('product_name', 200)->comment('@title=Product Name;@type=text;@require=true;@length=1,200;');

// Parsed result
$metadata = [
    'title' => 'Product Name',
    'type' => 'text',
    'require' => 'true',
    'length' => '1,200'
];

// Generated v14 Form code
$columns->text('product_name', 'Product Name')
    ->addRule(new Required())
    ->addRule(new Length(1, 200))
    ->setFormItemWidth(24);

// Generated v14 Table code
$container->text('product_name', 'Product Name')
    ->setSearch(true);

// Validation rule (Model)
$_validate[] = ['product_name', 'require', 'Product Name is required', self::MUST_VALIDATE];
$_validate[] = ['product_name', '1,200', 'Product Name length invalid', self::VALUE_VALIDATE, 'length'];
```

---

## Complete Field Example (v14)

```php
// Migration
$table->integer('cate_id')->comment('@title=Category;@type=select;@options=D(\'Cate\')->getFieldOptions();@require=true;');

// Generated v14 Table code
$container->select('cate_id', 'Category')
    ->setValueEnum(D('Cate')->getField('id,name'))
    ->setSearch(true);

// Generated v14 Form code
$columns->select('cate_id', 'Category')
    ->setValueEnum(D('Cate')->getField('id,name'))
    ->addRule(new Required())
    ->setFormItemWidth(24);

// Generated validation (Model)
$_validate[] = ['cate_id', 'require', 'Category is required', self::MUST_VALIDATE];
```

---

## v14-Specific Metadata Keys

### @search - Enable Column Search

```php
// Migration
$table->string('name', 200)->comment('@title=Name;@type=text;@search=true;');

// Generated v14 code
$container->text('name', 'Name')
    ->setSearch(true);
```

### @save - Enable Inline Edit

```php
// Migration
$table->integer('sort')->comment('@title=Sort;@type=num;@save=true;');

// Generated v14 code
$container->number('sort', 'Sort')
    ->editable();
```

### @badge - Status Badge Colors

```php
// Migration
$table->tinyInteger('status')->comment('@title=Status;@type=select;@options=DBCont::getStatusList();@badge=1:success,0:default;');

// Generated v14 code
$container->select('status', 'Status')
    ->setValueEnum(DBCont::getStatusList())
    ->setBadge([1 => 'success', 0 => 'default']);
```

### @width - Form Column Width

```php
// Migration
$table->integer('sort')->comment('@title=Sort;@type=num;@width=12;');
$table->tinyInteger('status')->comment('@title=Status;@type=select;@options=DBCont::getStatusList();@width=12;');

// Generated v14 code (two fields side by side)
$columns->number('sort', 'Sort')
    ->setFormItemWidth(12);

$columns->select('status', 'Status')
    ->setValueEnum(DBCont::getStatusList())
    ->setFormItemWidth(12);
```

### @crop - Image Crop Ratio

```php
// Migration
$table->string('cover_id', 50)->comment('@title=Cover;@type=picture;@crop=16/9;');

// Generated v14 code
$columns->image('cover_id', 'Cover')
    ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
    ->setCrop('16/9')
    ->setFormItemWidth(24);
```

---

## Metadata to v14 Code Mapping

| Metadata | Table Column | Form Column |
|----------|-------------|-------------|
| `@type=text` | `$container->text()` | `$columns->text()` |
| `@type=textarea` | `$container->text()` | `$columns->textarea()` |
| `@type=ueditor` | (not shown) | `$columns->ueditor()` |
| `@type=select` | `$container->select()->setValueEnum()` | `$columns->select()->setValueEnum()` |
| `@type=radio` | `$container->select()->setValueEnum()` | `$columns->radio()->setValueEnum()` |
| `@type=date` | `$container->date()` | `$columns->date()` |
| `@type=datetime` | `$container->datetime()` | `$columns->datetime()` |
| `@type=picture` | `$container->image()` | `$columns->image()` |
| `@type=pictures` | `$container->image()` | `$columns->images()` |
| `@type=num` | `$container->number()` | `$columns->number()` |
| `@type=money` | `$container->money()` | `$columns->money()` |
| `@type=file` | (not shown) | `$columns->file()` |
| `@search=true` | `->setSearch(true)` | N/A |
| `@save=true` | `->editable()` | N/A |
| `@require=true` | N/A | `->addRule(new Required())` |
| `@width=N` | N/A | `->setFormItemWidth(N)` |

---

## Related Rules

- [Scaffold Generate Code](scaffold-generate-code.md) - Code generation workflow
- [Scaffold Infer Types](scaffold-infer-types.md) - Type inference
- [Field Type Inference](../field-type-inference.md) - Complete inference strategy

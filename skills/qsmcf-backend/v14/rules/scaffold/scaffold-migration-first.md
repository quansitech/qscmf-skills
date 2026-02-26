---
title: Scaffold Migration First (v14)
impact: HIGH
impactDescription: Best practice for new modules
tags: scaffold, migration, first, v14
---

## Scaffold Migration First (v14)

Create migration with @metadata before generating code.

### When to Use This Rule

- Starting a new module
- Following best practices
- Ensuring accurate code generation

---

## Why Migration First?

1. **Single source of truth** - Schema defines everything
2. **Accurate code generation** - Metadata drives templates
3. **Database version control** - Track schema changes
4. **Documentation** - Comments describe fields

---

## Create Migration

```bash
cd /path/to/qscmf/project
php artisan make:migration create_product_table
```

---

## Add Fields with Metadata

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateProductTable extends Migration
{
    public function up()
    {
        Schema::create('product', function (Blueprint $table) {
            $table->id();

            // Basic fields with metadata
            $table->string('product_name', 200)
                ->comment('@title=Product Name;@type=text;@require=true;@length=1,200;@search=true;');

            $table->string('product_code', 50)
                ->comment('@title=Product Code;@type=text;');

            // Foreign key with options
            $table->integer('cate_id')->default(0)
                ->comment('@title=Category;@type=select;@options=D(\'Cate\')->getFieldOptions();@search=true;');

            // Image fields
            $table->string('cover_id', 50)->default('')
                ->comment('@title=Cover Image;@type=picture;@crop=16/9;');

            $table->text('images')->nullable()
                ->comment('@title=Gallery;@type=pictures;');

            // Numeric fields
            $table->decimal('price', 10, 2)->default(0)
                ->comment('@title=Price;@type=money;');

            $table->integer('stock')->default(0)
                ->comment('@title=Stock;@type=num;');

            // Text fields
            $table->text('summary')->nullable()
                ->comment('@title=Summary;@type=textarea;');

            $table->text('content')->nullable()
                ->comment('@title=Content;@type=ueditor;');

            // Common fields with v14-specific metadata
            $table->integer('sort')->default(0)
                ->comment('@title=Sort;@type=num;@save=true;@width=12;');

            $table->tinyInteger('status')->default(1)
                ->comment('@title=Status;@type=select;@options=DBCont::getStatusList();@badge=1:success,0:default;@width=12;');

            $table->integer('create_time')->default(0);
            $table->integer('update_time')->default(0);

            // Indexes
            $table->index('cate_id');
            $table->index('status');
        });
    }

    public function down()
    {
        Schema::dropIfExists('product');
    }
}
```

---

## Run Migration

```bash
php artisan migrate
```

---

## Generate Code

After migration is created, generate code using the scaffold workflow:

1. Parse migration metadata
2. Infer field types
3. Generate Model, Controller, API, Test
4. Write files
5. Output TODO list

---

## v14 Metadata Best Practices

### Always Include

- `@title` - Display label (required)
- `@type` - Field type (required for special types)

### Include When Applicable

- `@require=true` - Required fields
- `@options=...` - Select options
- `@length=min,max` - Validation length
- `@crop=W/H` - Image crop ratio
- `@save=true` - Inline editable

### v14-Specific Metadata

- `@search=true` - Enable column search
- `@badge=1:success,0:default` - Status badge colors
- `@width=N` - Form column width (24=full, 12=half)

### Example

```php
// Good - Complete metadata with v14 features
$table->string('product_name', 200)
    ->comment('@title=Product Name;@type=text;@require=true;@length=1,200;@search=true;');

$table->tinyInteger('status')->default(1)
    ->comment('@title=Status;@type=select;@options=DBCont::getStatusList();@badge=1:success,0:default;@width=12;');

// Bad - Missing metadata
$table->string('product_name', 200)->comment('Product Name');
```

---

## v14 Generated Code Examples

### From Migration Metadata

```php
// Migration
$table->string('product_name', 200)
    ->comment('@title=Product Name;@type=text;@require=true;@length=1,200;@search=true;');

// Generated v14 Table Column
$container->text('product_name', 'Product Name')
    ->setSearch(true);

// Generated v14 Form Column
$columns->text('product_name', 'Product Name')
    ->addRule(new Required())
    ->addRule(new Length(1, 200))
    ->setFormItemWidth(24);
```

### Status Field with Badge

```php
// Migration
$table->tinyInteger('status')->default(1)
    ->comment('@title=Status;@type=select;@options=DBCont::getStatusList();@badge=1:success,0:default;@width=12;');

// Generated v14 Table Column
$container->select('status', 'Status')
    ->setValueEnum(DBCont::getStatusList())
    ->setBadge([1 => 'success', 0 => 'default'])
    ->setSearch(true);

// Generated v14 Form Column
$columns->select('status', 'Status')
    ->setValueEnum(DBCont::getStatusList())
    ->setFormItemWidth(12);
```

### Sort with Inline Edit

```php
// Migration
$table->integer('sort')->default(0)
    ->comment('@title=Sort;@type=num;@save=true;@width=12;');

// Generated v14 Table Column
$container->number('sort', 'Sort')
    ->editable()
    ->setSearch(false);

// Generated v14 Form Column
$columns->number('sort', 'Sort')
    ->setFormItemWidth(12);
```

### Image with Crop

```php
// Migration
$table->string('cover_id', 50)->default('')
    ->comment('@title=Cover Image;@type=picture;@crop=16/9;');

// Generated v14 Table Column
$container->image('cover_id', 'Cover Image');

// Generated v14 Form Column
$columns->image('cover_id', 'Cover Image')
    ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
    ->setCrop('16/9')
    ->setFormItemWidth(24);
```

---

## Complete Migration Template (v14)

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class Create{Module}Table extends Migration
{
    public function up()
    {
        Schema::create('{table}', function (Blueprint $table) {
            $table->id();

            // ========== FIELDS WITH METADATA ==========

            // Basic text field
            $table->string('{table}_name', 200)
                ->comment('@title=Name;@type=text;@require=true;@search=true;');

            // Select field with options
            $table->integer('cate_id')->default(0)
                ->comment('@title=Category;@type=select;@options=D(\'Category\')->getFieldOptions();');

            // Image with crop
            $table->string('cover_id', 50)->default('')
                ->comment('@title=Cover;@type=picture;@crop=16/9;');

            // Rich text editor
            $table->text('content')->nullable()
                ->comment('@title=Content;@type=ueditor;');

            // Money field
            $table->decimal('price', 10, 2)->default(0)
                ->comment('@title=Price;@type=money;');

            // Sort with inline edit
            $table->integer('sort')->default(0)
                ->comment('@title=Sort;@type=num;@save=true;@width=12;');

            // Status with badge
            $table->tinyInteger('status')->default(1)
                ->comment('@title=Status;@type=select;@options=DBCont::getStatusList();@badge=1:success,0:default;@width=12;');

            // Timestamps
            $table->integer('create_time')->default(0);
            $table->integer('update_time')->default(0);

            // Indexes
            $table->index('status');
        });
    }

    public function down()
    {
        Schema::dropIfExists('{table}');
    }
}
```

---

## Related Rules

- [Scaffold Generate Code](scaffold-generate-code.md) - Code generation
- [Scaffold Parse Metadata](scaffold-parse-metadata.md) - Metadata parsing
- [Workflow Create Module](../workflow/workflow-create-module.md) - Complete workflow
- [Migration Guide](../../references/migration-guide.md) - Migration reference

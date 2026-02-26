---
title: Scaffold Migration First (v13)
impact: HIGH
impactDescription: Best practice for new modules
tags: scaffold, migration, first, v13
---

## Scaffold Migration First (v13)

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
                ->comment('@title=商品名称;@type=text;@require=true;@length=1,200;');

            $table->string('product_code', 50)
                ->comment('@title=商品编码;@type=text;');

            // Foreign key with options
            $table->integer('cate_id')->default(0)
                ->comment('@title=分类;@type=select;@options=D(\'Cate\')->getFieldOptions();');

            // Image fields
            $table->string('cover_id', 50)->default('')
                ->comment('@title=封面图;@type=picture;@crop=866/490;');

            $table->text('images')->nullable()
                ->comment('@title=图片集;@type=pictures;');

            // Numeric fields
            $table->decimal('price', 10, 2)->default(0)
                ->comment('@title=价格;@type=num;');

            $table->integer('stock')->default(0)
                ->comment('@title=库存;@type=num;');

            // Text fields
            $table->text('summary')->nullable()
                ->comment('@title=摘要;@type=textarea;');

            $table->text('content')->nullable()
                ->comment('@title=详情;@type=ueditor;');

            // Common fields
            $table->integer('sort')->default(0)
                ->comment('@title=排序;@type=num;@save=true;');

            $table->tinyInteger('status')->default(1)
                ->comment('@title=状态;@type=select;@options=DBCont::getStatusList();');

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

## Metadata Best Practices

### Always Include

- `@title` - Display label (required)
- `@type` - Field type (required for special types)

### Include When Applicable

- `@require=true` - Required fields
- `@options=...` - Select options
- `@length=min,max` - Validation length
- `@crop=W/H` - Image crop ratio
- `@save=true` - Inline editable

### Example

```php
// Good - Complete metadata
$table->string('product_name', 200)
    ->comment('@title=商品名称;@type=text;@require=true;@length=1,200;');

// Bad - Missing metadata
$table->string('product_name', 200)->comment('商品名称');
```

---

## Related Rules

- [Scaffold Generate Code](scaffold-generate-code.md) - Code generation
- [Scaffold Parse Metadata](scaffold-parse-metadata.md) - Metadata parsing
- [Workflow Create Module](../workflow/workflow-create-module.md) - Complete workflow
- [Migration Guide](../../references/migration-guide.md) - Migration reference

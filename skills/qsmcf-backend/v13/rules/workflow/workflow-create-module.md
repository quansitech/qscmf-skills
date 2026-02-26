---
title: Create Module Workflow (v13)
impact: HIGH
impactDescription: Standard workflow for creating new modules
tags: workflow, scaffold, v13
---

## Create Module Workflow (v13)

Step-by-step workflow for creating a new QSCMF v13 module.

### When to Use This Rule

- Creating a new module from scratch
- Understanding the complete module creation process
- Following best practices for module setup

---

## Workflow Steps

### Step 1: Create Migration

```bash
cd /path/to/qscmf/project
php artisan make:migration create_{table_name}_table
```

Edit migration file with @metadata:

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
            $table->string('product_name', 200)->comment('@title=商品名称;@type=text;@require=true;');
            $table->string('product_code', 50)->comment('@title=商品编码;@type=text;');
            $table->integer('cate_id')->default(0)->comment('@title=分类;@type=select;@options=D(\'Cate\')->getFieldOptions();');
            $table->string('cover_id', 50)->default('')->comment('@title=封面图;@type=picture;');
            $table->text('images')->nullable()->comment('@title=图片集;@type=pictures;');
            $table->decimal('price', 10, 2)->default(0)->comment('@title=价格;@type=num;');
            $table->integer('stock')->default(0)->comment('@title=库存;@type=num;');
            $table->text('summary')->nullable()->comment('@title=摘要;@type=textarea;');
            $table->text('content')->nullable()->comment('@title=详情;@type=ueditor;');
            $table->integer('sort')->default(0)->comment('@title=排序;@type=num;');
            $table->tinyInteger('status')->default(1)->comment('@title=状态;@type=select;@options=DBCont::getStatusList();');
            $table->integer('create_time')->default(0);
            $table->integer('update_time')->default(0);

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

### Step 2: Run Migration

```bash
php artisan migrate
```

### Step 3: Create Model

File: `app/Common/Model/ProductModel.class.php`

Use template: `v13/templates/model.php.tpl`

Key points:
- Extend `GyListModel`
- Define `$_validate` for validation
- Define `$_auto` for auto-fill
- Add business methods

### Step 4: Create Admin Controller

File: `app/Admin/Controller/ProductController.class.php`

Use template: `v13/templates/admin_controller.php.tpl`

Key methods:
- `index()` - List page
- `add()` - Add form
- `edit()` - Edit form
- `save()` - Save handler
- `delete()` - Delete handler

### Step 5: Create API Controller (Optional)

File: `app/Api/Controller/ProductController.class.php`

Use template: `v13/templates/api_controller.php.tpl`

### Step 6: Create Tests (Optional)

File: `lara/tests/Feature/ProductTest.php`

Use template: `v13/templates/test_case.php.tpl`

### Step 7: Configure Permissions

Add menu and permissions in admin panel:

```sql
-- Add menu
INSERT INTO qs_node (name, title, pid, level, url, status, sort)
VALUES ('Product', '商品管理', 0, 1, 'Admin/Product', 1, 100);

-- Get the parent ID
SET @pid = LAST_INSERT_ID();

-- Add child menus
INSERT INTO qs_node (name, title, pid, level, url, status, sort) VALUES
('index', '列表', @pid, 2, 'Admin/Product/index', 1, 0),
('add', '新增', @pid, 2, 'Admin/Product/add', 1, 0),
('edit', '编辑', @pid, 2, 'Admin/Product/edit', 1, 0),
('delete', '删除', @pid, 2, 'Admin/Product/delete', 1, 0);
```

### Step 8: Test

```bash
# Run tests
vendor/bin/phpunit lara/tests/Feature/ProductTest.php

# Or test manually in browser
# Visit: /admin/Product/index
```

---

## Complete Example Command Sequence

```bash
# 1. Create migration
php artisan make:migration create_product_table

# 2. Edit migration (add fields with @metadata)

# 3. Run migration
php artisan migrate

# 4. Create files (manually or via scaffold)
# - app/Common/Model/ProductModel.class.php
# - app/Admin/Controller/ProductController.class.php
# - app/Api/Controller/ProductController.class.php (optional)
# - lara/tests/Feature/ProductTest.php (optional)

# 5. Configure permissions in admin panel

# 6. Test
vendor/bin/phpunit lara/tests/Feature/ProductTest.php
```

---

## Checklist

- [ ] Migration created with @metadata
- [ ] Migration executed
- [ ] Model created
- [ ] Admin controller created
- [ ] API controller created (if needed)
- [ ] Tests created (if needed)
- [ ] Permissions configured
- [ ] Manual testing completed
- [ ] Automated tests passed

---

## Related Rules

- [Add CRUD Workflow](workflow-add-crud.md) - Adding CRUD to existing module
- [Scaffold Generate Code](../scaffold/scaffold-generate-code.md) - Code generation
- [Migration First](../scaffold/scaffold-migration-first.md) - Migration best practices

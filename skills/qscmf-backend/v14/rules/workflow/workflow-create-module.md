---
title: Create Module Workflow (v14)
impact: HIGH
impactDescription: Standard workflow for creating new modules with AntdAdmin
tags: workflow, scaffold, v14, antdadmin
---

## Create Module Workflow (v14)

Step-by-step workflow for creating a new QSCMF v14 module with AntdAdmin components.

### When to Use This Rule

- Creating a new module from scratch
- Understanding the complete module creation process
- Following best practices for v14 module setup with React/AntdAdmin rendering

---

## Workflow Steps

### Step 1: Create Migration

```bash
cd /path/to/qscmf/project
php artisan make:migration create_{table_name}_table
```

Edit migration file with @metadata for code generation hints:

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
            $table->integer('cate_id')->default(0)->comment('@title=分类;@type=select;@options=D(\'Category\')->getField(\'id,name\');');
            $table->string('cover_id', 50)->default('')->comment('@title=封面图;@type=image;@crop=16/9;');
            $table->text('images')->nullable()->comment('@title=图片集;@type=images;');
            $table->decimal('price', 10, 2)->default(0)->comment('@title=价格;@type=number;');
            $table->integer('stock')->default(0)->comment('@title=库存;@type=number;');
            $table->text('summary')->nullable()->comment('@title=摘要;@type=textarea;');
            $table->text('content')->nullable()->comment('@title=详情;@type=ueditor;');
            $table->integer('sort')->default(99)->comment('@title=排序;@type=number;');
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

Use template: `v14/templates/model.php.tpl`

Key points:
- Extend `GyListModel`
- Define `$_validate` for validation
- Define `$_auto` for auto-fill
- Use PHP 8.2 type declarations
- Add business methods

```php
<?php
namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;

class ProductModel extends GyListModel
{
    protected $tableName = 'product';

    protected $_validate = [
        ['product_name', 'require', '商品名称不能为空', self::MUST_VALIDATE],
        ['product_code', 'checkUnique', '商品编码已存在', self::VALUE_VALIDATE, 'callback'],
    ];

    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT, 'function'],
        ['update_time', 'time', self::MODEL_BOTH, 'function'],
    ];

    public function getActiveProducts(): array
    {
        return $this->where(['status' => DBCont::NORMAL_STATUS])
            ->order('sort asc, id desc')
            ->select();
    }

    protected function checkUnique(string $value, int $excludeId = 0): bool
    {
        $map = ['product_code' => $value];
        if ($excludeId > 0) {
            $map['id'] = ['NEQ', $excludeId];
        }
        return !$this->where($map)->count();
    }
}
```

### Step 4: Create Admin Controller (v14 AntdAdmin)

File: `app/Admin/Controller/ProductController.class.php`

Use template: `v14/templates/admin_controller.php.tpl`

v14 uses AntdAdmin Component API with React rendering:

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;
use Gy_Library\DBCont;
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;
use AntdAdmin\Component\Form;
use AntdAdmin\Component\Modal\Modal;
use AntdAdmin\Component\ColumnType\RuleType\Required;

class ProductController extends QsListController
{
    protected $modelName = 'Product';
    protected $formWidth = '800px';

    public function index()
    {
        $map = [];
        $this->buildSearchWhere(I('get.'), $map);

        $model = D('Product')->where($map);
        $count = $model->count();
        $page = new \Gy_Library\GyPage($count);

        $data_list = $model->page($page->nowPage, $page->listRows)
            ->order('id desc')
            ->select();

        $table = new Table();
        $table->setMetaTitle('商品列表')
            ->actions(function (Table\ActionsContainer $container) {
                $container->button('新增')
                    ->setProps(['type' => 'primary'])
                    ->modal((new Modal())
                        ->setWidth($this->formWidth)
                        ->setUrl(U('add'))
                        ->setTitle('新增商品'));
                $container->forbid();
                $container->resume();
                $container->delete();
            })
            ->columns(function (Table\ColumnsContainer $container) {
                $this->buildTableColumns($container);
            })
            ->setDataSource($data_list)
            ->setPagination(new Pagination($page->nowPage, $page->listRows, $count))
            ->render();
    }

    protected function buildTableColumns(Table\ColumnsContainer $container): void
    {
        $container->text('product_name', '商品名称')->setSearch(true);
        $container->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList())
            ->setBadge([1 => 'success', 0 => 'default'])
            ->setSearch(true);
        $container->number('sort', '排序')->editable();
        $container->datetime('create_time', '创建时间');

        $container->action('', '操作')
            ->actions(function (Table\ColumnType\ActionsContainer $container) {
                $container->edit()->modal(
                    (new Modal())
                        ->setWidth($this->formWidth)
                        ->setUrl(U('edit', ['id' => '__id__']))
                        ->setTitle('编辑')
                );
                $container->forbid();
                $container->resume();
                $container->delete();
            });
    }

    protected function buildSearchWhere(array $get_data, array &$map): void
    {
        if (!empty($get_data['product_name'])) {
            $map['product_name'] = ['like', '%' . $get_data['product_name'] . '%'];
        }

        if (isset($get_data['status']) && $get_data['status'] !== '') {
            $map['status'] = $get_data['status'];
        }
    }
}
```

### Step 5: Create API Controller (Optional)

File: `app/Api/Controller/ProductController.class.php`

Use template: `v14/templates/api_controller.php.tpl`

### Step 6: Create Tests (Optional)

File: `lara/tests/Feature/ProductTest.php`

Use template: `v14/templates/test_case.php.tpl`

v14 uses PHPUnit 10:

```php
<?php
namespace Tests\Feature;

use Tests\TestCase;
use Gy_Library\DBCont;

class ProductTest extends TestCase
{
    public function test_index_returns_products(): void
    {
        $response = $this->get('/api/product');

        $response->assertStatus(200)
            ->assertJsonStructure([
                'status',
                'data' => [
                    '*' => ['id', 'product_name', 'status']
                ],
                'meta' => ['total', 'page', 'page_size']
            ]);
    }
}
```

### Step 7: Configure Permissions

Add menu and permissions in admin panel:

```sql
-- Add menu
INSERT INTO admin_menu (name, title, pid, level, url, status, sort)
VALUES ('Product', '商品管理', 0, 1, 'Admin/Product', 1, 100);

-- Get the parent ID
SET @pid = LAST_INSERT_ID();

-- Add child menus
INSERT INTO admin_menu (name, title, pid, level, url, status, sort) VALUES
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

## v14-Specific Considerations

### Rendering Mode

v14 uses `ANTD_ADMIN_BUILDER_ENABLE` to control rendering:
- `ANTD_ADMIN_BUILDER_ENABLE = true` (default) → React/AntdAdmin rendering
- `ANTD_ADMIN_BUILDER_ENABLE = false` → jQuery rendering (backward compatible)

### Direct Component vs ListBuilder

v14 offers two approaches:

**Option 1: Direct AntdAdmin Components (Recommended for new projects)**

```php
$table = new Table();
$table->columns(function (Table\ColumnsContainer $container) {
    $container->text('name', '名称');
});
```

**Option 2: ListBuilder API (Backward compatible)**

```php
$builder = $this->builder();
$builder->addTableColumn('name', '名称');
```

### Inertia.js Integration

For SPA-like navigation in v14:

```php
use Qscmf\Lib\Inertia\HasLayoutProps;

class ProductController extends QsListController
{
    use HasLayoutProps;

    public function detail()
    {
        $data = D('Product')->find(I('get.id'));

        if ($this->isInertiaRequest()) {
            return Inertia::render('Product/Detail', [
                'product' => $data,
            ]);
        }

        $this->assign('data', $data);
        $this->display();
    }

    protected function isInertiaRequest(): bool
    {
        return !empty($_SERVER['HTTP_X_INERTIA']);
    }
}
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
- [ ] Model created with PHP 8.2 type declarations
- [ ] Admin controller created with AntdAdmin components
- [ ] API controller created (if needed)
- [ ] Tests created with PHPUnit 10 (if needed)
- [ ] Permissions configured
- [ ] Manual testing completed
- [ ] Automated tests passed

---

## Related Rules

- [Add CRUD Workflow](workflow-add-crud.md) - Adding CRUD to existing module
- [Scaffold Generate Code](../scaffold/scaffold-generate-code.md) - Code generation
- [Migration First](../scaffold/scaffold-migration-first.md) - Migration best practices
- [AntdAdmin Components](../antdadmin.md) - Direct component usage
- [Inertia.js Integration](../inertia.md) - SPA navigation

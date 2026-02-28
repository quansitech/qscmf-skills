---
name: qscmf-backend-v14
description: |
  QSCMF v14 backend development (PHP 8.2+, PHPUnit 10, AntdAdmin, Inertia.js).
  Auto-loaded when v14 is detected.

  Scaffold Mode Triggers: "创建", "生成", "scaffold", "模块", "CRUD", "API"
  Guide Mode: Default for QSCMF development questions
---

# QSCMF v14 Backend Development

## Overview

QSCMF v14 is the modern version of the framework featuring:
- **PHP 8.2+** with strict typing
- **PHPUnit 10** for testing
- **AntdAdmin** React components
- **Inertia.js** for SPA-like navigation
- **ListBuilder API** (same as v13, with React rendering)

### Rendering Mode

v14 uses `ANTD_ADMIN_BUILDER_ENABLE` to control rendering:
- `ANTD_ADMIN_BUILDER_ENABLE = true` (default) → React/AntdAdmin rendering
- `ANTD_ADMIN_BUILDER_ENABLE = false` → jQuery rendering (backward compatible)

---

## Mode Selection

### Scaffold Mode (Code Generation)

**Triggers**: "创建", "生成", "scaffold", "模块", "CRUD", "API"

Examples:
- "创建 Product 模块，需要后台 CRUD 和 API"
- "生成 User API"
- "QSCMF scaffold Order"

### Guide Mode (Development Assistance)

Default mode for QSCMF development questions.

Examples:
- "如何实现 QsListController 的 CRUD?"
- "AntdAdmin Table 组件如何使用?"
- "如何编写 PHPUnit 测试?"

---

## Scaffold Workflow (6 Steps)

### Step 1: Identify Requirements

Extract module name and required components from user request.

| Request Pattern | Module | Components |
|----------------|--------|------------|
| "创建 Product 模块，需要后台 CRUD 和 API" | Product | AdminController, ApiController, Model, Migration |
| "生成 User API" | User | ApiController only |
| "QSCMF scaffold Order" | Order | All components |

### Step 2: Parse Table Schema

Read schema from:
1. Migration files (`lara/database/migrations/`)
2. Existing database table
3. User-provided field list

Look for metadata comments:
```php
$table->string('cover_id')->comment('封面图 @type=image @crop=16/9');
```

### Step 3: Infer Field Types

Apply three-layer inference strategy:

```
Layer 1: Configuration (.claude/qscmf/field-rules.yaml)
    ↓ (not found)
Layer 2: Learning (scan existing controllers)
    ↓ (not found)
Layer 3: Default rules (field name suffix patterns)
```

**Default Rules**:

| Pattern | Form Type | Table Type |
|---------|-----------|------------|
| `*_content` | ueditor | text (truncated) |
| `*_date` | date | date |
| `*_time` | datetime | datetime |
| `*_id` (FK) | select | select |
| `status` | select | select (with badge) |
| `cover`, `*_img`, `*_image` | image | image |
| `file_id`, `*_file` | file | text |
| `sort`, `*_sort` | number | number (editable) |
| `is_*` | checkbox | select |
| `*_url` | text | link |

### Step 4: Generate Code

Use templates with inferred field types:

| Component | Template | Output Path |
|-----------|----------|-------------|
| AdminController | `admin_controller.php.tpl` | `app/Admin/Controller/{Name}Controller.class.php` |
| Model | `model.php.tpl` | `app/Common/Model/{Name}Model.class.php` |
| ApiController | `api_controller.php.tpl` | `app/Api/Controller/{Name}Controller.class.php` |
| Migration | `migration.php.tpl` | `lara/database/migrations/xxxx_create_{table}_table.php` |
| Test | `test_case.php.tpl` | `lara/tests/Feature/{Name}Test.php` |

### Step 5: Write Files

Create files in proper directories. Skip if file exists (unless `--force`).

### Step 6: Output TODO List

```markdown
## TODO List

### Required
- [ ] Run migration: `php artisan migrate`
- [ ] Configure permissions in admin_menu table
- [ ] Review and adjust field types in AdminController
- [ ] Add validation rules to Model::$_validate

### Recommended
- [ ] Write tests: `vendor/bin/phpunit lara/tests/Feature/{Name}Test.php`
- [ ] Configure cache if needed
- [ ] Add business logic to save() method

### References
- [ListBuilder API](rules/listbuilder-api.md)
- [FormBuilder API](rules/formbuilder-api.md)
- [Field Type Inference](rules/field-type-inference.md)
```

---

## Framework Guide

### Admin CRUD (QsListController)

QSCMF v14 uses the same ListBuilder API as v13, with React rendering.

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;

class ProductController extends QsListController
{
    protected $modelName = 'Product';

    public function index()
    {
        $map = $this->buildSearchMap(I('get.'));
        $model = D('Product')->where($map);
        $total = $model->count();

        $builder = $this->builder();
        $this->buildTableColumns($builder);
        $this->buildSearchForm($builder);
        $this->buildButtons($builder);

        $list = $model->order('id desc')->select();
        $builder->setData($list);
        $builder->display();
    }

    protected function buildTableColumns($builder)
    {
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('product_name', '商品名称');
        $builder->addTableColumn('status', '状态', DBCont::getStatusList());
        $builder->addTableColumn('create_time', '创建时间', 'time');
    }

    protected function buildSearchForm($builder)
    {
        $builder->addSearchItem('keyword', 'text', '关键词');
        $builder->addSearchItem('status', 'select', '状态', DBCont::getStatusList());
    }

    protected function buildButtons($builder)
    {
        $builder->addTopButton('addnew', ['title' => '新增', 'href' => U('add')]);
        $builder->addRightButton('edit', ['href' => U('edit', ['id' => '@id@'])]);
        $builder->addRightButton('delete');
    }
}
```

### RESTful API (RestController)

```php
<?php
namespace Api\Controller;

use Api\Controller\RestController;

class ProductController extends RestController
{
    protected $modelName = 'Product';

    public function index_get()
    {
        $page = I('get.page', 1, 'intval');
        $pageSize = I('get.page_size', 20, 'intval');

        $map = ['status' => DBCont::NORMAL_STATUS];
        $list = D('Product')->where($map)
            ->page($page, $pageSize)
            ->select();

        $total = D('Product')->where($map)->count();

        $this->response([
            'status' => true,
            'data' => $list,
            'meta' => [
                'total' => $total,
                'page' => $page,
                'page_size' => $pageSize
            ]
        ]);
    }
}
```

### Model (GyListModel)

```php
<?php
namespace Common\Model;

use Gy_Library\GyListModel;

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
}
```

---

## v14-Specific Features

### Inertia.js Integration

v14 supports Inertia.js for SPA-like navigation.

#### HasLayoutProps Trait

```php
use Qscmf\Lib\Inertia\HasLayoutProps;

class DashboardController extends QsListController
{
    use HasLayoutProps;

    public function index()
    {
        $this->shareLayoutProps([
            'title' => 'Dashboard',
            'breadcrumbs' => [
                ['title' => 'Home', 'href' => '/'],
                ['title' => 'Dashboard'],
            ],
        ]);

        // ... rest of controller
    }
}
```

#### X-Inertia Header Detection

```php
public function detail()
{
    $data = D('Product')->find(I('get.id'));

    if ($this->isInertiaRequest()) {
        // Return Inertia props for SPA navigation
        return Inertia::render('Product/Detail', [
            'product' => $data,
        ]);
    }

    // Traditional page render
    $this->assign('data', $data);
    $this->display();
}

protected function isInertiaRequest(): bool
{
    return !empty($_SERVER['HTTP_X_INERTIA']);
}
```

### Direct AntdAdmin Component Usage

For advanced scenarios beyond ListBuilder, use direct AntdAdmin components.

#### Table Component

```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;
use AntdAdmin\Component\Modal\Modal;

public function index()
{
    $model = D('Product');
    $count = $model->count();
    $page = new \Gy_Library\GyPage($count);

    $data_list = $model->page($page->nowPage, $page->listRows)->select();

    $table = new Table();
    $table->setMetaTitle('商品列表')
        ->actions(function (Table\ActionsContainer $container) {
            $container->button('新增')
                ->setProps(['type' => 'primary'])
                ->modal((new Modal())
                    ->setWidth('800px')
                    ->setUrl(U('add'))
                    ->setTitle('新增商品'));
            $container->forbid();
            $container->resume();
            $container->delete();
        })
        ->columns(function (Table\ColumnsContainer $container) {
            $container->text('product_name', '商品名称');
            $container->select('status', '状态')
                ->setValueEnum(DBCont::getStatusList())
                ->setBadge([1 => 'success', 0 => 'default']);
            $container->number('sort', '排序')
                ->editable();
            $container->action('', '操作')
                ->actions(function (Table\ColumnType\ActionsContainer $container) {
                    $container->edit()->modal(
                        (new Modal())
                            ->setWidth('800px')
                            ->setUrl(U('edit', ['id' => '__id__']))
                            ->setTitle('编辑')
                    );
                    $container->delete();
                });
        })
        ->setDataSource($data_list)
        ->setPagination(new Pagination($page->nowPage, $page->listRows, $count))
        ->render();
}
```

#### Form Component

```php
use AntdAdmin\Component\Form;
use AntdAdmin\Component\ColumnType\RuleType\Required;

public function add()
{
    if (IS_POST) {
        $data = I('post.');
        $result = D('Product')->createAdd($data);
        if ($result === false) {
            $this->error(D('Product')->getError());
        }
        $this->success('添加成功');
    }

    $form = new Form();
    $form->setSubmitRequest('post', U('add'))
        ->setInitialValues(['status' => 1])
        ->columns(function (Form\ColumnsContainer $columns) {
            $columns->text('product_name', '商品名称')
                ->addRule(new Required())
                ->setFormItemWidth(24);

            $columns->select('cate_id', '分类')
                ->setValueEnum(D('Category')->getField('id,name'))
                ->addRule(new Required())
                ->setFormItemWidth(24);

            $columns->image('cover_id', '封面图')
                ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
                ->setCrop('16/9')
                ->setFormItemWidth(24);

            $columns->number('sort', '排序')
                ->setFormItemWidth(12);

            $columns->select('status', '状态')
                ->setValueEnum(DBCont::getStatusList())
                ->setFormItemWidth(12);
        })
        ->actions(function (Form\ActionsContainer $actions) {
            $actions->button('提交')->submit();
            $actions->button('重置')->reset();
        });

    return $form->render();
}
```

### ListAdapter Pattern

The ListAdapter converts ListBuilder calls to AntdAdmin components internally.

```
User Code (ListBuilder API)
         ↓
    ListBuilder
         ↓
    ListAdapter (converts to AntdAdmin format)
         ↓
    AntdAdmin\Component\Table
         ↓
    React Rendering
```

For custom rendering, extend the adapter:

```php
use Qscmf\Builder\ListAdapter;

class CustomListAdapter extends ListAdapter
{
    protected function convertColumn($name, $title, $type, $value)
    {
        // Custom column conversion logic
        return parent::convertColumn($name, $title, $type, $value);
    }
}
```

---

## Testing

### PHPUnit 10

v14 uses PHPUnit 10 with improved assertions.

```php
<?php
// lara/tests/Feature/ProductTest.php

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

    public function test_create_product_success(): void
    {
        $data = [
            'product_name' => 'Test Product',
            'product_code' => 'TEST001',
            'status' => DBCont::NORMAL_STATUS,
        ];

        $response = $this->post('/api/product', $data);

        $response->assertStatus(201)
            ->assertJson(['status' => true]);

        $this->assertDatabaseHas('product', [
            'product_name' => 'Test Product',
        ]);
    }
}
```

### Wall Class Pattern for Mocking

```php
public function test_external_api_with_mock(): void
{
    // Create Wall mock
    $wallMock = $this->createMock(ProductWall::class);
    $wallMock->method('getInfo')
        ->willReturn(['id' => 1, 'name' => 'Mock Product']);

    app()->instance(ProductWall::class, $wallMock);

    $response = $this->get('/api/product/external/1');

    $response->assertJson(['name' => 'Mock Product']);
}
```

---

## Common Code Patterns

### Abstract Base Class Pattern

For multiple similar modules:

```php
<?php
// Common/Model/CategoryModel.class.php
abstract class CategoryModel extends GyListModel
{
    protected abstract function getTableName(): string;
    protected abstract function getModuleTitle(): string;

    public function getTree(): array
    {
        return $this->where(['status' => DBCont::NORMAL_STATUS])
            ->order('sort asc')
            ->select();
    }
}

// Common/Model/ProductCateModel.class.php
class ProductCateModel extends CategoryModel
{
    protected function getTableName(): string { return 'product_cate'; }
    protected function getModuleTitle(): string { return '商品分类'; }
}
```

### Redis Lock for Concurrency

```php
use Qscmf\Lib\Redis\RedisLock;

public function batchProcess()
{
    $lock = new RedisLock('batch_process_' . $this->uid);

    if (!$lock->acquire()) {
        $this->error('操作进行中，请稍候');
    }

    try {
        // Process batch
        $result = $this->doBatchProcess();
        $lock->release();
        return $result;
    } catch (\Exception $e) {
        $lock->release();
        throw $e;
    }
}
```

### Queue Job Pattern

```php
// Create job
use Qscmf\Lib\Queue\QueueJob;

class ExportJob extends QueueJob
{
    public function handle(): void
    {
        $data = $this->getData();
        // Process export...
    }
}

// Dispatch job
QueueJob::dispatch(ExportJob::class, [
    'module' => 'Product',
    'filters' => $filters,
]);
```

---

## File Paths Reference

| Component | Path |
|-----------|------|
| AdminController | `app/Admin/Controller/{Name}Controller.class.php` |
| ApiController | `app/Api/Controller/{Name}Controller.class.php` |
| Model | `app/Common/Model/{Name}Model.class.php` |
| Migration | `lara/database/migrations/xxxx_create_{table}_table.php` |
| Test | `lara/tests/Feature/{Name}Test.php` |
| Config | `app/Common/Conf/config.php` |

---

## Rules Index

### Core API
- [ListBuilder API](rules/listbuilder-api.md) - Complete ListBuilder method reference
- [FormBuilder API](rules/formbuilder-api.md) - Complete FormBuilder method reference
- [Field Type Inference](rules/field-type-inference.md) - Three-layer inference strategy

### v14 Specific
- [Inertia.js Integration](rules/inertia.md) - SPA navigation with Inertia
- [AntdAdmin Components](rules/antdadmin.md) - Direct component usage

### Workflow
- [Create Module](rules/workflow/workflow-create-module.md) - Module creation workflow
- [Add CRUD](rules/workflow/workflow-add-crud.md) - CRUD implementation workflow

### CRUD
- [Table Columns](rules/crud/crud-table-columns.md) - Column configuration and custom renderers
- [Search](rules/crud/crud-search-basic.md) - Search form configuration
- [Form Validation](rules/crud/crud-form-validation.md) - Form validation rules
- [Batch Actions](rules/crud/crud-batch-actions.md) - Batch operations

### API
- [Response Format](rules/api/api-response-format.md) - Standard JSON response
- [Pagination](rules/api/api-pagination-cursor.md) - Cursor/offset pagination
- [JWT Auth](rules/api/api-auth-jwt.md) - JWT authentication

### Testing
- [TDD First](rules/test/test-tdd-first.md) - Test-driven development
- [Wall Mock](rules/test/test-wall-mock.md) - External API mocking
- [Transaction](rules/test/test-transaction.md) - Database transactions

### Patterns
- [Abstract Base](rules/pattern/pattern-abstract-base.md) - Reusable base classes
- [Redis Lock](rules/pattern/pattern-redis-lock.md) - Concurrency control
- [Queue Job](rules/pattern/pattern-queue-job.md) - Async job processing
- [Wall Class](rules/pattern/pattern-wall-class.md) - External API wrapper

### Scaffold
- [Generate Code](rules/scaffold/scaffold-generate-code.md) - Code generation rules
- [Parse Metadata](rules/scaffold/scaffold-parse-metadata.md) - Migration metadata
- [Infer Types](rules/scaffold/scaffold-infer-types.md) - Type inference
- [Migration First](rules/scaffold/scaffold-migration-first.md) - Database-first approach

---

## References Index

- [Admin Controllers](references/admin-controllers.md) - Complete admin controller guide
- [API Controllers](references/api-controllers.md) - RESTful API development
- [Model Guide](references/model-guide.md) - GyListModel patterns
- [Migration Guide](references/migration-guide.md) - Laravel migrations
- [Migration Metadata](references/migration-metadata.md) - Code generation hints
- [CRUD Patterns](references/crud-patterns.md) - Development patterns
- [Where Query Reference](references/where-query-reference.md) - Query syntax
- [Development Standards](references/development-standards.md) - PHP 8.2 standards
- [Testing](references/testing.md) - PHPUnit patterns
- [Abstract Base Patterns](references/abstract-base-patterns.md) - Reusable patterns
- [Inertia Integration](references/inertia-integration.md) - v14 Inertia.js guide

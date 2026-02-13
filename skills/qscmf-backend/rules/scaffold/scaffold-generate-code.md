---
title: Code Generation from Migration
impact: CRITICAL
impactDescription: Required; 100% of scaffold operations depend on this
tags: scaffold, code-generation, both
---

## Code Generation from Migration

**Impact: CRITICAL (Required for all scaffold operations)**

Generate Model, Controller, API, and Test code from migration metadata.

### When to Use This Rule

- You need to generate CRUD code for a table with @metadata
- You need to understand the code generation workflow
- You want to ensure consistent code generation patterns

---

## Prerequisites

Before generating code, ensure:

1. **Migration exists** with @metadata annotations
2. **Version detected** (v13 or v14)
3. **Config loaded** from `_shared/config/v{X}.yaml`

```bash
# Check migration exists
ls lara/database/migrations/*create_{table_name}*

# Verify @metadata
grep '@title' lara/database/migrations/*create_{table_name}*
```

---

## Generation Workflow

### Step 1: Parse Migration Metadata

Read the migration file and extract @metadata from each column:

```php
// Example migration comment
$table->string('name', 200)->comment('@title=产品名称;@type=text;@length=1,200;@require=true;');
```

See: [scaffold-parse-metadata.md](scaffold-parse-metadata.md)

### Step 2: Infer Field Types

Use three-layer inference strategy:

1. **Config Layer**: Load from `_shared/config/v{X}.yaml`
2. **Pattern Layer**: Match field name patterns
3. **Default Layer**: Fallback based on column type

See: [scaffold-infer-types.md](scaffold-infer-types.md)

### Step 3: Generate Model

**Location**: `app/Common/Model/{Name}Model.class.php`

**Template**: `_shared/templates/{version}/model.php.tpl`

**Generated Code Structure**:
```php
<?php
namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;

class ProductModel extends GyListModel
{
    protected $_validate = [
        // Validation rules from @require, @length
        ['name', 'require', '产品名称不能为空'],
        ['name', '1,200', '产品名称长度不正确', 3, 'length'],
    ];

    protected $_auto = [
        // Auto-fill rules
        ['create_time', 'time', 1, 'function'],
        ['update_time', 'time', 3, 'function'],
    ];

    public function getStatusList(): array
    {
        return DBCont::getStatusList();
    }
}
```

### Step 4: Generate Admin Controller

**Location**: `app/Admin/Controller/{Name}Controller.class.php`

**Template**: `_shared/templates/{version}/admin_controller.php.tpl`

#### v14 (AntdAdmin)

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Form;

class ProductController extends QsListController
{
    protected function configureContainer(Table $container): void
    {
        // Table columns
        $container->text('name', '名称')
            ->setSearch(true)
            ->setSearchType('like')
            ->setSortable(true);

        $container->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList())
            ->setBadge([1 => 'success', 0 => 'default'])
            ->setSearch(true);

        $container->date('create_time', '创建时间')
            ->setSearch(true)
            ->setSearchType('between');

        // Actions
        $container->action('', '操作')
            ->actions(function ($actions) {
                $actions->edit();
                $actions->delete();
            });
    }

    protected function configureForm(Form $form): void
    {
        $form->text('name', '名称')
            ->addRule(new Required())
            ->setPlaceholder('请输入名称');

        $form->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList())
            ->setDefaultValue(1);
    }
}
```

#### v13 (ListBuilder)

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;

class ProductController extends QsListController
{
    protected function _initialize()
    {
        parent::_initialize();
        $this->model = D('Product');
    }

    protected function getBuilder()
    {
        $builder = new \Common\Builder\ListBuilder();

        // Table columns
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('name', '名称');
        $builder->addTableColumn('status', '状态', DBCont::getStatusList());
        $builder->addTableColumn('create_time', '创建时间');

        // Search
        $builder->addSearchItem('name', 'text', '名称');
        $builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());

        // Buttons
        $builder->addTopButton('addnew');
        $builder->addRightButton('edit');
        $builder->addRightButton('delete');

        return $builder;
    }
}
```

### Step 5: Generate API Controller

**Location**: `app/Api/Controller/{Name}Controller.class.php`

**Template**: `_shared/templates/{version}/api_controller.php.tpl`

```php
<?php
namespace Api\Controller;

use Api\Controller\RestController;

class ProductController extends RestController
{
    public function gets()
    {
        $page = I('page', 1);
        $pageSize = I('page_size', 20);

        $where = $this->buildWhere();
        $list = D('Product')->where($where)
            ->page($page, $pageSize)
            ->select();

        $total = D('Product')->where($where)->count();

        $this->response([
            'list' => $list,
            'total' => $total,
            'page' => $page,
            'page_size' => $pageSize,
        ]);
    }

    public function add()
    {
        $data = $this->getRequestData();

        if (false === D('Product')->add($data)) {
            $this->responseError('添加失败');
        }

        $this->responseSuccess('添加成功');
    }
}
```

### Step 6: Generate Test

**Location**: `lara/tests/Feature/{Name}Test.php`

**Template**: `_shared/templates/{version}/test_case.php.tpl`

```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;

class ProductTest extends TestCase
{
    public function testGetList(): void
    {
        $response = $this->get('/api.php/Product/gets');

        $response->assertStatus(200)
            ->assertJson(['status' => 1])
            ->assertJsonStructure([
                'data' => ['list', 'total']
            ]);
    }

    public function testCreate(): void
    {
        $response = $this->post('/api.php/Product/add', [
            'name' => 'Test Product',
            'status' => 1,
        ]);

        $response->assertStatus(200)
            ->assertJson(['status' => 1]);
    }
}
```

---

## Field Type to Code Mapping

| @type | v14 Component | v13 Builder Method | Form Item |
|-------|---------------|--------------------|-----------|
| `text` | `$container->text()` | `addTableColumn()` | text |
| `textarea` | `$container->textarea()` | `addTableColumn('textarea')` | textarea |
| `select` | `$container->select()` | `addTableColumn('select')` | select |
| `date` | `$container->date()` | `addTableColumn('date')` | date |
| `datetime` | `$container->datetime()` | `addTableColumn('time')` | datetime |
| `num` | `$container->number()` | `addTableColumn('num')` | num |
| `picture` | `$container->image()` | `addTableColumn('picture')` | picture |
| `pictures` | `$container->images()` | `addTableColumn('pictures')` | pictures |
| `richText` | `$container->rich_text()` | `addFormItem('ueditor')` | ueditor/richtext |
| `status` | `$container->select()` | `addTableColumn('status')` | select |
| `file` | `$container->file()` | `addFormItem('file')` | file |
| `files` | `$container->files()` | `addFormItem('files')` | files |

---

## Generation Checklist

After generation, verify:

### Model
- [ ] Extends `GyListModel`
- [ ] `$_validate` has rules from @require and @length
- [ ] Foreign key relations defined (`$_link`)
- [ ] Status list method exists

### Admin Controller
- [ ] Extends `QsListController`
- [ ] Table columns match migration fields
- [ ] Search items configured
- [ ] Form items configured
- [ ] Actions (edit/delete) added

### API Controller
- [ ] Extends `RestController`
- [ ] CRUD methods (gets/add/edit/delete)
- [ ] Proper response format
- [ ] Validation in add/edit

### Test
- [ ] Extends `TestCase`
- [ ] Tests for each API endpoint
- [ ] Success and failure cases
- [ ] Mock external dependencies

---

## Post-Generation TODO

Output this TODO list after code generation:

```markdown
## Generated Files

- app/Common/Model/ProductModel.class.php
- app/Admin/Controller/ProductController.class.php
- app/Api/Controller/ProductController.class.php
- lara/tests/Feature/ProductTest.php

## Manual Steps Required

1. [ ] Run migration: `php artisan migrate`
2. [ ] Configure permissions in `qs_node` table
3. [ ] Add custom validation rules in Model::$_validate
4. [ ] Implement business logic (save/delete hooks)
5. [ ] Configure menu entry in admin panel
6. [ ] Run tests: `vendor/bin/phpunit lara/tests/Feature/ProductTest.php`
```

---

## See Also

- [Parse Metadata](scaffold-parse-metadata.md) - @metadata parsing logic
- [Infer Types](scaffold-infer-types.md) - Field type inference
- [Migration First](scaffold-migration-first.md) - Create migration with @metadata
- [Add CRUD Workflow](../workflow/workflow-add-crud.md) - Complete workflow

---
title: Add CRUD Workflow (v14)
impact: HIGH
impactDescription: Workflow for adding CRUD to existing tables with AntdAdmin
tags: workflow, crud, scaffold, v14, antdadmin
---

## Add CRUD Workflow (v14)

Workflow for adding CRUD functionality to an existing database table using v14 AntdAdmin components.

### When to Use This Rule

- Adding admin CRUD for existing table
- Creating admin interface for database table
- Extending existing module with CRUD operations

---

## Workflow Steps

### Step 1: Analyze Existing Table

```bash
# Check table structure
php artisan tinker
>>> Schema::getColumnListing('existing_table');
>>> Schema::getColumnType('existing_table', 'column_name');
```

Or query database directly:

```sql
DESCRIBE existing_table;
SHOW CREATE TABLE existing_table;
```

### Step 2: Create Model (If Not Exists)

If model doesn't exist, create it:

```php
<?php
namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;

class ExistingModel extends GyListModel
{
    protected $tableName = 'existing_table';
    protected $pk = 'id';

    // Add validation rules
    protected $_validate = [
        ['name', 'require', '名称不能为空', self::MUST_VALIDATE],
    ];

    // Add auto-fill rules
    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT, 'function'],
        ['update_time', 'time', self::MODEL_UPDATE, 'function'],
    ];

    // Add business methods with PHP 8.2 type declarations
    public function getStatusList(): array
    {
        return DBCont::getStatusList();
    }
}
```

### Step 3: Create Admin Controller (v14 AntdAdmin)

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

class ExistingController extends QsListController
{
    protected $modelName = 'Existing';
    protected $formWidth = '800px';

    public function index()
    {
        $map = [];
        $this->buildSearchWhere(I('get.'), $map);

        $model = D('Existing')->where($map);
        $count = $model->count();
        $page = new \Gy_Library\GyPage($count);

        $data_list = $model->page($page->nowPage, $page->listRows)
            ->order('id desc')
            ->select();

        $table = new Table();
        $table->setMetaTitle('列表管理')
            ->actions(function (Table\ActionsContainer $container) {
                $container->button('新增')
                    ->setProps(['type' => 'primary'])
                    ->modal((new Modal())
                        ->setWidth($this->formWidth)
                        ->setUrl(U('add'))
                        ->setTitle('新增'));
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
        $container->text('name', '名称')->setSearch(true);
        $container->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList())
            ->setBadge([1 => 'success', 0 => 'default'])
            ->setSearch(true);
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
        if (!empty($get_data['name'])) {
            $map['name'] = ['like', '%' . $get_data['name'] . '%'];
        }

        if (isset($get_data['status']) && $get_data['status'] !== '') {
            $map['status'] = $get_data['status'];
        }
    }
}
```

### Step 4: Add Form Methods

```php
public function add()
{
    if (IS_POST) {
        $data = I('post.');
        $result = D('Existing')->createAdd($data);
        if ($result === false) {
            $this->error(D('Existing')->getError());
        }
        $this->success('添加成功');
    }

    $form = new Form();
    $form->setSubmitRequest('post', U('add'))
        ->setInitialValues(['status' => 1])
        ->columns(function (Form\ColumnsContainer $columns) {
            $this->buildFormColumns($columns);
        })
        ->actions(function (Form\ActionsContainer $actions) {
            $actions->button('提交')->submit();
            $actions->button('重置')->reset();
        });

    return $form->render();
}

public function edit()
{
    $id = I('get.id', 0, 'intval');
    $data = D('Existing')->find($id);

    if (!$data) {
        $this->error('记录不存在');
    }

    if (IS_POST) {
        $data = I('post.');
        $result = D('Existing')->createSave($data);
        if ($result === false) {
            $this->error(D('Existing')->getError());
        }
        $this->success('保存成功');
    }

    $form = new Form();
    $form->setSubmitRequest('post', U('edit', ['id' => $id]))
        ->setInitialValues($data)
        ->columns(function (Form\ColumnsContainer $columns) {
            $this->buildFormColumns($columns);
        })
        ->actions(function (Form\ActionsContainer $actions) {
            $actions->button('提交')->submit();
            $actions->button('重置')->reset();
        });

    return $form->render();
}

protected function buildFormColumns(Form\ColumnsContainer $columns): void
{
    $columns->text('name', '名称')
        ->addRule(new Required())
        ->setFormItemWidth(24);

    $columns->select('status', '状态')
        ->setValueEnum(DBCont::getStatusList())
        ->setFormItemWidth(12);

    $columns->number('sort', '排序')
        ->setFormItemWidth(12);
}
```

### Step 5: Configure Permissions

Add menu entry in admin panel or run SQL:

```sql
INSERT INTO admin_menu (name, title, pid, level, url, status, sort)
VALUES ('Existing', 'Existing管理', 0, 1, 'Admin/Existing', 1, 100);

SET @pid = LAST_INSERT_ID();

INSERT INTO admin_menu (name, title, pid, level, url, status, sort) VALUES
('index', '列表', @pid, 2, 'Admin/Existing/index', 1, 0),
('add', '新增', @pid, 2, 'Admin/Existing/add', 1, 0),
('edit', '编辑', @pid, 2, 'Admin/Existing/edit', 1, 0),
('delete', '删除', @pid, 2, 'Admin/Existing/delete', 1, 0);
```

---

## Field Type Mapping (v14 AntdAdmin)

Map database types to AntdAdmin column types:

| Database Type | Table Column | Form Column |
|---------------|--------------|-------------|
| `varchar` | `text()` | `text()` |
| `text` | `text()` | `textarea()` |
| `int` (status) | `select()` with `setBadge()` | `select()` |
| `int` (FK) | `select()` with `setValueEnum()` | `select()` |
| `decimal` | `money()` or `number()` | `number()` |
| `date` | `date()` | `date()` |
| `datetime` | `datetime()` | `datetime()` |
| `tinyint(1)` | `select()` | `radio()` or `checkbox()` |
| `*_image`/`cover` | `image()` | `image()` |
| `*_content` | `text()` (truncated) | `ueditor()` |

---

## Common v14 Enhancements

### Add Image Upload

```php
// In buildTableColumns
$container->image('cover', '封面');

// In buildFormColumns
$columns->image('cover_id', '封面图')
    ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
    ->setCrop('16/9')
    ->setFormItemWidth(24);
```

### Add Rich Text Editor

```php
// In buildFormColumns
$columns->ueditor('content', '详情')
    ->setFormItemWidth(24);
```

### Add Foreign Key Relation

```php
// In buildTableColumns
$container->select('cate_id', '分类')
    ->setValueEnum(D('Category')->getField('id,name'))
    ->setSearch(true);

// In buildFormColumns
$columns->select('cate_id', '分类')
    ->setValueEnum(D('Category')->getField('id,name'))
    ->addRule(new Required())
    ->setFormItemWidth(24);

// In buildSearchWhere
if (!empty($get_data['cate_id'])) {
    $map['cate_id'] = $get_data['cate_id'];
}
```

### Add Date Range Search

```php
// In buildTableColumns
$container->datetime('create_time', '创建时间')
    ->setSearch(true);

// In buildSearchWhere
if (!empty($get_data['create_time'])) {
    $map = array_merge($map, \Qscmf\Builder\ListSearchType\DateRange::parse(
        'create_time',
        'create_time',
        $get_data
    ));
}
```

### Add Editable Column

```php
// In buildTableColumns
$container->number('sort', '排序')->editable();
```

### Add Modal Form (v14 Pattern)

```php
// In buildTableColumns - actions
$container->action('', '操作')
    ->actions(function (Table\ColumnType\ActionsContainer $container) {
        $container->edit()->modal(
            (new Modal())
                ->setWidth($this->formWidth)
                ->setUrl(U('edit', ['id' => '__id__']))
                ->setTitle('编辑')
        );
    });
```

---

## Complete Example: Full CRUD Controller

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
            ->order('sort asc, id desc')
            ->select();

        $table = new Table();
        $table->setMetaTitle('商品管理')
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
                $container->image('cover', '封面');
                $container->text('product_name', '商品名称')->setSearch(true);
                $container->select('cate_id', '分类')
                    ->setValueEnum(D('Category')->getField('id,name'))
                    ->setSearch(true);
                $container->money('price', '价格');
                $container->number('stock', '库存');
                $container->number('sort', '排序')->editable();
                $container->select('status', '状态')
                    ->setValueEnum(DBCont::getStatusList())
                    ->setBadge([1 => 'success', 0 => 'default'])
                    ->setSearch(true);
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
            })
            ->setDataSource($data_list)
            ->setPagination(new Pagination($page->nowPage, $page->listRows, $count))
            ->render();
    }

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
            ->setInitialValues(['status' => 1, 'sort' => 99])
            ->columns(function (Form\ColumnsContainer $columns) {
                $this->buildFormColumns($columns);
            })
            ->actions(function (Form\ActionsContainer $actions) {
                $actions->button('提交')->submit();
                $actions->button('重置')->reset();
            });

        return $form->render();
    }

    public function edit()
    {
        $id = I('get.id', 0, 'intval');
        $data = D('Product')->find($id);

        if (!$data) {
            $this->error('记录不存在');
        }

        if (IS_POST) {
            $data = I('post.');
            $result = D('Product')->createSave($data);
            if ($result === false) {
                $this->error(D('Product')->getError());
            }
            $this->success('保存成功');
        }

        $form = new Form();
        $form->setSubmitRequest('post', U('edit', ['id' => $id]))
            ->setInitialValues($data)
            ->columns(function (Form\ColumnsContainer $columns) {
                $this->buildFormColumns($columns);
            })
            ->actions(function (Form\ActionsContainer $actions) {
                $actions->button('提交')->submit();
                $actions->button('重置')->reset();
            });

        return $form->render();
    }

    protected function buildFormColumns(Form\ColumnsContainer $columns): void
    {
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

        $columns->number('price', '价格')
            ->setFormItemWidth(12);

        $columns->number('stock', '库存')
            ->setFormItemWidth(12);

        $columns->number('sort', '排序')
            ->setFormItemWidth(12);

        $columns->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList())
            ->setFormItemWidth(12);

        $columns->ueditor('content', '商品详情')
            ->setFormItemWidth(24);
    }

    protected function buildSearchWhere(array $get_data, array &$map): void
    {
        if (!empty($get_data['product_name'])) {
            $map['product_name'] = ['like', '%' . $get_data['product_name'] . '%'];
        }

        if (!empty($get_data['cate_id'])) {
            $map['cate_id'] = $get_data['cate_id'];
        }

        if (isset($get_data['status']) && $get_data['status'] !== '') {
            $map['status'] = $get_data['status'];
        }
    }
}
```

---

## Checklist

- [ ] Table structure analyzed
- [ ] Model created/updated with PHP 8.2 types
- [ ] Admin controller created with AntdAdmin components
- [ ] Index (list) method with Table component
- [ ] Add method with Form component
- [ ] Edit method with Form component
- [ ] Search conditions implemented
- [ ] Table columns configured
- [ ] Form fields configured
- [ ] Permissions configured
- [ ] Manual testing completed

---

## Related Rules

- [Create Module Workflow](workflow-create-module.md) - Creating new module
- [Table Columns Configuration](../crud/crud-table-columns.md) - Column types and custom renderers
- [Form Validation](../crud/crud-form-validation.md) - Form validation rules
- [AntdAdmin Components](../antdadmin.md) - Direct component usage
- [ListBuilder API](../listbuilder-api.md) - Backward compatible API

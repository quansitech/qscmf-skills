---
title: Add CRUD Workflow (v13)
impact: HIGH
impactDescription: Workflow for adding CRUD to existing tables
tags: workflow, crud, scaffold, v13
---

## Add CRUD Workflow (v13)

Workflow for adding CRUD functionality to an existing database table.

### When to Use This Rule

- Adding admin CRUD for existing table
- Creating admin interface for database table
- Extending existing module with CRUD

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

### Step 2: Create Model

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
        ['name', 'require', '名称不能为空'],
    ];

    // Add auto-fill rules
    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT, 'function'],
        ['update_time', 'time', self::MODEL_UPDATE, 'function'],
    ];

    // Add business methods
    public function getStatusList(): array
    {
        return DBCont::getStatusList();
    }
}
```

### Step 3: Create Admin Controller

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;
use Gy_Library\DBCont;

class ExistingController extends QsListController
{
    protected $modelName = 'Existing';

    public function index()
    {
        $map = $this->buildSearchMap(I('get.'));
        $list = D('Existing')->where($map)->order('id desc')->select();

        $builder = $this->builder();
        $builder->setMetaTitle('列表管理');

        // Add columns based on table structure
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('name', '名称');
        $builder->addTableColumn('status', '状态', DBCont::getStatusList());
        $builder->addTableColumn('create_time', '创建时间');

        // Add search items
        $builder->addSearchItem('keyword', 'text', '搜索');
        $builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());

        // Add buttons
        $builder->addTopButton('addnew');
        $builder->addTopButton('forbid');
        $builder->addTopButton('resume');
        $builder->addTopButton('delete');

        $builder->addRightButton('edit');
        $builder->addRightButton('delete');

        $builder->setData($list);
        $builder->display();
    }

    protected function buildSearchMap(array $search): array
    {
        $map = [];

        if (!empty($search['keyword'])) {
            $map['name'] = ['like', '%' . $search['keyword'] . '%'];
        }

        if (isset($search['status']) && $search['status'] !== '') {
            $map['status'] = $search['status'];
        }

        return $map;
    }
}
```

### Step 4: Add Form Methods

```php
public function add()
{
    $builder = $this->builder();
    $this->buildFormItems($builder);
    $builder->display();
}

public function edit()
{
    $id = I('get.id', 0, 'intval');
    $data = D('Existing')->find($id);

    if (!$data) {
        $this->error('记录不存在');
    }

    $builder = $this->builder();
    $this->buildFormItems($builder);
    $builder->setData($data);
    $builder->display();
}

protected function buildFormItems($builder)
{
    $builder->addFormItem('name', 'text', '名称', '请输入名称', true);
    $builder->addFormItem('status', 'radio', '状态', DBCont::getStatusList());
}
```

### Step 5: Add Save/Delete Methods

```php
public function save()
{
    $data = I('post.');

    if (empty($data['name'])) {
        $this->error('名称不能为空');
    }

    $result = parent::save($data);

    if ($result !== false) {
        $this->success('保存成功', U('index'));
    } else {
        $this->error('保存失败');
    }
}

public function delete()
{
    $ids = I('get.ids');
    if (empty($ids)) {
        $this->error('请选择要删除的记录');
    }

    $id_array = explode(',', $ids);
    $result = D('Existing')->where(['id' => ['IN', $id_array]])->delete();

    if ($result !== false) {
        $this->success('删除成功', U('index'));
    } else {
        $this->error('删除失败');
    }
}
```

### Step 6: Configure Permissions

Add menu entry in admin panel or run SQL:

```sql
INSERT INTO qs_node (name, title, pid, level, url, status, sort)
VALUES ('Existing', 'Existing管理', 0, 1, 'Admin/Existing', 1, 100);
```

---

## Field Type Mapping

Map database types to form types:

| Database Type | Form Type |
|---------------|-----------|
| `varchar` | text |
| `text` | textarea |
| `int` (status) | select/radio |
| `int` (FK) | select |
| `decimal` | num |
| `date` | date |
| `datetime` | datetime |
| `tinyint(1)` | radio/checkbox |

---

## Checklist

- [ ] Table structure analyzed
- [ ] Model created/updated
- [ ] Admin controller created
- [ ] Index (list) method added
- [ ] Add/Edit methods added
- [ ] Save method added
- [ ] Delete method added
- [ ] Permissions configured
- [ ] Manual testing completed

---

## Related Rules

- [Create Module Workflow](workflow-create-module.md) - Creating new module
- [ListBuilder API](../listbuilder-api.md) - Table configuration
- [FormBuilder API](../formbuilder-api.md) - Form configuration

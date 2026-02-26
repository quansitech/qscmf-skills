---
title: ListBuilder API Reference (v13)
impact: CRITICAL
impactDescription: Core API for all v13 CRUD operations (100% usage)
tags: api, listbuilder, table, v13, core
---

## ListBuilder API Reference (v13)

The ListBuilder API is the core interface for building admin tables in QSCMF v13 with jQuery/Bootstrap rendering.

### When to Use This Rule

- Building admin CRUD tables in v13
- Adding table columns with various types
- Configuring search functionality
- Adding action buttons (top and row-level)

---

## Quick Reference

### Core Methods

```php
$builder = $this->builder();  // Get ListBuilder instance

// Table columns
$builder->addTableColumn($name, $title, $type = '', $options = '', $extra = '');

// Search items
$builder->addSearchItem($name, $type, $title, $default = '', $options = '');

// Buttons
$builder->addTopButton($type, $attributes = []);
$builder->addRightButton($type, $attributes = []);

// Configuration
$builder->setCheckBox($enabled = true, $callback = null);
$builder->setMetaTitle($title);
$builder->setData($data);
$builder->display();
```

---

## Table Column Types

### 1. Text Column (Default)

```php
$builder->addTableColumn('id', 'ID');
$builder->addTableColumn('name', '名称');
```

### 2. Status/Select Column

Display mapped values from array:

```php
// Using DBCont constants
$builder->addTableColumn('status', '状态', DBCont::getStatusList());

// Custom mapping
$builder->addTableColumn('audit_status', '审核状态', [
    0 => '<span class="label label-default">待审核</span>',
    1 => '<span class="label label-success">已通过</span>',
    2 => '<span class="label label-danger">已拒绝</span>'
]);
```

### 3. Date/Time Column

```php
// Date format
$builder->addTableColumn('create_time', '创建时间', 'date_format', 'Y-m-d H:i');

// Time type (auto-format)
$builder->addTableColumn('publish_time', '发布时间', 'time');
```

### 4. Picture Column

```php
// Single image
$builder->addTableColumn('cover', '封面图', 'picture');

// With custom thumbnail
$builder->addTableColumn('proof', '凭证', 'picture', [
    'small-url' => function($image_id) {
        $url = showFileUrl($image_id);
        return $url . '?x-oss-process=image/resize,m_fill,w_40,h_40';
    }
]);
```

### 5. Pictures Column (Multiple)

```php
$builder->addTableColumn('images', '图片集', 'pictures');
```

### 6. Number Column

```php
$builder->addTableColumn('sort', '排序', 'num');
$builder->addTableColumn('price', '价格', 'num');
```

### 7. Checkbox Column

```php
$builder->addTableColumn('is_recommend', '推荐', 'checkbox');
$builder->addTableColumn('is_hot', '热门', 'checkbox');
```

### 8. Link Column

```php
$builder->addTableColumn('url', '链接', 'a');

// With custom href
$builder->addTableColumn('id', '操作', 'a', [
    'title' => '查看详情',
    'href' => U('detail', ['id' => '@id@'])
]);
```

### 9. Custom Function Column

```php
$builder->addTableColumn('custom', '自定义', 'fun', function($value, $data) {
    return $data['field1'] . ' - ' . $data['field2'];
});

// Complex example
$builder->addTableColumn('user_id', '用户', 'fun', function($user_id, $row) {
    $user = D('User')->find($user_id);
    return $user ? $user['username'] : '未知';
});
```

### 10. Textarea Column (Truncated)

```php
$builder->addTableColumn('summary', '摘要', 'textarea');
```

---

## Search Item Types

### 1. Text Search

```php
$builder->addSearchItem('keyword', 'text', '关键词');
```

### 2. Select Search

```php
// Status dropdown
$builder->addSearchItem('status', 'select', '状态', '', [
    '' => '全部',
    1 => '启用',
    0 => '禁用'
]);

// Using DBCont
$builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());

// From model
$builder->addSearchItem('cate_id', 'select', '分类', '', D('Category')->getFieldOptions());
```

### 3. Date Search

```php
$builder->addSearchItem('create_date', 'date', '创建时间');
```

### 4. Date Range Search

```php
$builder->addSearchItem('donate_date', 'date_range', '时间范围', ['time_picker' => '0']);

// With time picker
$builder->addSearchItem('create_time', 'date_range', '创建时间', ['time_picker' => '1']);
```

### 5. Between Search

```php
$builder->addSearchItem('price', 'between', '价格范围');
```

---

## Top Button Types

### 1. Add New Button

```php
$builder->addTopButton('addnew', [
    'title' => '新增',
    'href' => U('add')
]);
```

### 2. Forbid (Disable) Button

```php
$builder->addTopButton('forbid', [
    'title' => '禁用',
    'href' => U('toggleStatus', ['type' => 'forbid']),
    'ajax' => true,
    'confirm' => '确定要禁用选中的记录吗？'
]);
```

### 3. Resume (Enable) Button

```php
$builder->addTopButton('resume', [
    'title' => '启用',
    'href' => U('toggleStatus', ['type' => 'resume']),
    'ajax' => true,
    'confirm' => '确定要启用选中的记录吗？'
]);
```

### 4. Delete Button

```php
$builder->addTopButton('delete', [
    'title' => '删除',
    'href' => U('delete'),
    'ajax' => true,
    'confirm' => '确定要删除选中的记录吗？'
]);
```

### 5. Custom Button

```php
$builder->addTopButton('custom', [
    'title' => '导出',
    'href' => U('export'),
    'icon' => 'fa fa-download',
    'class' => 'btn btn-info must-select-item',
    'must-select-msg' => '请选择要导出的数据'
]);
```

---

## Right Button Types (Row Actions)

### 1. Edit Button

```php
$builder->addRightButton('edit', [
    'title' => '编辑',
    'href' => U('edit', ['id' => '@id@'])
]);
```

### 2. Delete Button

```php
$builder->addRightButton('delete', [
    'title' => '删除',
    'href' => U('delete', ['ids' => '@id@']),
    'confirm' => '确定要删除该记录吗？'
]);
```

### 3. Forbid/Resume Button

```php
$builder->addRightButton('forbid', [
    'title' => '禁用',
    'href' => U('toggleStatus', ['type' => 'forbid', 'ids' => '@id@']),
    'ajax' => true
]);
```

### 4. Custom Button

```php
$builder->addRightButton('custom', [
    'title' => '查看',
    'href' => U('detail', ['id' => '@id@']),
    'icon' => 'fa fa-eye'
]);
```

---

## Placeholder Syntax

Use `@field_name@` in button href attributes:

```php
// Use @id@ for primary key
'href' => U('edit', ['id' => '@id@'])

// Use any field name
'href' => U('index', ['name' => '@name@'])

// Use @project_id@ for underscored fields
'href' => U('detail', ['project_id' => '@project_id@'])
```

---

## Checkbox Configuration

```php
// Enable checkbox
$builder->setCheckBox(true);

// With disabled callback
$builder->setCheckBox(true, function($attr, $data) {
    if ($data['type'] === 'manual') {
        $attr['disabled'] = 'disabled';
    }
    return $attr;
});

// Using helper method for condition
$builder->setCheckBox(true, ListBuilder::genCheckBoxDisableCb('manual', 0));
```

---

## Search Parameter Parsing

### DateRange Parse

```php
use Qscmf\Builder\ListSearchType\DateRange;

$map = array_merge($map, DateRange::parse('date_range_data', 'create_date', $get_data));
```

### Text Parse

```php
use Qscmf\Builder\ListSearchType\Text;

// Fuzzy search (default)
$map = array_merge($map, Text::parse('keyword', 'name', $get_data, 'fuzzy'));

// Exact search
$map = array_merge($map, Text::parse('code', 'code', $get_data, 'exact'));
```

### Select Parse

```php
use Qscmf\Builder\ListSearchType\Select;

$map = array_merge($map, Select::parse('cate_id', 'cate_id', $get_data));
```

### SelectText Parse (Advanced)

```php
use Qscmf\Builder\ListSearchType\SelectText;

$map = array_merge($map, SelectText::parse([
    'employee_name' => [
        'map_key' => 'employee_id',
        'rule' => function($map_key, $word) {
            $employee_sql = D('Employee')->where(['name' => ['like', '%'.$word.'%']])->field('id')->buildSql();
            return [$map_key => ['exp', 'in '.$employee_sql]];
        }
    ],
    'reason' => [
        'map_key' => 'reason',
        'rule' => 'fuzzy'
    ]
], $get_data));
```

---

## Complete Example

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;
use Gy_Library\DBCont;

class ProductController extends QsListController
{
    protected $modelName = 'Product';

    public function index()
    {
        $map = $this->buildSearchMap(I('get.'));
        $list = D('Product')->where($map)->order('id desc')->select();

        $builder = $this->builder();
        $builder->setMetaTitle('商品列表');
        $builder->setCheckBox(true);

        // Table columns
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('name', '名称');
        $builder->addTableColumn('cate_id', '分类', D('Category')->getFieldOptions());
        $builder->addTableColumn('cover', '封面', 'picture');
        $builder->addTableColumn('price', '价格', 'num');
        $builder->addTableColumn('status', '状态', DBCont::getStatusList());
        $builder->addTableColumn('create_time', '创建时间', 'date_format', 'Y-m-d H:i');

        // Search items
        $builder->addSearchItem('keyword', 'text', '搜索');
        $builder->addSearchItem('cate_id', 'select', '分类', '', D('Category')->getFieldOptions());
        $builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());

        // Top buttons
        $builder->addTopButton('addnew', ['title' => '新增']);
        $builder->addTopButton('forbid');
        $builder->addTopButton('resume');
        $builder->addTopButton('delete');

        // Right buttons
        $builder->addRightButton('edit', ['href' => U('edit', ['id' => '@id@'])]);
        $builder->addRightButton('delete', ['href' => U('delete', ['ids' => '@id@'])]);

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

        if (!empty($search['cate_id'])) {
            $map['cate_id'] = $search['cate_id'];
        }

        return $map;
    }
}
```

---

## Related Rules

- [FormBuilder API](formbuilder-api.md) - Form field configuration
- [Table Columns v13](crud/crud-table-columns-v13.md) - Detailed column configuration
- [Search Basic](crud/crud-search-basic.md) - Search functionality
- [Legacy jQuery](legacy-jquery.md) - v13 specific jQuery quirks

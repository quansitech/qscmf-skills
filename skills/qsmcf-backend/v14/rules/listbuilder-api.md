# ListBuilder API Reference

Complete reference for the ListBuilder API used in QSCMF for building admin list pages.

## API Choice in v14

QSCMF v14 supports TWO APIs:

1. **AntdAdmin Component API** (recommended for new projects)
   - Use: `new \AntdAdmin\Component\Table()`
   - Rendering: React/AntdAdmin components
   - See: [antdadmin.md](antdadmin.md)

2. **ListBuilder API** (legacy, backward compatible)
   - Use: `$this->builder()` in QsListController
   - Rendering: jQuery or React (controlled by `ANTD_ADMIN_BUILDER_ENABLE`)

This document covers the **ListBuilder API** (legacy).

---

## Core Methods

### Table Configuration

| Method | Parameters | Description |
|--------|-----------|-------------|
| `setMetaTitle($title)` | string | Set page title |
| `setCheckBox($enabled, $callback)` | bool, callable | Enable checkbox selection |
| `setData($data)` | array | Set table data |
| `setPage($page, $pageSize)` | int, int | Configure pagination |
| `display()` | - | Render the table |

### Table Columns

```php
$builder->addTableColumn($name, $title, $type, $value, $editable, $tip, $th_extra_attr, $td_extra_attr, $auth_node);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `$name` | string | Field name |
| `$title` | string | Column title |
| `$type` | string | Column type (see below) |
| `$value` | mixed | Type-specific value |
| `$editable` | bool/callable | Enable inline editing |
| `$tip` | string | Column tooltip |
| `$th_extra_attr` | string | Header cell extra attributes |
| `$td_extra_attr` | string | Data cell extra attributes |
| `$auth_node` | array/string | Permission node |

### Column Types

| Type | Description | Value Format |
|------|-------------|--------------|
| `text` (default) | Plain text | - |
| `status` | Status badge | Array of values |
| `icon` | Icon display | - |
| `date` | Date format | Format string (Y-m-d) |
| `time` | DateTime format | Format string (Y-m-d H:i:s) |
| `picture` | Single image | - |
| `pictures` | Multiple images | - |
| `type` | Custom type mapping | Array |
| `fun` | Custom function | Callable |
| `a` | Link | Array with href, title |
| `self` | Custom template | Template path |
| `num` | Number with format | - |
| `checkbox` | Checkbox selection | - |
| `select` | Select display | Array of options |
| `select2` | Enhanced select | - |
| `textarea` | Truncated text | - |
| `btn` | Button column | - |

### Top Buttons

```php
$builder->addTopButton($type, $attribute, $tips, $auth_node, $options);
```

| Type | Description |
|------|-------------|
| `addnew` | Add new record |
| `submit` | Submit form |
| `resume` | Enable records |
| `forbid` | Disable records |
| `delete` | Delete records |
| `modal` | Modal button |
| `custom` | Custom button |

### Right Buttons

```php
$builder->addRightButton($type, $attribute, $tips, $auth_node, $options);
```

| Type | Description |
|------|-------------|
| `edit` | Edit record |
| `delete` | Delete record |
| `forbid` | Disable record |
| `resume` | Enable record |
| `self` | Custom template |
| `custom` | Custom action |

### Search Items

```php
$builder->addSearchItem($name, $type, $title, $options, $auth_node);
```

| Type | Description |
|------|-------------|
| `text` | Text input |
| `select` | Dropdown select |
| `date` | Date picker |
| `time` | Time picker |
| `datetime` | DateTime picker |
| `between` | Range input |
| `checkbox` | Multiple checkboxes |
| `date_range` | Date range picker |
| `hidden` | Hidden filter |
| `select_text` | Select with text search |
| `select_city` | City selector |
| `self` | Custom template |

---

## Search Item Parse Methods

### DateRange

```php
$map = array_merge($map, \Qscmf\Builder\ListSearchType\DateRange::parse(
    'date_range_data',
    'create_date',
    $get_data
));
```

### Hidden

```php
$map = array_merge($map, \Qscmf\Builder\ListSearchType\Hidden::parse(
    'employee_id',
    'employee_id',
    $get_data
));
```

### Text

```php
$map = array_merge($map, \Qscmf\Builder\ListSearchType\Text::parse(
    'keyword',
    'product_name',
    $get_data,
    'fuzzy' // or 'exact'
));
```

### SelectText

```php
$map = array_merge($map, \Qscmf\Builder\ListSearchType\SelectText::parse([
    'field_name' => [
        'map_key' => 'db_field',
        'rule' => 'fuzzy' // or 'exact' or callable
    ]
], $get_data));
```

---

## Placeholder Syntax

Use `@field_name@` for dynamic value replacement:

```php
$builder->addRightButton('edit', [
    'href' => U('edit', ['id' => '@id@', 'name' => '@product_name@'])
]);
```

---

## Permission Control

```php
// Single permission node
$builder->addTableColumn('id', 'ID', '', '', '', '', '', '', 'admin.Product.id');

// Multiple permission nodes with AND logic
$builder->addRightButton('edit', [...], '', [
    'node' => ['admin.Product.edit', 'admin.Product.list'],
    'logic' => 'and'
]);

// Multiple permission nodes with OR logic
$builder->addRightButton('view', [...], '', [
    'node' => ['admin.Product.view', 'admin.Product.list'],
    'logic' => 'or'
]);
```

---

## Checkbox Configuration

```php
// Basic checkbox
$builder->setCheckBox(true);

// Custom checkbox callback
$builder->setCheckBox(true, function($attr, $data) {
    if ($data['type'] === 'manual') {
        $attr['disabled'] = 'disabled';
    }
    return $attr;
});

// Disable checkbox based on field value
$builder->setCheckBox(true, \Qscmf\Builder\ListBuilder::genCheckBoxDisableCb('status', 0));
```

---

## Pagination Configuration

```php
// Use QsPage (dropdown style)
\Gy_Library\QsPage::setPullStyle(true);

// Number pagination (default)
\Gy_Library\QsPage::setPullStyle(false);
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
        $model = D('Product')->where($map);
        $total = $model->count();

        $builder = $this->builder();
        $builder->setMetaTitle('商品列表');

        // Configure columns
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('product_name', '商品名称');
        $builder->addTableColumn('price', '价格', 'num');
        $builder->addTableColumn('status', '状态', DBCont::getStatusList());
        $builder->addTableColumn('create_time', '创建时间', 'time');
        $builder->addTableColumn('right_button', '操作', 'btn');

        // Configure search
        $builder->addSearchItem('keyword', 'text', '关键词');
        $builder->addSearchItem('status', 'select', '状态', DBCont::getStatusList());
        $builder->addSearchItem('create_time', 'date_range', '创建时间');

        // Configure buttons
        $builder->addTopButton('addnew', ['title' => '新增', 'href' => U('add')]);
        $builder->addTopButton('resume');
        $builder->addTopButton('forbid');
        $builder->addTopButton('delete');

        $builder->addRightButton('edit', ['href' => U('edit', ['id' => '@id@'])]);
        $builder->addRightButton('delete');

        // Set data
        $list = $model->order('id desc')->select();
        $builder->setData($list);

        // Enable checkbox
        $builder->setCheckBox(true);

        $builder->display();
    }
}
```

---

## Related Documentation

- [AntdAdmin Components](antdadmin.md) - Modern React API (v14)
- [FormBuilder API](formbuilder-api.md) - Form building API

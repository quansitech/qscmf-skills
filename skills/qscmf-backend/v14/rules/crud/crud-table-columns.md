---
title: Table Columns Configuration (v14)
impact: HIGH
impactDescription: Required for all admin list pages
tags: crud, table, columns, v14, antdadmin
---

## Table Columns Configuration (v14 - AntdAdmin)

Complete reference for configuring table columns using AntdAdmin Component API in QSCMF v14.

### When to Use This Rule

- Building admin list pages with React rendering
- Configuring table columns with modern API
- Adding column-level features like search, inline edit

---

## Quick Reference

```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\ColumnsContainer;

protected function buildTableColumns(ColumnsContainer $container)
{
    // Basic text column
    $container->text('product_name', '商品名称');

    // Select with badge colors
    $container->select('status', '状态')
        ->setValueEnum(DBCont::getStatusList())
        ->setBadge([1 => 'success', 0 => 'default']);

    // Number with inline edit
    $container->number('sort', '排序')
        ->editable();

    // DateTime column
    $container->datetime('create_time', '创建时间');
}
```

---

## Column Types

### 1. Text (Default)

```php
// Basic text
$container->text('name', '名称');

// With search enabled
$container->text('product_name', '商品名称')
    ->setSearch(true);

// With copy functionality
$container->text('order_no', '订单号')
    ->setCopyable(true);

// With ellipsis for long text
$container->text('description', '描述')
    ->setEllipsis(true);
```

### 2. Select/Status

```php
// Using DBCont constants
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList())
    ->setBadge([1 => 'success', 0 => 'default']);

// Custom options
$container->select('audit_status', '审核状态')
    ->setValueEnum([
        0 => '待审核',
        1 => '已通过',
        2 => '已拒绝'
    ])
    ->setBadge([
        0 => 'warning',
        1 => 'success',
        2 => 'error'
    ]);

// From model
$container->select('cate_id', '分类')
    ->setValueEnum(D('Category')->getField('id,name'))
    ->setSearch(true);

// Multiple select display
$container->select('tags', '标签')
    ->setValueEnum(D('Tag')->getField('id,name'))
    ->setMode('multiple');
```

### 3. Number

```php
// Basic number
$container->number('stock', '库存');

// With inline edit
$container->number('sort', '排序')
    ->editable();

// With search
$container->number('quantity', '数量')
    ->setSearch(true);
```

### 4. Money/Currency

```php
// Basic money display
$container->money('price', '价格');

// With search
$container->money('amount', '金额')
    ->setSearch(true);

// Custom currency symbol
$container->money('total', '总计')
    ->setMoneySymbol('USD');
```

### 5. Date/Time

```php
// Date only
$container->date('publish_date', '发布日期');

// DateTime
$container->datetime('create_time', '创建时间');

// With search
$container->datetime('create_time', '创建时间')
    ->setSearch(true);
```

### 6. Image

```php
// Single image
$container->image('cover', '封面');

// Multiple images
$container->images('gallery', '图片集');

// With custom size
$container->image('avatar', '头像')
    ->setWidth(60)
    ->setHeight(60);
```

### 7. Action Column

```php
$container->action('', '操作')
    ->actions(function (Table\ColumnType\ActionsContainer $container) {
        // Edit with modal
        $container->edit()->modal(
            (new Modal())
                ->setWidth('800px')
                ->setUrl(U('edit', ['id' => '__id__']))
                ->setTitle('编辑')
        );

        // Delete
        $container->delete();

        // Forbid/Resume
        $container->forbid();
        $container->resume();

        // Custom action
        $container->button('查看')
            ->setProps(['type' => 'link'])
            ->modal((new Modal())
                ->setWidth('600px')
                ->setUrl(U('detail', ['id' => '__id__']))
                ->setTitle('详情'));
    });
```

### 8. Custom Renderer

```php
// Using callback for custom display
$container->text('user_info', '用户信息')
    ->setRender(function($value, $row) {
        return $row['first_name'] . ' ' . $row['last_name'];
    });

// Complex custom display
$container->text('price_display', '价格')
    ->setRender(function($value, $row) {
        $price = number_format($row['price'], 2);
        return '<span style="color: red;">¥' . $price . '</span>';
    });

// Status with icon
$container->text('status_icon', '状态')
    ->setRender(function($value, $row) {
        $icons = [1 => 'check-circle', 0 => 'close-circle'];
        $colors = [1 => 'green', 0 => 'red'];
        return sprintf(
            '<i class="anticon anticon-%s" style="color:%s"></i>',
            $icons[$row['status']] ?? 'question',
            $colors[$row['status']] ?? 'gray'
        );
    });
```

### 9. Common Render Patterns

```php
// Status with color badge
$container->text('status_display', '状态')
    ->setRender(function($value, $row) {
        $color_map = [0 => 'default', 1 => 'success', 2 => 'warning', 3 => 'error'];
        $text_map = [0 => '待处理', 1 => '已完成', 2 => '处理中', 3 => '已取消'];
        $status = $row['status'];
        return sprintf(
            '<span class="ant-tag ant-tag-%s">%s</span>',
            $color_map[$status] ?? 'default',
            $text_map[$status] ?? '未知'
        );
    });

// Image with preview
$container->text('cover_display', '封面')
    ->setRender(function($value, $row) {
        if (empty($row['cover'])) {
            return '<span class="ant-tag">无图片</span>';
        }
        $url = get_image_url($row['cover']);
        return sprintf(
            '<a href="%s" target="_blank"><img src="%s" style="max-width:60px;max-height:40px;"></a>',
            $url, $url
        );
    });

// Avatar with name
$container->text('user', '用户')
    ->setRender(function($value, $row) {
        $user = D('User')->find($row['user_id']);
        if (!$user) return '未知';
        $avatar = !empty($user['avatar']) ? get_image_url($user['avatar']) : 'https://ui-avatars.com/api/?name=' . urlencode($user['name']);
        return sprintf(
            '<div style="display: flex; align-items: center;"><img src="%s" style="width: 32px; height: 32px; border-radius: 50%; margin-right: 8px;"><span>%s</span></div>',
            $avatar, $user['name']
        );
    });

// Multi-column info
$container->text('product_info', '商品信息')
    ->setRender(function($value, $row) {
        return sprintf(
            '<div><div class="product-name"><strong>%s</strong></div><div class="text-muted">编码: %s</div><div class="text-danger">¥%s</div></div>',
            $row['name'], $row['code'], number_format($row['price'], 2)
        );
    });

// Link with action
$container->text('action_link', '操作')
    ->setRender(function($value, $row) {
        return sprintf('<a href="%s" class="ant-btn ant-btn-link">查看</a>', U('detail', ['id' => $row['id']]));
    });
```

---

## Custom Column Types

### Extending BaseColumn

```php
<?php
namespace Admin\Component;

use AntdAdmin\Component\Table\ColumnType\BaseColumn;
use Gy_Library\DBCont;

class StatusColumn extends BaseColumn
{
    protected $type = 'select';

    public function setStatusMap(array $map)
    {
        $this->setValueEnum($map);
        return $this;
    }

    public function setDefaultBadge()
    {
        $this->setBadge([
            DBCont::NORMAL_STATUS => 'success',
            DBCont::FORBIDDEN_STATUS => 'default'
        ]);
        return $this;
    }

    public function enableSearch()
    {
        $this->setSearch(true);
        return $this;
    }
}
```

### Using Custom Column

```php
use Admin\Component\StatusColumn;

$table->columns(function (Table\ColumnsContainer $container) {
    $status = new StatusColumn('status', '状态');
    $status->setStatusMap(DBCont::getStatusList())
        ->setDefaultBadge()
        ->enableSearch();

    $container->addColumn($status);
});
```

---

## Column Methods

### Common Methods

| Method | Description | Example |
|--------|-------------|---------|
| `setSearch($enabled)` | Enable/disable column search | `->setSearch(true)` |
| `setFormItemWidth($width)` | Set column width (1-24 grid) | `->setFormItemWidth(12)` |
| `setTooltip($text)` | Set column tooltip | `->setTooltip('帮助信息')` |
| `setFixed($position)` | Fixed column (left/right) | `->setFixed('left')` |

### Select Column Methods

| Method | Description | Example |
|--------|-------------|---------|
| `setValueEnum($values)` | Set enum values | `->setValueEnum([1 => '启用'])` |
| `setBadge($colors)` | Set badge colors | `->setBadge([1 => 'success'])` |
| `setMode($mode)` | Selection mode | `->setMode('multiple')` |

### Number Column Methods

| Method | Description | Example |
|--------|-------------|---------|
| `editable()` | Enable inline editing | `->editable()` |
| `setPrecision($precision)` | Decimal precision | `->setPrecision(2)` |

### Image Column Methods

| Method | Description | Example |
|--------|-------------|---------|
| `setWidth($width)` | Set image width | `->setWidth(60)` |
| `setHeight($height)` | Set image height | `->setHeight(60)` |

---

## Badge Colors

| Value | Color | Use Case |
|-------|-------|----------|
| `success` | Green | Active, completed |
| `processing` | Blue (animated) | In progress |
| `warning` | Orange | Pending, warning |
| `error` | Red | Error, rejected |
| `default` | Gray | Inactive, default |

---

## Inline Editing

### Enable Inline Edit

```php
// Number column with inline edit
$container->number('sort', '排序')
    ->editable();

// With condition callback
$container->number('amount', '金额')
    ->editable(function($row) {
        return $row['is_manual'] === 1;
    });
```

### Handling Inline Edit Save

The framework automatically handles inline edit saves. Ensure your Model has proper field validation:

```php
// In Model
protected $_validate = [
    ['sort', 'number', '排序必须为数字', self::VALUE_VALIDATE],
];
```

---

## Search Configuration

### Enable Search on Column

```php
// Text search (fuzzy by default)
$container->text('name', '名称')
    ->setSearch(true);

// Select search
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList())
    ->setSearch(true);

// Date range search
$container->datetime('create_time', '创建时间')
    ->setSearch(true);
```

### Search Handler

```php
protected function buildSearchWhere($get_data, &$map)
{
    // Text search (fuzzy)
    if (!empty($get_data['name'])) {
        $map['name'] = ['like', '%' . $get_data['name'] . '%'];
    }

    // Select search (exact)
    if (isset($get_data['status']) && $get_data['status'] !== '') {
        $map['status'] = $get_data['status'];
    }

    // Date range
    if (!empty($get_data['create_time'])) {
        $map = array_merge($map, \Qscmf\Builder\ListSearchType\DateRange::parse(
            'create_time',
            'create_time',
            $get_data
        ));
    }
}
```

---

## Complete Example

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;
use AntdAdmin\Component\Modal\Modal;
use Gy_Library\DBCont;

class ProductController extends QsListController
{
    protected $modelName = 'Product';

    public function index()
    {
        $map = [];
        $this->buildSearchWhere(I('get.'), $map);

        $model = D('Product')->where($map);
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
                $container->text('id', 'ID');
                $container->text('product_name', '商品名称')
                    ->setSearch(true);
                $container->select('cate_id', '分类')
                    ->setValueEnum(D('Category')->getField('id,name'))
                    ->setSearch(true);
                $container->image('cover', '封面');
                $container->money('price', '价格')
                    ->setSearch(true);
                $container->number('stock', '库存')
                    ->editable();
                $container->select('status', '状态')
                    ->setValueEnum(DBCont::getStatusList())
                    ->setBadge([1 => 'success', 0 => 'default'])
                    ->setSearch(true);
                $container->number('sort', '排序')
                    ->editable();
                $container->datetime('create_time', '创建时间');
                $container->action('', '操作')
                    ->actions(function (Table\ColumnType\ActionsContainer $container) {
                        $container->edit()->modal(
                            (new Modal())
                                ->setWidth('800px')
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
            ->setSearch(false)
            ->render();
    }

    protected function buildSearchWhere($get_data, &$map)
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
        if (!empty($get_data['price'])) {
            $map['price'] = $get_data['price'];
        }
    }
}
```

---

## Related Rules

- [AntdAdmin Components](../antdadmin.md) - Complete component reference
- [CRUD Search Basic](crud-search-basic.md) - Search configuration
- [Form Validation](crud-form-validation.md) - Form validation rules
- [ListBuilder API](../listbuilder-api.md) - Legacy API reference

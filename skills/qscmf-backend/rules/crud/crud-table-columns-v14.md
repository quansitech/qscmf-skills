---
title: Table Columns Configuration (v14 - AntdAdmin)
impact: HIGH
impactDescription: Core CRUD UI component (30% daily usage)
tags: crud, table, columns, antd-admin, v14, modern
---

## Table Columns Configuration (v14 - AntdAdmin)

Complete reference for configuring table columns using the modern AntdAdmin API (React-based) in QSCMF v14.

### When to Use This Rule

- You are working on a QSCMF v14 project
- You need to configure table columns in an Admin controller
- You want to add search functionality with advanced filtering
- You need to configure custom renderers for complex displays
- You want to use inline editing, batch actions, or async data loading

---

## Complete Method Reference

### AntdAdmin Column Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `text()` | `$field, $title` | Column | Text column with search support |
| `select()` | `$field, $title` | Column | Select column with enum mapping |
| `date()` | `$field, $title` | Column | Date column with range search |
| `image()` | `$field, $title` | Column | Image column with dimensions |
| `action()` | `$field, $title` | Column | Action button column |
| `custom()` | `$field, $title` | Column | Custom renderer column |
| `setSearch()` | `$enable` | Column | Enable/disable search input |
| `setSearchType()` | `$type` | Column | Set search type (like/exact/between) |
| `setSearchPlaceholder()` | `$text` | Column | Set search input placeholder |
| `setSearchDefault()` | `$value` | Column | Set default search value |
| `setSortable()` | `$enable` | Column | Enable/disable column sorting |
| `setWidth()` | `$width` | Column | Set column width |
| `setEllipsis()` | `$enable` | Column | Enable text overflow ellipsis |
| `setShowCondition()` | `$field, $op, $value` | Column | Conditional display |
| `setValueEnum()` | `$enum` | Column | Set enum value mapping |
| `setBadge()` | `$map` | Column | Set status badge colors |
| `setRenderer()` | `$callback` | Column | Set custom renderer function |
| `setFormat()` | `$format` | Column | Set date/time format |
| `setHeight()` | `$height` | Column | Set image height |
| `setParams()` | `$params` | Column | Set action parameters |
| `actions()` | `$callback` | Column | Configure action buttons |
| `editable()` | - | Column | Enable inline editing |

---

## Column Types

AntdAdmin supports 6 column types with fluent method chaining:

### 1. Text Column

Basic text column with search support.

```php
// Simple text column
$container->text('name', '名称');

// With search enabled
$container->text('name', '名称')
    ->setSearch(true)
    ->setSearchType('like')
    ->setSearchPlaceholder('请输入名称');

// With sorting
$container->text('title', '标题')
    ->setSearch(true)
    ->setSearchType('like')
    ->setSortable(true)
    ->setWidth(200)
    ->setEllipsis(true);

// Complex text configuration
$container->text('product_name', '商品名称')
    ->setSearch(true)
    ->setSearchType('like')
    ->setSearchPlaceholder('搜索商品名称')
    ->setSearchDefault('')  // Default empty value
    ->setSortable(true)
    ->setWidth(250)
    ->setEllipsis(true)
    ->setShowCondition('status', 'eq', 1);  // Only show when status = 1
```

**Search Types:**
- `like` - Fuzzy search (default for text)
- `exact` - Exact match search
- `between` - Range search (for numeric text)

### 2. Select Column

Dropdown selection column with value mapping and badge display.

```php
// Basic select with DBCont
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList())
    ->setBadge([1 => 'success', 0 => 'default']);

// With search
$container->select('cate_id', '分类')
    ->setValueEnum(D('Category')->getFields())
    ->setSearch(true)
    ->setSearchType('exact')
    ->setWidth(150);

// Custom enum with badges
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
    ])
    ->setSearch(true)
    ->setSearchType('exact');

// Conditional badge display
$container->select('order_status', '订单状态')
    ->setValueEnum([
        0 => '待付款',
        1 => '已付款',
        2 => '已发货',
        3 => '已完成',
        4 => '已取消'
    ])
    ->setBadge([
        0 => 'default',
        1 => 'processing',
        2 => 'warning',
        3 => 'success',
        4 => 'error'
    ])
    ->setSearch(true);
```

**Badge Types:**
- `success` - Green badge
- `processing` - Blue badge (animated)
- `warning` - Orange badge
- `error` - Red badge
- `default` - Gray badge

### 3. Date Column

Date/time column with date range search.

```php
// Basic date column
$container->date('create_time', '创建时间');

// With date range search
$container->date('create_time', '创建时间')
    ->setSearch(true)
    ->setSearchType('between')
    ->setFormat('Y-m-d H:i:s');

// DateTime column
$container->date('publish_time', '发布时间')
    ->setSearch(true)
    ->setSearchType('between')
    ->setFormat('Y-m-d H:i:s')
    ->setWidth(180);

// Multiple date columns
$container->date('start_date', '开始日期')
    ->setSearch(true)
    ->setSearchType('between')
    ->setFormat('Y-m-d')
    ->setWidth(150);

$container->date('end_date', '结束日期')
    ->setSearch(true)
    ->setSearchType('between')
    ->setFormat('Y-m-d')
    ->setWidth(150);
```

**Date Formats:**
- `Y-m-d` - 2024-01-15
- `Y-m-d H:i:s` - 2024-01-15 14:30:00
- `H:i:s` - 14:30:00
- `Y年m月d日` - 2024年01月15日

### 4. Image Column

Display single or multiple images.

```php
// Basic image column
$container->image('cover', '封面');

// With dimensions
$container->image('cover', '封面')
    ->setWidth(100)
    ->setHeight(60);

// Multiple images column
$container->image('images', '图片集')
    ->setWidth(120)
    ->setHeight(80);

// Conditional display
$container->image('avatar', '头像')
    ->setWidth(60)
    ->setHeight(60)
    ->setShowCondition('status', 'neq', 0);  // Hide if status = 0
```

### 5. Action Column

Action buttons for row operations.

```php
// Basic action column
$container->action('', '操作')
    ->setParams(['id' => 'id'])
    ->actions(function ($actions) {
        $actions->edit();
        $actions->delete();
    });

// With modal edit
$container->action('', '操作')
    ->setParams(['id' => 'id'])
    ->actions(function ($actions) {
        $actions->edit()
            ->modal((new \Qscmf\Lib\AntdAdmin\Layouts\FormBuilder\Modal())
                ->setWidth('800px')
                ->setUrl(U('edit', ['id' => '__id__']))
                ->setTitle('编辑商品'));
    });

// Custom action buttons
$container->action('', '操作')
    ->setParams(['id' => 'id'])
    ->actions(function ($actions) {
        $actions->link('查看详情', 'detail', [
            'href' => U('detail', ['id' => '__id__'])
        ]);

        $actions->link('审核', 'audit', [
            'href' => U('audit', ['id' => '__id__']),
            'confirm' => '确定要审核通过吗？'
        ]);

        $actions->delete();
    });

// Conditional actions
$container->action('', '操作')
    ->setParams(['id' => 'id', 'status' => 'status'])
    ->actions(function ($actions) {
        $actions->edit();

        // Show forbid only when status = 1
        $actions->link('禁用', 'forbid', [
            'showCondition' => ['status' => 1],
            'href' => U('forbid', ['id' => '__id__']),
            'confirm' => '确定要禁用吗？'
        ]);

        // Show resume only when status = 0
        $actions->link('启用', 'resume', [
            'showCondition' => ['status' => 0],
            'href' => U('resume', ['id' => '__id__'])
        ]);
    });
```

**Action Types:**
- `edit()` - Edit button (opens modal or page)
- `delete()` - Delete button with confirmation
- `link()` - Custom link button
- `ajax()` - AJAX action button

### 6. Custom Column

Custom renderer with React components.

```php
// Simple custom renderer
$container->custom('status', '状态')
    ->setRenderer(function($value, $row) {
        $statusMap = [1 => '启用', 0 => '禁用'];
        return $statusMap[$value] ?? '未知';
    });

// Custom renderer with React Badge
$container->custom('status', '状态')
    ->setRenderer(function($value, $row) {
        return \Qscmf\Lib\AntdAdmin\React::render('Badge', [
            'status' => $value === 1 ? 'success' : 'default',
            'text' => $value === 1 ? '启用' : '禁用'
        ]);
    });

// Complex custom renderer
$container->custom('user_id', '用户')
    ->setRenderer(function($user_id, $row) {
        $user = D('User')->find($user_id);
        if (!$user) {
            return '未知用户';
        }

        return \Qscmf\Lib\AntdAdmin\React::render('UserCard', [
            'username' => $user['username'],
            'avatar' => $user['avatar'],
            'email' => $user['email']
        ]);
    });

// Custom renderer with conditional display
$container->custom('stock', '库存')
    ->setRenderer(function($stock, $row) {
        if ($stock <= 10) {
            return \Qscmf\Lib\AntdAdmin\React::render('Tag', [
                'color' => 'red',
                'text' => "库存紧张: {$stock}"
            ]);
        } elseif ($stock <= 50) {
            return \Qscmf\Lib\AntdAdmin\React::render('Tag', [
                'color' => 'orange',
                'text' => $stock
            ]);
        } else {
            return \Qscmf\Lib\AntdAdmin\React::render('Tag', [
                'color' => 'green',
                'text' => $stock
            ]);
        }
    });

// Custom renderer with search
$container->custom('full_name', '全名')
    ->setRenderer(function($value, $row) {
        return $row['first_name'] . ' ' . $row['last_name'];
    })
    ->setSearch(true)
    ->setSearchType('like');
```

---

## Advanced Features

### Inline Editing

Enable inline editing for columns.

```php
// Basic inline edit
$container->text('title', '标题')
    ->editable();

// Inline edit with validation
$container->number('price', '价格')
    ->editable()
    ->setMin(0)
    ->setMax(999999);

// Inline edit with async save
$container->text('name', '名称')
    ->editable()
    ->setSaveUrl(U('ajaxSave'));

// Conditional inline edit
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList())
    ->editable()
    ->setShowCondition('can_edit', 'eq', 1);
```

### Batch Actions

Configure batch operations.

```php
// Enable batch actions
$container->setBatchActions([
    'delete' => '批量删除',
    'enable' => '批量启用',
    'disable' => '批量禁用'
]);

// Batch action with custom handler
$container->setBatchActions([
    'audit' => '批量审核',
    'export' => '导出数据'
]);

// Batch action handler (in controller)
public function batchAudit()
{
    $ids = I('post.ids');
    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    $result = D('Product')->where(['id' => ['in', $ids]])->setField('audit_status', 1);

    $this->success("成功审核 {$result} 条记录");
}
```

### Async Data Loading

Load select options asynchronously.

```php
// Async select options
$container->select('user_id', '用户')
    ->setAsync(true)
    ->setAsyncUrl(U('Api/User/getOptions'))
    ->setSearch(true);

// Async with custom parameters
$container->select('tag_id', '标签')
    ->setAsync(true)
    ->setAsyncUrl(U('Api/Tag/search'))
    ->setAsyncParams([
        'type' => 'product',
        'status' => 1
    ]);
```

### Advanced Filters

Configure complex filter conditions.

```php
// Set advanced filter
$container->setAdvancedFilter([
    'status' => [
        'type' => 'select',
        'options' => DBCont::getStatusList(),
        'default' => 1
    ],
    'date_range' => [
        'type' => 'between',
        'field' => 'create_time'
    ],
    'price_range' => [
        'type' => 'between',
        'field' => 'price'
    ]
]);
```

---

## Complete Working Examples

### Example 1: Product List (v14)

```php
<?php
// app/Admin/Controller/ProductController.class.php

class ProductController extends \Qscmf\Lib\AntdAdmin\AdminController
{
    protected function buildTableColumns($container)
    {
        // ID column with sorting
        $container->text('id', 'ID')
            ->setSortable(true)
            ->setWidth(80);

        // Product name with search
        $container->text('name', '商品名称')
            ->setSearch(true)
            ->setSearchType('like')
            ->setSearchPlaceholder('搜索商品名称')
            ->setSortable(true)
            ->setWidth(200)
            ->setEllipsis(true);

        // Category with search
        $container->select('cate_id', '分类')
            ->setValueEnum(D('Category')->getFields())
            ->setSearch(true)
            ->setSearchType('exact')
            ->setWidth(120);

        // Cover image
        $container->image('cover', '封面')
            ->setWidth(100)
            ->setHeight(60);

        // Price with inline edit
        $container->number('price', '价格')
            ->setSearch(true)
            ->setSearchType('between')
            ->setSortable(true)
            ->setMin(0)
            ->setMax(999999)
            ->setWidth(100)
            ->editable();

        // Stock with inline edit
        $container->number('stock', '库存')
            ->setSearch(true)
            ->setSearchType('between')
            ->setSortable(true)
            ->setWidth(100)
            ->editable();

        // Status with badge
        $container->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList())
            ->setBadge([1 => 'success', 0 => 'default'])
            ->setSearch(true)
            ->setSearchType('exact')
            ->setWidth(100);

        // Sort with inline edit
        $container->number('sort', '排序')
            ->setSortable(true)
            ->setWidth(80)
            ->editable();

        // Create time with range search
        $container->date('create_time', '创建时间')
            ->setSearch(true)
            ->setSearchType('between')
            ->setFormat('Y-m-d H:i:s')
            ->setWidth(180);

        // Action column
        $container->action('', '操作')
            ->setParams(['id' => 'id'])
            ->setWidth(150)
            ->actions(function ($actions) {
                $actions->edit()
                    ->modal((new \Qscmf\Lib\AntdAdmin\Layouts\FormBuilder\Modal())
                        ->setWidth('800px')
                        ->setUrl(U('edit', ['id' => '__id__']))
                        ->setTitle('编辑商品'));

                $actions->delete();
            });
    }

    public function index()
    {
        $container = new \Qscmf\Lib\AntdAdmin\Layouts\Table\TableContainer();
        $this->buildTableColumns($container);

        // Configure data source
        $container->setDataSource(U('getListData'));

        // Enable pagination
        $container->setPagination([
            'pageSize' => 20,
            'showSizeChanger' => true,
            'showTotal' => function($total) {
                return "共 {$total} 条";
            }
        ]);

        return $this->display($container);
    }
}
```

### Example 2: Order List with Custom Renderers

```php
protected function buildTableColumns($container)
{
    // Order number
    $container->text('order_no', '订单号')
        ->setSearch(true)
        ->setSearchType('like')
        ->setWidth(180);

    // User info with custom renderer
    $container->custom('user_id', '用户')
        ->setRenderer(function($user_id, $row) {
            $user = D('User')->find($user_id);
            if (!$user) {
                return '未知用户';
            }

            return \Qscmf\Lib\AntdAdmin\React::render('UserDisplay', [
                'avatar' => $user['avatar'],
                'name' => $user['username'],
                'mobile' => $user['mobile']
            ]);
        })
        ->setWidth(150);

    // Amount with custom formatting
    $container->custom('total_amount', '金额')
        ->setRenderer(function($amount, $row) {
            return \Qscmf\Lib\AntdAdmin\React::render('Money', [
                'amount' => $amount,
                'currency' => 'CNY',
                'color' => 'red'
            ]);
        })
        ->setSearch(true)
        ->setSearchType('between')
        ->setSortable(true)
        ->setWidth(120);

    // Order status with badge
    $container->select('order_status', '订单状态')
        ->setValueEnum([
            0 => '待付款',
            1 => '已付款',
            2 => '已发货',
            3 => '已完成',
            4 => '已取消'
        ])
        ->setBadge([
            0 => 'default',
            1 => 'processing',
            2 => 'warning',
            3 => 'success',
            4 => 'error'
        ])
        ->setSearch(true)
        ->setSearchType('exact')
        ->setWidth(100);

    // Payment status with conditional badge
    $container->custom('pay_status', '支付状态')
        ->setRenderer(function($status, $row) {
            $map = [
                0 => ['text' => '未支付', 'color' => 'default'],
                1 => ['text' => '已支付', 'color' => 'success'],
                2 => ['text' => '支付失败', 'color' => 'error']
            ];

            $info = $map[$status] ?? ['text' => '未知', 'color' => 'default'];

            return \Qscmf\Lib\AntdAdmin\React::render('Badge', [
                'status' => $info['color'],
                'text' => $info['text']
            ]);
        })
        ->setSearch(true)
        ->setWidth(100);

    // Create time
    $container->date('create_time', '下单时间')
        ->setSearch(true)
        ->setSearchType('between')
        ->setFormat('Y-m-d H:i:s')
        ->setSortable(true)
        ->setWidth(180);

    // Action column with conditional buttons
    $container->action('', '操作')
        ->setParams(['id' => 'id', 'order_status' => 'order_status'])
        ->setWidth(200)
        ->actions(function ($actions) {
            // View detail - always show
            $actions->link('查看详情', 'detail', [
                'href' => U('detail', ['id' => '__id__'])
            ]);

            // Edit - only for unpaid orders
            $actions->edit()
                ->showCondition(['order_status' => 0])
                ->modal((new \Qscmf\Lib\AntdAdmin\Layouts\FormBuilder\Modal())
                    ->setWidth('800px')
                    ->setUrl(U('edit', ['id' => '__id__']))
                    ->setTitle('编辑订单'));

            // Ship - only for paid but unshipped
            $actions->link('发货', 'ship', [
                'showCondition' => ['order_status' => 1],
                'href' => U('ship', ['id' => '__id__']),
                'confirm' => '确定要发货吗？'
            ]);

            // Cancel - only for unpaid
            $actions->link('取消', 'cancel', [
                'showCondition' => ['order_status' => 0],
                'href' => U('cancel', ['id' => '__id__']),
                'confirm' => '确定要取消订单吗？'
            ]);

            $actions->delete();
        });
}
```

### Example 3: User List with Async Data

```php
protected function buildTableColumns($container)
{
    // Avatar
    $container->image('avatar', '头像')
        ->setWidth(60)
        ->setHeight(60);

    // Username
    $container->text('username', '用户名')
        ->setSearch(true)
        ->setSearchType('like')
        ->setSortable(true)
        ->setWidth(150);

    // Email
    $container->text('email', '邮箱')
        ->setSearch(true)
        ->setSearchType('like')
        ->setWidth(200);

    // Mobile
    $container->text('mobile', '手机号')
        ->setSearch(true)
        ->setSearchType('exact')
        ->setWidth(120);

    // Role with async loading
    $container->select('role_id', '角色')
        ->setAsync(true)
        ->setAsyncUrl(U('Api/Role/getOptions'))
        ->setSearch(true)
        ->setSearchType('exact')
        ->setWidth(120);

    // Status with badge and inline edit
    $container->select('status', '状态')
        ->setValueEnum(DBCont::getStatusList())
        ->setBadge([1 => 'success', 0 => 'default'])
        ->setSearch(true)
        ->setSearchType('exact')
        ->setWidth(100)
        ->editable();

    // Last login time
    $container->date('last_login_time', '最后登录')
        ->setSearch(true)
        ->setSearchType('between')
        ->setFormat('Y-m-d H:i:s')
        ->setSortable(true)
        ->setWidth(180);

    // Action column
    $container->action('', '操作')
        ->setParams(['id' => 'id'])
        ->setWidth(200)
        ->actions(function ($actions) {
            $actions->link('重置密码', 'resetPassword', [
                'href' => U('resetPassword', ['id' => '__id__']),
                'confirm' => '确定要重置密码吗？'
            ]);

            $actions->edit();
            $actions->delete();
        });
}
```

---

## Configuration Methods Reference

### setSearch

Enable or disable search input for the column.

```php
->setSearch(true)   // Enable search
->setSearch(false)  // Disable search
```

### setSearchType

Set the search type.

```php
->setSearchType('like')    // Fuzzy search (for text)
->setSearchType('exact')   // Exact match (for select, number)
->setSearchType('between') // Range search (for date, number)
```

### setSearchPlaceholder

Set placeholder text for search input.

```php
->setSearchPlaceholder('请输入商品名称')
```

### setSearchDefault

Set default search value.

```php
->setSearchDefault('默认值')
```

### setSortable

Enable or disable column sorting.

```php
->setSortable(true)   // Enable sorting
->setSortable(false)  // Disable sorting
```

### setWidth

Set column width.

```php
->setWidth(100)       // Pixel width
->setWidth('10%')     // Percentage width
```

### setEllipsis

Enable text overflow with ellipsis.

```php
->setEllipsis(true)   // Enable ellipsis
->setEllipsis(false)  // Disable ellipsis
```

### setShowCondition

Set conditional display for column or action.

```php
// Show only when field matches value
->setShowCondition('status', 'eq', 1)     // status == 1
->setShowCondition('status', 'neq', 0)    // status != 0
->setShowCondition('price', 'gt', 100)    // price > 100
->setShowCondition('stock', 'lt', 10)     // stock < 10

// Operators: eq, neq, gt, lt, gte, lte, in, not_in
```

### setValueEnum

Set enum value mapping for select columns.

```php
->setValueEnum([
    1 => '启用',
    0 => '禁用'
])
```

### setBadge

Set badge color mapping for status columns.

```php
->setBadge([
    1 => 'success',    // Green
    2 => 'processing', // Blue
    3 => 'warning',    // Orange
    0 => 'error',      // Red
    -1 => 'default'    // Gray
])
```

### setRenderer

Set custom renderer function.

```php
->setRenderer(function($value, $row) {
    // $value: Current field value
    // $row: Complete row data array
    return 'Custom HTML or React component';
})
```

### setFormat

Set date/time format.

```php
->setFormat('Y-m-d H:i:s')
->setFormat('Y-m-d')
->setFormat('H:i:s')
```

### setHeight

Set image height.

```php
->setHeight(60)
```

### setParams

Set parameters for action column.

```php
->setParams(['id' => 'id', 'status' => 'status'])
```

### actions

Configure action buttons.

```php
->actions(function ($actions) {
    $actions->edit();
    $actions->delete();
    $actions->link('Custom', 'action', ['href' => '...']);
})
```

### editable

Enable inline editing.

```php
->editable()
```

---

## Version Differences

### v13 vs v14

| Feature | v13 (Legacy) | v14 (Modern) |
|---------|--------------|--------------|
| **API** | `addTableColumn()` | `text()`, `select()`, `date()` methods |
| **UI Framework** | jQuery 1.x | React + AntdAdmin |
| **Custom Renderer** | `'fun'` type with callback | `setRenderer()` with React components |
| **Inline Edit** | `@save=true` metadata | `editable()` method |
| **Search Types** | Limited types | Extended with like/exact/between modes |
| **Status Display** | Pass array to `addTableColumn()` | `setValueEnum()` + `setBadge()` |
| **Action Buttons** | `addRightButton()` | `actions()` closure |
| **Async Data** | Not supported | `setAsync()` + `setAsyncUrl()` |
| **Performance** | DOM manipulation | Virtual DOM, better performance |

### Migration Example

```php
// v13 (Legacy)
$builder->addTableColumn('name', '名称');
$builder->addTableColumn('status', '状态', DBCont::getStatusList());
$builder->addTableColumn('create_time', '创建时间');

// v14 (Modern)
$container->text('name', '名称')
    ->setSearch(true)
    ->setSearchType('like');

$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList())
    ->setBadge([1 => 'success', 0 => 'default'])
    ->setSearch(true);

$container->date('create_time', '创建时间')
    ->setSearch(true)
    ->setSearchType('between');
```

---

## Related Rules

- [Table Columns v13](./crud-table-columns-v13.md) - Legacy ListBuilder API
- [Form Validation](./crud-form-validation.md) - Field validation rules
- [Search Configuration](./crud-search-basic.md) - Advanced search patterns
- [Custom Components](./crud-custom-components.md) - React custom renderers

---

## Best Practices

1. **Always enable search for key columns** - Use `setSearch(true)` on name, code, status fields
2. **Use badges for status** - `setBadge()` makes status more visual
3. **Set appropriate column widths** - Prevent layout issues with `setWidth()`
4. **Use ellipsis for long text** - `setEllipsis(true)` improves readability
5. **Leverage inline editing** - Use `editable()` for frequently updated fields
6. **Use conditional display** - `setShowCondition()` reduces UI clutter
7. **Custom renderers for complex data** - Use `setRenderer()` instead of modifying templates
8. **Async loading for large datasets** - `setAsyncUrl()` improves performance
9. **Date range search** - Use `setSearchType('between')` for dates
10. **Keep action buttons concise** - Limit to 3-4 actions per row

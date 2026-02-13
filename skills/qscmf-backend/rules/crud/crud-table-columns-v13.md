---
title: Table Columns Configuration (v13 - ListBuilder)
impact: HIGH
impactDescription: Core CRUD UI component (30% daily usage)
tags: crud, table, columns, legacy, v13, listbuilder
---

## Table Columns Configuration (v13 - ListBuilder)

Complete reference for configuring table columns using the legacy ListBuilder API (jQuery-based) in QSCMF v13.

### When to Use This Rule

- You are working on a QSCMF v13 project
- You need to configure table columns in an Admin controller
- You want to add search functionality to your list page
- You need to add action buttons (top buttons or row buttons)
- You are maintaining or updating legacy CRUD code

---

## Complete Method Reference

### ListBuilder Public Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `addTableColumn()` | `$name, $title, $type = 'text', $options = []` | ListBuilder | Add a table column |
| `addSearchItem()` | `$name, $type, $title, $default = '', $options = []` | ListBuilder | Add a search form item |
| `addTopButton()` | `$type, $options = []` | ListBuilder | Add a toolbar button |
| `addRightButton()` | `$type, $options = []` | ListBuilder | Add a row action button |
| `setCheckBox()` | `$enable = true` | ListBuilder | Enable checkbox for batch operations |
| `setPageTemplate()` | `$template` | ListBuilder | Set custom page template |
| `setSearchUrl()` | `$url` | ListBuilder | Set custom search action URL |
| `setLockRow()` | `$fields` | ListBuilder | Lock specified rows from editing |
| `setLockCol()` | `$fields` | ListBuilder | Lock specified columns from editing |
| `setMetaTitle()` | `$title` | ListBuilder | Set page meta title |
| `setTableName()` | `$name` | ListBuilder | Set table name for data |
| `setAjaxUrl()` | `$url` | ListBuilder | Set AJAX data URL |
| `setKey()` | `$key` | ListBuilder | Set primary key field |
| `build()` | - | string | Build and return HTML output |

---

## Table Column Types

ListBuilder supports 15+ column types via `addTableColumn()`:

### 1. Text Column (Default)

Basic text display column.

```php
$builder = new \Qscmf\Builder\ListBuilder();

// Simple text column
$builder->addTableColumn('id', 'ID');
$builder->addTableColumn('name', '名称');
$builder->addTableColumn('email', '邮箱');
```

### 2. Status Column

Display status with enum value mapping.

```php
$builder->addTableColumn('status', '状态', DBCont::getStatusList());
// Output: 1 → "启用", 0 → "禁用"

// Custom status mapping
$builder->addTableColumn('audit_status', '审核状态', [
    0 => '待审核',
    1 => '已通过',
    2 => '已拒绝'
]);
```

**DBCont Common Lists:**
- `DBCont::getStatusList()` - [1 => '启用', 0 => '禁用']
- `DBCont::getBoolStatusList()` - [1 => '是', 0 => '否']

### 3. Date Column

Auto-format date values.

```php
$builder->addTableColumn('create_time', '创建时间');
$builder->addTableColumn('update_time', '更新时间');
$builder->addTableColumn('publish_date', '发布日期');
```

**Format:** Auto-detected from field name or use 'date' type.

### 4. Time Column

Display time values.

```php
$builder->addTableColumn('start_time', '开始时间', 'time');
$builder->addTableColumn('end_time', '结束时间', 'time');
```

### 5. Picture Column

Display single image with thumbnail.

```php
$builder->addTableColumn('cover', '封面图', 'picture');
$builder->addTableColumn('avatar', '头像', 'picture');

// With custom width/height
$builder->addTableColumn('cover', '封面', 'picture', [
    'width' => 100,
    'height' => 60
]);
```

### 6. Pictures Column

Display multiple images.

```php
$builder->addTableColumn('images', '图片集', 'pictures');
$builder->addTableColumn('gallery', '相册', 'pictures');
```

### 7. Icon Column

Display icon (from icon class).

```php
$builder->addTableColumn('icon', '图标', 'icon');
```

### 8. Type Column

Display mapped type values.

```php
$type_list = [
    1 => '普通商品',
    2 => '虚拟商品',
    3 => '服务商品'
];

$builder->addTableColumn('type', '商品类型', $type_list);
```

### 9. Number (num) Column

Display formatted number.

```php
$builder->addTableColumn('sort', '排序', 'num');
$builder->addTableColumn('price', '价格', 'num');
$builder->addTableColumn('stock', '库存', 'num');
```

### 10. Checkbox Column

Display boolean as checkbox icon.

```php
$builder->addTableColumn('is_recommend', '推荐', 'checkbox');
$builder->addTableColumn('is_hot', '热门', 'checkbox');
$builder->addTableColumn('is_new', '新品', 'checkbox');
```

### 11. Select Column

Display mapped value from foreign key or options.

```php
// Get categories from database
$cate_list = D('Category')->getFields();

$builder->addTableColumn('cate_id', '分类', $cate_list);

// Or with explicit options
$status_list = [1 => '正常', 2 => '冻结', 3 => '关闭'];
$builder->addTableColumn('account_status', '账户状态', $status_list);
```

### 12. Select2 Column

Enhanced select with search functionality.

```php
$tag_list = D('Tag')->select();
$builder->addTableColumn('tag_id', '标签', $tag_list, 'select2');
```

### 13. Textarea Column

Display long text content.

```php
$builder->addTableColumn('summary', '摘要', 'textarea');
$builder->addTableColumn('description', '描述', 'textarea');
```

### 14. Link (a) Column

Display as clickable link.

```php
$builder->addTableColumn('url', '链接', 'a');

// With custom link title
$builder->addTableColumn('website', '官网', 'a', [
    'title_field' => 'name'
]);
```

### 15. Self Column

Display self-referencing data (e.g., parent category).

```php
$builder->addTableColumn('parent_id', '父级', 'self');
```

### 16. Custom Function (fun) Column

Display custom rendered content using callback.

```php
$builder->addTableColumn('custom', '自定义', 'fun', function($value, $row) {
    // $value: Current field value
    // $row: Complete row data array

    return sprintf(
        '<span class="badge">%s</span>',
        $value
    );
});

// Complex example: Display related data
$builder->addTableColumn('user_id', '用户', 'fun', function($user_id, $row) {
    $user = D('User')->find($user_id);
    return $user ? $user['username'] : '未知';
});

// Conditional display
$builder->addTableColumn('status', '状态', 'fun', function($status, $row) {
    $color_map = [1 => 'green', 0 => 'red'];
    $text_map = [1 => '启用', 0 => '禁用'];

    return sprintf(
        '<span style="color: %s">%s</span>',
        $color_map[$status],
        $text_map[$status]
    );
});
```

---

## Search Types

Add search form items using `addSearchItem()`:

### Search Type Parameters

```php
$builder->addSearchItem(
    $name,      // Field name
    $type,      // Search type: text, select, date, time, datetime, between, checkbox
    $title,     // Display label
    $default,   // Default value (optional)
    $options    // Additional options (optional)
);
```

### 1. Text Search

Simple keyword search input.

```php
$builder->addSearchItem('keyword', 'text', '搜索关键词');

// Search across multiple fields (in controller)
$map = [];
if ($keyword = I('get.keyword')) {
    $map['title'] = ['like', '%' . $keyword . '%'];
}
```

### 2. Select Search

Dropdown select search.

```php
$builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());

// With custom options
$cate_list = D('Category')->select();
$builder->addSearchItem('cate_id', 'select', '分类', '', $cate_list);

// With default selected value
$builder->addSearchItem('type', 'select', '类型', '1', [
    1 => '类型一',
    2 => '类型二',
    3 => '类型三'
]);
```

### 3. Date Search

Date picker search.

```php
$builder->addSearchItem('create_date', 'date', '创建时间');
$builder->addSearchItem('publish_date', 'date', '发布日期');
```

### 4. Time Search

Time picker search.

```php
$builder->addSearchItem('start_time', 'time', '开始时间');
$builder->addSearchItem('end_time', 'time', '结束时间');
```

### 5. DateTime Search

DateTime picker search.

```php
$builder->addSearchItem('publish_time', 'datetime', '发布时间');
```

### 6. Between Search

Range search (for dates or numbers).

```php
// Date range
$builder->addSearchItem('create_time', 'between', '创建时间');

// Price range
$builder->addSearchItem('price', 'between', '价格范围');

// Usage in controller:
if ($start_time = I('get.create_time_start')) {
    $map['create_time'][] = ['egt', strtotime($start_time)];
}
if ($end_time = I('get.create_time_end')) {
    $map['create_time'][] = ['elt', strtotime($end_time)];
}
```

### 7. Checkbox Search

Multi-select checkbox search.

```php
$options = [
    1 => '咨询',
    2 => '研发',
    3 => '设计',
    4 => '测试'
];

$builder->addSearchItem('business_type', 'checkbox', '业务类型', '', $options);
```

---

## Button Types

### Top Buttons (Toolbar Buttons)

Add buttons above the table using `addTopButton()`:

#### 1. Add New Button

```php
$builder->addTopButton('addnew');

// With custom title
$builder->addTopButton('addnew', [
    'title' => '新增用户'
]);

// With custom URL
$builder->addTopButton('addnew', [
    'title' => '新增',
    'href' => U('Admin/User/create')
]);
```

#### 2. Forbid/Disable Button

Batch disable selected records.

```php
$builder->addTopButton('forbid');

// With custom config
$builder->addTopButton('forbid', [
    'title' => '禁用',
    'confirm' => '确定要禁用选中的记录吗？',
    'url' => U('setStatus', ['status' => 0])
]);
```

#### 3. Resume/Enable Button

Batch enable selected records.

```php
$builder->addTopButton('resume');

// With custom config
$builder->addTopButton('resume', [
    'title' => '启用',
    'confirm' => '确定要启用选中的记录吗？',
    'url' => U('setStatus', ['status' => 1])
]);
```

#### 4. Delete Button

Batch delete selected records.

```php
$builder->addTopButton('delete');

// With custom config
$builder->addTopButton('delete', [
    'title' => '删除',
    'confirm' => '确定要删除选中的记录吗？此操作不可恢复！',
    'url' => U('batchDelete')
]);
```

#### 5. Custom Button

Create custom action button.

```php
$builder->addTopButton('custom', [
    'title' => '导出',
    'href' => U('export'),
    'icon' => 'fa fa-download',
    'class' => 'btn btn-success'
]);

// Custom AJAX button
$builder->addTopButton('custom', [
    'title' => '批量审核',
    'href' => U('batchAudit'),
    'ajax' => true,
    'confirm' => '确定要批量审核通过吗？'
]);
```

### Right Buttons (Row Action Buttons)

Add action buttons for each row using `addRightButton()`:

#### 1. Edit Button

```php
$builder->addRightButton('edit');

// With custom title
$builder->addRightButton('edit', [
    'title' => '编辑'
]);

// With custom URL
$builder->addRightButton('edit', [
    'title' => '编辑',
    'href' => U('edit', ['id' => '__id__'])
]);
```

#### 2. Delete Button

```php
$builder->addRightButton('delete');

// With custom config
$builder->addRightButton('delete', [
    'title' => '删除',
    'confirm' => '确定要删除吗？',
    'url' => U('delete', ['id' => '__id__'])
]);
```

#### 3. Forbid Button (Row-level)

```php
$builder->addRightButton('forbid');

// Conditional display (only if status == 1)
$builder->addRightButton('forbid', [
    'title' => '禁用',
    'showCondition' => [
        'field' => 'status',
        'operator' => 'eq',
        'value' => 1
    ]
]);
```

#### 4. Resume Button (Row-level)

```php
$builder->addRightButton('resume');

// Conditional display (only if status == 0)
$builder->addRightButton('resume', [
    'title' => '启用',
    'showCondition' => [
        'field' => 'status',
        'operator' => 'eq',
        'value' => 0
    ]
]);
```

#### 5. Custom Button

```php
$builder->addRightButton('custom', [
    'title' => '审核',
    'href' => U('audit', ['id' => '__id__']),
    'icon' => 'fa fa-check'
]);

// Custom AJAX button
$builder->addRightButton('custom', [
    'title' => '重置密码',
    'href' => U('resetPassword', ['id' => '__id__']),
    'ajax' => true,
    'confirm' => '确定要重置密码吗？'
]);
```

**Special Placeholders:**
- `__id__` - Primary key value
- `__row__` - Complete row data array

---

## Complete Working Examples

### Example 1: Basic Product List

```php
<?php
// app/Admin/Controller/ProductController.class.php

class ProductController extends QsListController
{
    protected function buildListOptions($builder)
    {
        // Set page title
        $builder->setMetaTitle('商品列表');

        // Top toolbar buttons
        $builder->addTopButton('addnew');
        $builder->addTopButton('forbid');
        $builder->addTopButton('resume');
        $builder->addTopButton('delete');

        // Search form
        $builder->addSearchItem('keyword', 'text', '搜索');
        $builder->addSearchItem('cate_id', 'select', '分类', '', D('Category')->getFields());
        $builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());
        $builder->addSearchItem('create_time', 'between', '创建时间');

        // Table columns
        $builder->addTableColumn('id', 'ID')
            ->setSortOrder('asc');

        $builder->addTableColumn('name', '商品名称');

        $builder->addTableColumn('cate_id', '分类', D('Category')->getFields());

        $builder->addTableColumn('cover', '封面图', 'picture');

        $builder->addTableColumn('price', '价格', 'num');

        $builder->addTableColumn('stock', '库存', 'num');

        $builder->addTableColumn('is_recommend', '推荐', 'checkbox');

        $builder->addTableColumn('is_hot', '热门', 'checkbox');

        $builder->addTableColumn('status', '状态', DBCont::getStatusList());

        $builder->addTableColumn('sort', '排序', 'num');

        $builder->addTableColumn('create_time', '创建时间');

        // Row action buttons
        $builder->addRightButton('edit');
        $builder->addRightButton('delete');

        return $builder;
    }

    public function index()
    {
        $builder = new \Qscmf\Builder\ListBuilder(
            $this,
            [$this, 'buildListOptions'],
            $this->buildSearchMap()
        );

        return $this->display($builder);
    }

    protected function buildSearchMap()
    {
        $map = [];

        // Keyword search
        if ($keyword = I('get.keyword')) {
            $map['name'] = ['like', '%' . $keyword . '%'];
        }

        // Category filter
        if ($cate_id = I('get.cate_id')) {
            $map['cate_id'] = $cate_id;
        }

        // Status filter
        if ($status = I('get.status') !== '') {
            $map['status'] = $status;
        }

        // Date range
        if ($start_time = I('get.create_time_start')) {
            $map['create_time'][] = ['egt', strtotime($start_time)];
        }
        if ($end_time = I('get.create_time_end')) {
            $map['create_time'][] = ['elt', strtotime($end_time)];
        }

        return $map;
    }
}
```

### Example 2: Advanced Custom Renderer

```php
protected function buildListOptions($builder)
{
    $builder->setMetaTitle('订单列表');

    $builder->addTopButton('addnew');

    // Search
    $builder->addSearchItem('order_no', 'text', '订单号');
    $builder->addSearchItem('status', 'select', '状态', '', [
        0 => '待付款',
        1 => '已付款',
        2 => '已发货',
        3 => '已完成',
        4 => '已取消'
    ]);

    // Columns
    $builder->addTableColumn('id', 'ID');

    $builder->addTableColumn('order_no', '订单号');

    // Custom renderer for user info
    $builder->addTableColumn('user_id', '用户', 'fun', function($user_id, $row) {
        $user = D('User')->find($user_id);
        if ($user) {
            return sprintf(
                '<div>%s</div><div class="text-muted">%s</div>',
                $user['username'],
                $user['mobile']
            );
        }
        return '未知用户';
    });

    // Custom renderer for amount
    $builder->addTableColumn('total_amount', '金额', 'fun', function($amount, $row) {
        return sprintf('<span class="text-danger">¥%.2f</span>', $amount);
    });

    // Status with color
    $builder->addTableColumn('status', '状态', 'fun', function($status, $row) {
        $status_map = [
            0 => ['text' => '待付款', 'color' => 'gray'],
            1 => ['text' => '已付款', 'color' => 'blue'],
            2 => ['text' => '已发货', 'color' => 'orange'],
            3 => ['text' => '已完成', 'color' => 'green'],
            4 => ['text' => '已取消', 'color' => 'red']
        ];

        $info = $status_map[$status] ?? ['text' => '未知', 'color' => 'gray'];

        return sprintf(
            '<span class="label label-%s">%s</span>',
            $info['color'],
            $info['text']
        );
    });

    $builder->addTableColumn('create_time', '创建时间');

    // Action buttons
    $builder->addRightButton('edit');

    // Custom action button
    $builder->addRightButton('custom', [
        'title' => '查看详情',
        'href' => U('detail', ['id' => '__id__']),
        'icon' => 'fa fa-eye'
    ]);

    return $builder;
}
```

### Example 3: Permission-based Button Display

```php
protected function buildListOptions($builder)
{
    $builder->setMetaTitle('用户管理');

    // Check admin permission
    if (is_admin()) {
        $builder->addTopButton('addnew');
        $builder->addTopButton('delete');
    }

    // Columns
    $builder->addTableColumn('id', 'ID');
    $builder->addTableColumn('username', '用户名');
    $builder->addTableColumn('email', '邮箱');
    $builder->addTableColumn('status', '状态', DBCont::getStatusList());

    // Conditional right buttons based on status
    $builder->addRightButton('edit');

    // Show forbid button only for active users
    $builder->addRightButton('forbid', [
        'title' => '禁用',
        'showCondition' => [
            'field' => 'status',
            'operator' => 'eq',
            'value' => 1
        ]
    ]);

    // Show resume button only for disabled users
    $builder->addRightButton('resume', [
        'title' => '启用',
        'showCondition' => [
            'field' => 'status',
            'operator' => 'eq',
            'value' => 0
        ]
    ]);

    // Only show delete button for admins
    if (is_admin()) {
        $builder->addRightButton('delete');
    }

    return $builder;
}
```

---

## Configuration Methods

### setCheckBox

Enable checkbox column for batch operations.

```php
$builder->setCheckBox(true);

// Batch operation handler (in controller)
public function batchForbid()
{
    $ids = I('post.ids');
    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    $map['id'] = ['in', $ids];
    D('Product')->where($map)->setField('status', 0);

    $this->success('操作成功');
}
```

### setPageTemplate

Use custom list page template.

```php
$builder->setPageTemplate('custom_product_list');
// Template: app/Admin/View/custom_product_list.html
```

### setSearchUrl

Set custom search form action URL.

```php
$builder->setSearchUrl(U('Admin/Product/customSearch'));
```

### setLockRow

Prevent editing of specific rows.

```php
// Lock system records from editing
$builder->setLockRow(['id' => [1, 2, 3]]);
```

### setLockCol

Lock specific columns from inline editing.

```php
// Lock id and status columns
$builder->setLockCol(['id', 'status']);
```

### setMetaTitle

Set page title and browser title.

```php
$builder->setMetaTitle('商品管理列表');
```

### setTableName

Override the default table name.

```php
$builder->setTableName('qs_product');
```

### setAjaxUrl

Set custom AJAX data URL.

```php
$builder->setAjaxUrl(U('Admin/Product/getListData'));
```

### setKey

Set primary key field (default: 'id').

```php
$builder->setKey('product_id');
```

---

## Common Patterns

### Pattern 1: Self-Referencing Categories

```php
protected function buildListOptions($builder)
{
    $builder->setMetaTitle('分类管理');

    $builder->addTopButton('addnew');

    // Columns with parent self-reference
    $builder->addTableColumn('id', 'ID');
    $builder->addTableColumn('name', '分类名称');
    $builder->addTableColumn('parent_id', '父级分类', 'self');
    $builder->addTableColumn('sort', '排序', 'num');
    $builder->addTableColumn('status', '状态', DBCont::getStatusList());

    $builder->addRightButton('edit');
    $builder->addRightButton('delete');

    return $builder;
}
```

### Pattern 2: Inline Edit with @save=true

```php
// In migration
$table->mediumInteger('sort')->comment('@title=排序;@type=num;@save=true;');
$table->string('title')->comment('@title=标题;@type=text;@save=true;');

// Enable inline editing in controller
$builder->addTableColumn('sort', '排序', 'num');
$builder->addTableColumn('title', '标题');
// Both columns will be editable in list view
```

### Pattern 3: Batch Operations with Confirmation

```php
$builder->setCheckBox(true);

$builder->addTopButton('custom', [
    'title' => '批量上架',
    'href' => U('batchOnSale'),
    'ajax' => true,
    'confirm' => '确定要批量上架选中的商品吗？'
]);

$builder->addTopButton('custom', [
    'title' => '批量下架',
    'href' => U('batchOffSale'),
    'ajax' => true,
    'confirm' => '确定要批量下架选中的商品吗？'
]);
```

### Pattern 4: Custom Search with Multiple Fields

```php
// In controller
protected function buildSearchMap()
{
    $map = [];

    if ($keyword = I('get.keyword')) {
        // Search across multiple fields
        $map['_complex'] = [
            '_logic' => 'or',
            'name' => ['like', '%' . $keyword . '%'],
            'code' => ['like', '%' . $keyword . '%'],
            'description' => ['like', '%' . $keyword . '%']
        ];
    }

    return $map;
}

// In buildListOptions
$builder->addSearchItem('keyword', 'text', '商品名称/编码/描述');
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Column not showing | Check field name matches database table. Use `var_dump()` to verify data. |
| Status column shows numbers | Pass the status list array: `DBCont::getStatusList()` |
| Search not filtering | Ensure `buildSearchMap()` returns correct `$map` array. Check I('get.') parameter names. |
| Custom button not working | Verify URL is correct. Use `U('Module/Controller/action')` format. |
| Picture column shows broken image | Check image path. Verify `qs_file_pic` table has correct records. |
| Pagination not working | Ensure `setKey()` is set if primary key is not 'id'. Check `$map` array format. |
| Batch operations fail | Verify `setCheckBox(true)` is called. Check form field name is 'ids[]'. |
| Self-reference column shows IDs | Verify parent records exist. Check circular reference chains. |
| Date search not filtering | Convert search string to timestamp: `strtotime(I('get.date_field'))`. |
| Custom renderer not called | Ensure 'fun' type is set. Check callback function signature: `function($value, $row)`. |

---

## Version Differences

### v13 vs v14

| Feature | v13 (Legacy) | v14 (Modern) |
|---------|--------------|--------------|
| **API** | `addTableColumn()` | `text()`, `select()`, `date()` methods |
| **UI Framework** | jQuery 1.x | React + AntdAdmin |
| **Custom Renderer** | `'fun'` type with callback | `setRenderer()` with React components |
| **Inline Edit** | `@save=true` metadata | `editable()` method |
| **Search Types** | 7 types (text, select, date, etc.) | Extended with like/exact/between modes |
| **Status Display** | Pass array to `addTableColumn()` | `setValueEnum()` + `setBadge()` |
| **Action Buttons** | `addRightButton()` | `actions()` closure |

### Migration Example

```php
// v13 (Legacy)
$builder->addTableColumn('status', '状态', DBCont::getStatusList());
$builder->addTableColumn('name', '名称');
$builder->addTableColumn('cover', '封面', 'picture');

// v14 (Modern)
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList())
    ->setBadge([1 => 'success', 0 => 'default']);

$container->text('name', '名称')
    ->setSearch(true)
    ->setSortable(true);

$container->image('cover', '封面')
    ->setWidth(100)
    ->setHeight(60);
```

---

## Related Rules

- [Table Columns v14](./crud-table-columns-v14.md) - Modern AntdAdmin API
- [Form Validation](./crud-form-validation.md) - Field validation rules
- [Search Configuration](./crud-search-basic.md) - Advanced search patterns
- [Batch Actions](./crud-batch-actions.md) - Batch operation patterns
- [Custom Components](./crud-custom-components.md) - Custom renderers and components

---

## Best Practices

1. **Always set `setMetaTitle()`** for better UX and SEO
2. **Use DBCont constants** for status fields instead of hardcoding arrays
3. **Enable checkbox** when you have batch operations
4. **Use custom renderer ('fun')** for complex display logic instead of modifying templates
5. **Set `showCondition`** on buttons to show/hide based on field values
6. **Use `between` search** for date ranges instead of two separate date pickers
7. **Lock critical columns** with `setLockCol()` to prevent accidental editing
8. **Add confirmations** for destructive actions (delete, forbid)
9. **Use `addTopButton('custom')`** for export/import operations
10. **Keep column count under 10** for optimal performance and UX

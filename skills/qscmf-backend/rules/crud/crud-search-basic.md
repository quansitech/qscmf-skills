---
title: Basic Search Configuration for Table
impact: HIGH
impactDescription: Used in 80% of CRUD implementations
tags: crud, search, table, filter, both
---

## Basic Search Configuration

Configure search functionality for table columns in QSCMF CRUD.

### When to Use This Rule

- You need to add search/filter functionality to table columns
- You want to enable user-friendly search interfaces
- You need to implement complex search logic (multi-field, range, etc.)
- You want to understand the complete search configuration system

---

## Search Type Overview

QSCMF supports multiple search types for different data scenarios:

| Search Type | Best For | v13 | v14 | Example |
|-------------|----------|-----|-----|---------|
| **like** | Text fields (names, titles) | ✅ | ✅ | Product name, User name |
| **exact** | IDs, codes, exact values | ✅ | ✅ | Order ID, SKU |
| **between** | Date ranges, numeric ranges | ✅ | ✅ | Date range, Price range |
| **select** | Dropdown choices | ✅ | ✅ | Status, Category |
| **checkbox** | Multiple selections | ✅ | ✅ | Multiple tags |
| **date** | Date pickers | ✅ | ✅ | Created date |
| **time** | Time pickers | ✅ | ✅ | Time slot |
| **datetime** | DateTime pickers | ✅ | ✅ | Published datetime |

---

## v14 (AntdAdmin) Search Configuration

### Basic Text Search

```php
// Simple text search (LIKE query)
$container->text('name', '产品名称')
    ->setSearch(true)
    ->setSearchType('like')
    ->setSearchPlaceholder('请输入产品名称');
```

**How it works:**
- User types in search box → `WHERE name LIKE '%keyword%'`
- Case-insensitive by default
- Supports partial matching

### Exact Match Search

```php
// Exact match for IDs or codes
$container->text('order_no', '订单号')
    ->setSearch(true)
    ->setSearchType('exact')
    ->setSearchPlaceholder('请输入完整订单号');
```

**How it works:**
- User types → `WHERE order_no = 'keyword'`
- Must match entire value
- Best for IDs, codes, unique identifiers

### Date Range Search

```php
// Date range picker
$container->date('create_time', '创建时间')
    ->setSearch(true)
    ->setSearchType('between')
    ->setFormat('Y-m-d')
    ->setSearchPlaceholder('选择日期范围');
```

**How it works:**
- User picks range → `WHERE create_time BETWEEN '2024-01-01' AND '2024-01-31'`
- Automatically adds `>=` and `<=` conditions
- Supports date, time, datetime fields

### Select (Dropdown) Search

```php
// Status selection
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList())
    ->setSearch(true)
    ->setSearchType('exact');

// DBCont::getStatusList() returns:
// [1 => '启用', 0 => '禁用']
```

**How it works:**
- User selects from dropdown → `WHERE status = 1`
- Uses exact match by default
- Can use `setSearchType('in')` for multiple selections

### Number Range Search

```php
// Price range
$container->text('price', '价格')
    ->setSearch(true)
    ->setSearchType('between');
```

**Input format:** `min,max` (e.g., `100,500`)
- Generates: `WHERE price BETWEEN 100 AND 500`

---

## v13 (Legacy jQuery) Search Configuration

### Using ListBuilder Search

```php
// Text search (LIKE)
$builder->addTableColumn('name', '名称');
$builder->addSearchItem('name', 'text', '名称');

// Date range
$builder->addTableColumn('create_time', '创建时间');
$builder->addSearchItem('create_time', 'date', '创建时间');

// Select dropdown
$builder->addTableColumn('status', '状态', DBCont::getStatusList());
$builder->addSearchItem('status', 'select', '状态', DBCont::getStatusList());
```

### Search Item Types (v13)

| Type | Description | Example |
|------|-------------|---------|
| `text` | Text input (LIKE) | `addSearchItem('name', 'text', '名称')` |
| `select` | Dropdown (exact) | `addSearchItem('status', 'select', '状态', $options)` |
| `date` | Date picker | `addSearchItem('date', 'date', '日期')` |
| `time` | Time picker | `addSearchItem('time', 'time', '时间')` |
| `datetime` | DateTime picker | `addSearchItem('datetime', 'datetime', '日期时间')` |
| `between` | Range input | `addSearchItem('price', 'between', '价格范围')` |
| `checkbox` | Multiple choices | `addSearchItem('tags', 'checkbox', '标签', $options)` |

---

## Advanced: Custom Search Map

For complex search logic, override `buildSearchMap()` method:

### v14 Example

```php
// app/Admin/Controller/ProductController.class.php

class ProductController extends \QsAdmin\Controller\QsListController
{
    protected function buildSearchMap(array $search): array
    {
        $map = parent::buildSearchMap($search);

        // Multi-field keyword search
        $keyword = $search['keyword'] ?? '';
        if ($keyword) {
            $map['_string'] = "name LIKE '%{$keyword}%' OR description LIKE '%{$keyword}%'";
        }

        // Price range parsing
        $priceRange = $search['price'] ?? '';
        if ($priceRange) {
            [$min, $max] = explode(',', $priceRange);
            if ($min) $map['price'][] = ['egt', $min];
            if ($max) $map['price'][] = ['elt', $max];
        }

        // Category with subcategories
        $categoryId = $search['category_id'] ?? 0;
        if ($categoryId) {
            $categoryIds = D('Category')->getSubcategoryIds($categoryId);
            $map['category_id'] = ['in', $categoryIds];
        }

        return $map;
    }

    protected function tableContainer(\Gy_Library\Components\TableContainer $container): void
    {
        $container->text('name', '产品名称')
            ->setSearch(true)
            ->setSearchType('like');

        $container->text('price', '价格')
            ->setSearch(true)
            ->setSearchType('between');

        $container->select('category_id', '分类')
            ->setValueEnum(D('Category')->getFieldOptions())
            ->setSearch(true);
    }
}
```

### v13 Example

```php
// app/Admin/Controller/ProductController.class.php

class ProductController extends \QsAdmin\Controller\QsListController
{
    public function index()
    {
        $builder = $this->builder();

        // Add table columns
        $builder->addTableColumn('name', '名称');
        $builder->addTableColumn('price', '价格');
        $builder->addTableColumn('create_time', '创建时间');

        // Add search items
        $builder->addSearchItem('name', 'text', '名称');
        $builder->addSearchItem('price', 'between', '价格范围');
        $builder->addSearchItem('create_time', 'date', '创建时间');

        // Custom search logic
        $map = $this->buildSearchMap(I('get.'));

        $builder->setData(D('Product')->where($map)->select());
        $builder->display();
    }

    protected function buildSearchMap(array $search): array
    {
        $map = [];

        // Keyword search across multiple fields
        $keyword = $search['keyword'] ?? '';
        if ($keyword) {
            $map['name|description'] = ['like', '%' . $keyword . '%'];
        }

        // Price range
        $priceMin = $search['price_min'] ?? 0;
        $priceMax = $search['price_max'] ?? 0;
        if ($priceMin && $priceMax) {
            $map['price'] = [['egt', $priceMin], ['elt', $priceMax]];
        }

        return $map;
    }
}
```

---

## Common Search Patterns

### Pattern 1: Multi-Field Keyword Search

Search across multiple related fields with a single keyword:

```php
// v14
protected function buildSearchMap(array $search): array
{
    $map = parent::buildSearchMap($search);

    $keyword = $search['keyword'] ?? '';
    if ($keyword) {
        // Search in name, email, or phone
        $map['_complex'] = [
            'name'     => ['like', '%' . $keyword . '%'],
            'email'    => ['like', '%' . $keyword . '%'],
            'telephone' => ['like', '%' . $keyword . '%'],
            '_logic'   => 'OR'
        ];
    }

    return $map;
}
```

### Pattern 2: Date Range with Defaults

```php
// v14
protected function buildSearchMap(array $search): array
{
    $map = parent::buildSearchMap($search);

    // Default to last 30 days if no date specified
    if (empty($search['create_time'])) {
        $map['create_time'] = [
            ['egt', date('Y-m-d', strtotime('-30 days'))],
            ['elt', date('Y-m-d')]
        ];
    }

    return $map;
}
```

### Pattern 3: Status Filtering with "All" Option

```php
// v14
protected function tableContainer(\Gy_Library\Components\TableContainer $container): void
{
    $statusOptions = [0 => '全部'] + DBCont::getStatusList();

    $container->select('status', '状态')
        ->setValueEnum($statusOptions)
        ->setSearch(true)
        ->setSearchType('exact')
        ->setSearchDefault(['status' => 0]); // Default to "All"
}

protected function buildSearchMap(array $search): array
{
    $map = parent::buildSearchMap($search);

    // Remove status condition if "All" is selected
    if (isset($map['status']) && $map['status'] == 0) {
        unset($map['status']);
    }

    return $map;
}
```

### Pattern 4: Related Field Search (Join Tables)

```php
// v14
protected function buildSearchMap(array $search): array
{
    $map = parent::buildSearchMap($search);

    // Search in related table
    $categoryName = $search['category_name'] ?? '';
    if ($categoryName) {
        $categoryIds = D('Category')
            ->where(['name' => ['like', '%' . $categoryName . '%']])
            ->getField('id', true);

        $map['category_id'] = ['in', $categoryIds ?: [0]];
    }

    return $map;
}
```

---

## Search Configuration Methods Reference

### v14 (AntdAdmin)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `setSearch()` | `bool $enable = true` | `$this` | Enable/disable search for this column |
| `setSearchType()` | `string $type` | `$this` | Set search type: `like`, `exact`, `between` |
| `setSearchPlaceholder()` | `string $text` | `$this` | Set placeholder text in search input |
| `setSearchDefault()` | `array $value` | `$this` | Set default search value |
| `setAdvancedFilter()` | `array $config` | `$this` | Configure advanced filter panel |

### v13 (ListBuilder)

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `addSearchItem()` | `$field, $type, $title, $options = []` | `void` | Add search item to form |
| `setSearchUrl()` | `string $url` | `void` | Custom search submission URL |

---

## Search Map Query Syntax

### ThinkPHP Where Conditions

```php
// Equal
$map['status'] = 1;
// WHERE status = 1

// LIKE
$map['name'] = ['like', '%keyword%'];
// WHERE name LIKE '%keyword%'

// Greater than or equal
$map['price'] = ['egt', 100];
// WHERE price >= 100

// Less than or equal
$map['price'] = ['elt', 500];
// WHERE price <= 500

// Between
$map['price'] = [['egt', 100], ['elt', 500]];
// WHERE price >= 100 AND price <= 500

// IN array
$map['category_id'] = ['in', [1, 2, 3]];
// WHERE category_id IN (1, 2, 3)

// NOT IN
$map['status'] = ['not in', [0, -1]];
// WHERE status NOT IN (0, -1)

// Complex OR conditions
$map['_complex'] = [
    'name' => ['like', '%keyword%'],
    'email' => ['like', '%keyword%'],
    '_logic' => 'OR'
];
// WHERE (name LIKE '%keyword%' OR email LIKE '%keyword%')
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|--------|----------|
| Search not working | `setSearch(true)` not called | Add `->setSearch(true)` to column definition |
| Date search fails | Date format mismatch | Ensure database stores dates as `Y-m-d` format |
 Chinese search fails | Character encoding issue | Check database charset is `utf8mb4` |
| Multi-field search not working | Incorrect `_complex` syntax | Use proper ThinkPHP complex query syntax |
| Search results empty | Search map overriding conditions | Check `buildSearchMap()` logic, use `parent::buildSearchMap()` |

---

## Best Practices

1. **Always enable search on frequently filtered fields**
   ```php
   $container->text('name', '名称')->setSearch(true);
   ```

2. **Use appropriate search types**
   - Text fields → `like`
   - IDs, codes → `exact`
   - Dates, numbers → `between`

3. **Provide helpful placeholders**
   ```php
   ->setSearchPlaceholder('请输入产品名称或编码')
   ```

4. **Handle empty search gracefully**
   ```php
   if (!empty($search['keyword'])) {
       $map['name'] = ['like', '%' . $search['keyword'] . '%'];
   }
   ```

5. **Set reasonable defaults**
   ```php
   ->setSearchDefault(['status' => 1]) // Default to active
   ```

6. **Test search with various inputs**
   - Empty search
   - Partial matches
   - Special characters
   - Date ranges
   - Boundary values

---

## Version Differences

| Feature | v14 (AntdAdmin) | v13 (Legacy) |
|---------|------------------|--------------|
| Search API | `setSearch()`, `setSearchType()` | `addSearchItem()` |
| Search Types | like, exact, between | text, select, date, between, checkbox |
| Default Search Type | `like` for text columns | Based on column type |
| Custom Search | Override `buildSearchMap()` | Override in `index()` method |
| Multi-field Search | Complex query support | Manual implementation |
| Date Range UI | Built-in date picker | Manual input or date picker |
| Search URL | AJAX to controller | Form GET submission |

---

## Complete Working Example

### v14 Product Search

```php
<?php
// app/Admin/Controller/ProductController.class.php

namespace Admin\Controller;
use Gy_Library\Components\TableContainer;

class ProductController extends \QsAdmin\Controller\QsListController
{
    protected $tableName = 'product';

    protected function tableContainer(TableContainer $container): void
    {
        // Basic columns
        $container->text('id', 'ID')
            ->setSortable(true)
            ->setWidth(80);

        $container->text('name', '产品名称')
            ->setSearch(true)
            ->setSearchType('like')
            ->setSearchPlaceholder('输入产品名称')
            ->setSortable(true);

        $container->select('category_id', '分类')
            ->setValueEnum(D('Category')->getFieldOptions())
            ->setSearch(true)
            ->setSearchType('exact');

        $container->text('price', '价格')
            ->setSearch(true)
            ->setSearchType('between')
            ->setSortable(true);

        $container->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList())
            ->setSearch(true)
            ->setSearchType('exact')
            ->setBadge([1 => 'success', 0 => 'default']);

        $container->date('create_time', '创建时间')
            ->setSearch(true)
            ->setSearchType('between')
            ->setFormat('Y-m-d H:i:s');
    }

    protected function buildSearchMap(array $search): array
    {
        $map = parent::buildSearchMap($search);

        // Multi-field keyword search
        $keyword = $search['keyword'] ?? '';
        if ($keyword) {
            $map['_complex'] = [
                'name'        => ['like', '%' . $keyword . '%'],
                'description' => ['like', '%' . $keyword . '%'],
                '_logic'      => 'OR'
            ];
        }

        // Default: only show active products
        if (!isset($search['status'])) {
            $map['status'] = DBCont::NORMAL_STATUS;
        }

        return $map;
    }
}
```

### v13 Product Search

```php
<?php
// app/Admin/Controller/ProductController.class.php

namespace Admin\Controller;

class ProductController extends \QsAdmin\Controller\QsListController
{
    protected $tableName = 'product';

    public function index()
    {
        $builder = $this->builder();

        // Table columns
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('name', '名称');
        $builder->addTableColumn('category_id', '分类', D('Category')->getFieldOptions());
        $builder->addTableColumn('price', '价格');
        $builder->addTableColumn('status', '状态', DBCont::getStatusList());
        $builder->addTableColumn('create_time', '创建时间');

        // Search items
        $builder->addSearchItem('name', 'text', '产品名称');
        $builder->addSearchItem('category_id', 'select', '分类', D('Category')->getFieldOptions());
        $builder->addSearchItem('price', 'between', '价格范围');
        $builder->addSearchItem('status', 'select', '状态', DBCont::getStatusList());
        $builder->addSearchItem('create_time', 'date', '创建时间');

        // Build search map
        $map = $this->buildSearchMap(I('get.'));

        // Set data
        $builder->setData(D('Product')->where($map)->order('id desc')->select());
        $builder->display();
    }

    protected function buildSearchMap(array $search): array
    {
        $map = [];

        // Name search
        if (!empty($search['name'])) {
            $map['name'] = ['like', '%' . $search['name'] . '%'];
        }

        // Category filter
        if (!empty($search['category_id'])) {
            $map['category_id'] = $search['category_id'];
        }

        // Price range
        if (!empty($search['price'])) {
            [$min, $max] = explode(',', $search['price']);
            if ($min) $map['price'][] = ['egt', $min];
            if ($max) $map['price'][] = ['elt', $max];
        }

        // Status filter
        if (isset($search['status']) && $search['status'] !== '') {
            $map['status'] = $search['status'];
        }

        // Date range
        if (!empty($search['create_time'])) {
            [$start, $end] = explode(',', $search['create_time']);
            if ($start) $map['create_time'][] = ['egt', $start];
            if ($end) $map['create_time'][] = ['elt', $end];
        }

        return $map;
    }
}
```

---

## See Also

- [Table Columns v14](crud-table-columns-v14.md) - Complete column configuration
- [Table Columns v13](crud-table-columns-v13.md) - Legacy column configuration
- [Form Validation](crud-form-validation.md) - Form field validation
- [CRUD Workflow](../workflow/workflow-add-crud.md) - End-to-end CRUD development

---

## Iron Law

```
NO SEARCH WITHOUT setSearch(true) CONFIGURATION
```

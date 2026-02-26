---
title: Search Configuration (v13)
impact: HIGH
impactDescription: Required for all list pages with filtering
tags: crud, search, v13
---

## Search Configuration (v13)

Configure search functionality for v13 admin list pages.

### When to Use This Rule

- Adding search to list page
- Configuring filter options
- Building complex search conditions

---

## Search Item Types

### Text Search

```php
$builder->addSearchItem('keyword', 'text', '关键词');
```

Controller handling:

```php
if (!empty($search['keyword'])) {
    $map['name'] = ['like', '%' . $search['keyword'] . '%'];
}
```

### Select Search

```php
// Static options
$builder->addSearchItem('status', 'select', '状态', '', [
    '' => '全部',
    1 => '启用',
    0 => '禁用'
]);

// From DBCont
$builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());

// From model
$builder->addSearchItem('cate_id', 'select', '分类', '', D('Category')->getFieldOptions());
```

Controller handling:

```php
// Status (supports 0 value)
if (isset($search['status']) && $search['status'] !== '') {
    $map['status'] = $search['status'];
}

// Category
if (!empty($search['cate_id'])) {
    $map['cate_id'] = $search['cate_id'];
}
```

### Date Search

```php
$builder->addSearchItem('create_date', 'date', '创建日期');
```

### Date Range Search

```php
$builder->addSearchItem('create_time', 'date_range', '时间范围', ['time_picker' => '0']);
```

Controller handling:

```php
use Qscmf\Builder\ListSearchType\DateRange;

$map = array_merge($map, DateRange::parse('create_time', 'create_time', $get_data));
```

Or manual:

```php
if (!empty($search['create_time_start'])) {
    $map['create_time'][] = ['egt', strtotime($search['create_time_start'])];
}
if (!empty($search['create_time_end'])) {
    $map['create_time'][] = ['elt', strtotime($search['create_time_end'])];
}
```

### Between Search

```php
$builder->addSearchItem('price', 'between', '价格范围');
```

Controller handling:

```php
if (!empty($search['price_start'])) {
    $map['price'][] = ['egt', $search['price_start']];
}
if (!empty($search['price_end'])) {
    $map['price'][] = ['elt', $search['price_end']];
}
```

### Checkbox Search

```php
$builder->addSearchItem('tags', 'checkbox', '标签', '', [
    1 => '标签一',
    2 => '标签二',
    3 => '标签三'
]);
```

---

## Search Parameter Parsing

### Using Built-in Parse Methods

```php
use Qscmf\Builder\ListSearchType\Text;
use Qscmf\Builder\ListSearchType\Select;
use Qscmf\Builder\ListSearchType\DateRange;
use Qscmf\Builder\ListSearchType\Hidden;

// Text search (fuzzy)
$map = array_merge($map, Text::parse('keyword', 'name', $get_data, 'fuzzy'));

// Text search (exact)
$map = array_merge($map, Text::parse('code', 'code', $get_data, 'exact'));

// Select
$map = array_merge($map, Select::parse('status', 'status', $get_data));

// Date range
$map = array_merge($map, DateRange::parse('create_time', 'create_time', $get_data));

// Hidden
$map = array_merge($map, Hidden::parse('user_id', 'user_id', $get_data));
```

---

## Multi-Field Search

```php
// Search across multiple fields
if (!empty($search['keyword'])) {
    $map['_complex'] = [
        '_logic' => 'or',
        'name' => ['like', '%' . $search['keyword'] . '%'],
        'code' => ['like', '%' . $search['keyword'] . '%'],
        'description' => ['like', '%' . $search['keyword'] . '%']
    ];
}
```

---

## Complete Example

```php
protected function buildSearchForm($builder)
{
    $builder->addSearchItem('keyword', 'text', '搜索');
    $builder->addSearchItem('cate_id', 'select', '分类', '', D('Category')->getFieldOptions());
    $builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());
    $builder->addSearchItem('create_time', 'date_range', '创建时间');
}

protected function buildSearchMap(array $search): array
{
    $map = [];

    // Keyword
    if (!empty($search['keyword'])) {
        $map['name|code'] = ['like', '%' . $search['keyword'] . '%'];
    }

    // Category
    if (!empty($search['cate_id'])) {
        $map['cate_id'] = $search['cate_id'];
    }

    // Status
    if (isset($search['status']) && $search['status'] !== '') {
        $map['status'] = $search['status'];
    }

    // Date range
    if (!empty($search['create_time_start'])) {
        $map['create_time'][] = ['egt', strtotime($search['create_time_start'])];
    }
    if (!empty($search['create_time_end'])) {
        $map['create_time'][] = ['elt', strtotime($search['create_time_end'])];
    }

    return $map;
}
```

---

## Related Rules

- [ListBuilder API](../listbuilder-api.md) - Complete API reference
- [Table Columns v13](crud-table-columns-v13.md) - Column configuration

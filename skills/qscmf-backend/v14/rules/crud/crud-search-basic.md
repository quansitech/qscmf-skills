---
title: Search Configuration (v14)
impact: HIGH
impactDescription: Required for all list pages with filtering
tags: crud, search, v14, antdadmin
---

## Search Configuration (v14)

Configure search functionality for v14 admin list pages using AntdAdmin Component API.

### When to Use This Rule

- Adding search to list page
- Configuring filter options
- Building complex search conditions

---

## Basic Search with setSearch()

In v14, search is configured directly on columns using `setSearch()`:

```php
$table->columns(function (Table\ColumnsContainer $container) {
    // Enable search on text column
    $container->text('product_name', '商品名称')
        ->setSearch(true);

    // Enable search on select column
    $container->select('status', '状态')
        ->setValueEnum(DBCont::getStatusList())
        ->setSearch(true);

    // Enable search on datetime column
    $container->datetime('create_time', '创建时间')
        ->setSearch(true);
});
```

---

## Search Types

### Text Search

```php
// Basic text search (fuzzy match by default)
$container->text('name', '名称')
    ->setSearch(true);

// Text search with exact match
$container->text('order_no', '订单号')
    ->setSearch(true)
    ->setSearchType('exact');
```

Controller handling:

```php
protected function buildSearchWhere($get_data, &$map)
{
    // Fuzzy search (default)
    if (!empty($get_data['name'])) {
        $map['name'] = ['like', '%' . $get_data['name'] . '%'];
    }

    // Exact match
    if (!empty($get_data['order_no'])) {
        $map['order_no'] = $get_data['order_no'];
    }
}
```

### Select Search

```php
// Using DBCont constants
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList())
    ->setSearch(true);

// Custom options
$container->select('audit_status', '审核状态')
    ->setValueEnum([
        '' => '全部',
        0 => '待审核',
        1 => '已通过',
        2 => '已拒绝'
    ])
    ->setSearch(true);

// From model
$container->select('cate_id', '分类')
    ->setValueEnum(D('Category')->getField('id,name'))
    ->setSearch(true);
```

Controller handling:

```php
protected function buildSearchWhere($get_data, &$map)
{
    // Status (supports 0 value)
    if (isset($get_data['status']) && $get_data['status'] !== '') {
        $map['status'] = $get_data['status'];
    }

    // Category
    if (!empty($get_data['cate_id'])) {
        $map['cate_id'] = $get_data['cate_id'];
    }
}
```

### Date/DateTime Search

```php
// Date search
$container->date('publish_date', '发布日期')
    ->setSearch(true);

// DateTime search (range picker)
$container->datetime('create_time', '创建时间')
    ->setSearch(true);
```

Controller handling:

```php
use Qscmf\Builder\ListSearchType\DateRange;

protected function buildSearchWhere($get_data, &$map)
{
    // Single date
    if (!empty($get_data['publish_date'])) {
        $map['publish_date'] = $get_data['publish_date'];
    }

    // Date range
    if (!empty($get_data['create_time'])) {
        $map = array_merge($map, DateRange::parse(
            'create_time',
            'create_time',
            $get_data
        ));
    }
}
```

### Number/Money Search

```php
// Number search
$container->number('stock', '库存')
    ->setSearch(true);

// Money search
$container->money('price', '价格')
    ->setSearch(true);
```

---

## Search Parameter Parsing

### Using Built-in Parse Methods

```php
use Qscmf\Builder\ListSearchType\Text;
use Qscmf\Builder\ListSearchType\Select;
use Qscmf\Builder\ListSearchType\DateRange;
use Qscmf\Builder\ListSearchType\Hidden;

protected function buildSearchWhere($get_data, &$map)
{
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
}
```

### Manual Parsing

```php
protected function buildSearchWhere($get_data, &$map)
{
    // Keyword fuzzy search
    if (!empty($get_data['keyword'])) {
        $map['name'] = ['like', '%' . $get_data['keyword'] . '%'];
    }

    // Status exact match
    if (isset($get_data['status']) && $get_data['status'] !== '') {
        $map['status'] = $get_data['status'];
    }

    // Date range manual
    if (!empty($get_data['create_time_start'])) {
        $map['create_time'][] = ['egt', strtotime($get_data['create_time_start'])];
    }
    if (!empty($get_data['create_time_end'])) {
        $map['create_time'][] = ['elt', strtotime($get_data['create_time_end'])];
    }

    // Number range
    if (!empty($get_data['price_start'])) {
        $map['price'][] = ['egt', $get_data['price_start']];
    }
    if (!empty($get_data['price_end'])) {
        $map['price'][] = ['elt', $get_data['price_end']];
    }
}
```

---

## Multi-Field Search

### Search Across Multiple Fields

```php
protected function buildSearchWhere($get_data, &$map)
{
    // Search across multiple fields with OR logic
    if (!empty($get_data['keyword'])) {
        $map['_complex'] = [
            '_logic' => 'or',
            'name' => ['like', '%' . $get_data['keyword'] . '%'],
            'code' => ['like', '%' . $get_data['keyword'] . '%'],
            'description' => ['like', '%' . $get_data['keyword'] . '%']
        ];
    }
}
```

### Using ThinkPHP Field Syntax

```php
protected function buildSearchWhere($get_data, &$map)
{
    // Search in name or code field
    if (!empty($get_data['keyword'])) {
        $map['name|code'] = ['like', '%' . $get_data['keyword'] . '%'];
    }
}
```

---

## Search Configuration Options

### setSearch() Method

```php
// Enable search (default behavior)
$container->text('name', '名称')
    ->setSearch(true);

// Disable search
$container->text('internal_id', '内部ID')
    ->setSearch(false);
```

### Search Placeholder

```php
$container->text('name', '名称')
    ->setSearch(true)
    ->setPlaceholder('请输入商品名称');
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
use Qscmf\Builder\ListSearchType\Text;
use Qscmf\Builder\ListSearchType\Select;
use Qscmf\Builder\ListSearchType\DateRange;

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
        $data_list = $model
            ->order('id desc')
            ->page($page->nowPage, $page->listRows)
            ->select();

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

                // Keyword search
                $container->text('product_name', '商品名称')
                    ->setSearch(true);

                // Select search from model
                $container->select('cate_id', '分类')
                    ->setValueEnum(D('Category')->getField('id,name'))
                    ->setSearch(true);

                $container->image('cover', '封面');
                $container->money('price', '价格');

                // Select search with DBCont
                $container->select('status', '状态')
                    ->setValueEnum(DBCont::getStatusList())
                    ->setBadge([1 => 'success', 0 => 'default'])
                    ->setSearch(true);

                // Date range search
                $container->datetime('create_time', '创建时间')
                    ->setSearch(true);

                $container->action('', '操作')
                    ->actions(function (Table\ColumnType\ActionsContainer $container) {
                        $container->edit()->modal(
                            (new Modal())
                                ->setWidth('800px')
                                ->setUrl(U('edit', ['id' => '__id__']))
                                ->setTitle('编辑')
                        );
                        $container->delete();
                    });
            })
            ->setDataSource($data_list)
            ->setPagination(new Pagination($page->nowPage, $page->listRows, $count))
            ->render();
    }

    protected function buildSearchWhere($get_data, &$map)
    {
        // Keyword search across multiple fields
        if (!empty($get_data['product_name'])) {
            $map['product_name|code'] = ['like', '%' . $get_data['product_name'] . '%'];
        }

        // Category filter
        if (!empty($get_data['cate_id'])) {
            $map['cate_id'] = $get_data['cate_id'];
        }

        // Status filter (supports 0 value)
        if (isset($get_data['status']) && $get_data['status'] !== '') {
            $map['status'] = $get_data['status'];
        }

        // Date range filter
        if (!empty($get_data['create_time'])) {
            $map = array_merge($map, DateRange::parse(
                'create_time',
                'create_time',
                $get_data
            ));
        }
    }
}
```

---

## Search Type Reference

| Type | Use Case | Query Format |
|------|----------|--------------|
| Text (fuzzy) | Name, title search | `LIKE '%keyword%'` |
| Text (exact) | Code, order number | `= 'value'` |
| Select | Status, category | `= value` |
| Date | Single date | `= 'Y-m-d'` |
| DateRange | Date range | `BETWEEN start AND end` |
| Number | Numeric value | `= value` |

---

## Related Rules

- [Table Columns v14](crud-table-columns-v14.md) - Column configuration
- [AntdAdmin Components](../antdadmin.md) - Complete component reference
- [ListBuilder API](../listbuilder-api.md) - Legacy API reference

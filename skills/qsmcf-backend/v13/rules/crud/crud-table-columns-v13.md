---
title: Table Columns Configuration (v13)
impact: HIGH
impactDescription: Required for all admin list pages
tags: crud, table, columns, v13, listbuilder
---

## Table Columns Configuration (v13 - ListBuilder)

Complete reference for configuring table columns using ListBuilder API in QSCMF v13.

### When to Use This Rule

- Building admin list pages
- Configuring table columns
- Adding column-level features

---

## Quick Reference

```php
$builder = $this->builder();

// Basic column
$builder->addTableColumn('id', 'ID');

// With type
$builder->addTableColumn('status', '状态', DBCont::getStatusList());

// With options
$builder->addTableColumn('cover', '封面', 'picture');
```

---

## Column Types

### 1. Text (Default)

```php
$builder->addTableColumn('name', '名称');
$builder->addTableColumn('email', '邮箱');
```

### 2. Status/Select

```php
// Using DBCont
$builder->addTableColumn('status', '状态', DBCont::getStatusList());

// Custom mapping
$builder->addTableColumn('audit_status', '审核状态', [
    0 => '<span class="label label-default">待审核</span>',
    1 => '<span class="label label-success">已通过</span>',
    2 => '<span class="label label-danger">已拒绝</span>'
]);
```

### 3. Date/Time

```php
// Date format
$builder->addTableColumn('create_time', '创建时间', 'date_format', 'Y-m-d H:i');

// Time type
$builder->addTableColumn('publish_time', '发布时间', 'time');
```

### 4. Image

```php
// Single image
$builder->addTableColumn('cover', '封面', 'picture');

// Multiple images
$builder->addTableColumn('images', '图片集', 'pictures');

// With custom thumbnail
$builder->addTableColumn('proof', '凭证', 'picture', [
    'small-url' => function($image_id) {
        $url = showFileUrl($image_id);
        return $url . '?x-oss-process=image/resize,m_fill,w_40,h_40';
    }
]);
```

### 5. Number

```php
$builder->addTableColumn('sort', '排序', 'num');
$builder->addTableColumn('price', '价格', 'num');
$builder->addTableColumn('stock', '库存', 'num');
```

### 6. Checkbox

```php
$builder->addTableColumn('is_recommend', '推荐', 'checkbox');
$builder->addTableColumn('is_hot', '热门', 'checkbox');
```

### 7. Link

```php
$builder->addTableColumn('url', '链接', 'a');

// With custom href
$builder->addTableColumn('id', '操作', 'a', [
    'title' => '查看详情',
    'href' => U('detail', ['id' => '@id@'])
]);
```

### 8. Custom Function

```php
$builder->addTableColumn('custom', '自定义', 'fun', function($value, $data) {
    return $data['field1'] . ' - ' . $data['field2'];
});

// User info example
$builder->addTableColumn('user_id', '用户', 'fun', function($user_id, $row) {
    $user = D('User')->find($user_id);
    return $user ? $user['username'] : '未知';
});

// Status with color
$builder->addTableColumn('status_display', '状态', 'fun', function($value, $data) {
    $color_map = [1 => 'success', 0 => 'default'];
    $text_map = [1 => '启用', 0 => '禁用'];
    return sprintf(
        '<span class="label label-%s">%s</span>',
        $color_map[$data['status']],
        $text_map[$data['status']]
    );
});
```

### 9. Textarea (Truncated)

```php
$builder->addTableColumn('summary', '摘要', 'textarea');
```

---

## Column Options

### Width

```php
$builder->addTableColumn('name', '名称', '', '', 'style="width:200px"');
```

### Editable (Inline)

```php
// In migration: @save=true
$table->integer('sort')->comment('@title=排序;@type=num;@save=true;');

// Column will be editable
$builder->addTableColumn('sort', '排序', 'num');

// With callback condition
$builder->addTableColumn('amount', '金额', 'num', '', function($data) {
    return $data['manual'] == 1;  // Only editable when manual
});
```

---

## Complete Example

```php
protected function buildTableColumns($builder)
{
    $builder->addTableColumn('id', 'ID');
    $builder->addTableColumn('product_name', '商品名称');
    $builder->addTableColumn('cate_id', '分类', D('Cate')->getFieldOptions());
    $builder->addTableColumn('cover', '封面', 'picture');
    $builder->addTableColumn('price', '价格', 'num');
    $builder->addTableColumn('stock', '库存', 'num');
    $builder->addTableColumn('is_recommend', '推荐', 'checkbox');
    $builder->addTableColumn('status', '状态', DBCont::getStatusList());
    $builder->addTableColumn('sort', '排序', 'num');
    $builder->addTableColumn('create_time', '创建时间', 'date_format', 'Y-m-d H:i');
}
```

---

## Related Rules

- [ListBuilder API](../listbuilder-api.md) - Complete API reference
- [CRUD Search Basic](crud-search-basic.md) - Search configuration
- [CRUD Custom Components](crud-custom-components.md) - Custom renderers

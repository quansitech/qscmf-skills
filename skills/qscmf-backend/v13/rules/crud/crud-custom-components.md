---
title: Custom Components (v13)
impact: MEDIUM
impactDescription: Required for custom table/form rendering
tags: crud, custom, components, v13
---

## Custom Components (v13)

Create custom renderers and components for v13 admin pages.

### When to Use This Rule

- Custom table column rendering
- Complex form field types
- Special display logic

---

## Custom Column Renderer

### Function Type

```php
// Simple callback
$builder->addTableColumn('custom', '自定义', 'fun', function($value, $data) {
    return '<span class="badge">' . $value . '</span>';
});

// Complex callback with data
$builder->addTableColumn('user_info', '用户信息', 'fun', function($value, $data) {
    $user = D('User')->find($data['user_id']);
    if ($user) {
        return sprintf(
            '<div><strong>%s</strong></div><div class="text-muted">%s</div>',
            $user['username'],
            $user['email']
        );
    }
    return '未知用户';
});

// Status with color
$builder->addTableColumn('status_display', '状态', 'fun', function($value, $data) {
    $color_map = [
        0 => 'default',
        1 => 'success',
        2 => 'warning',
        3 => 'danger'
    ];
    $text_map = [
        0 => '待处理',
        1 => '已完成',
        2 => '处理中',
        3 => '已取消'
    ];

    $status = $data['status'];
    $color = $color_map[$status] ?? 'default';
    $text = $text_map[$status] ?? '未知';

    return sprintf('<span class="label label-%s">%s</span>', $color, $text);
});

// Image with preview
$builder->addTableColumn('cover_display', '封面', 'fun', function($value, $data) {
    if (empty($data['cover'])) {
        return '<span class="text-muted">无图片</span>';
    }
    $url = get_image_url($data['cover']);
    return sprintf(
        '<a href="%s" target="_blank"><img src="%s" style="max-width:60px;max-height:40px;"></a>',
        $url, $url
    );
});

// Price with currency
$builder->addTableColumn('price_display', '价格', 'fun', function($value, $data) {
    $price = number_format($data['price'], 2);
    return '<span class="text-danger">¥' . $price . '</span>';
});

// Link with action
$builder->addTableColumn('action_link', '操作', 'fun', function($value, $data) {
    return sprintf(
        '<a href="%s" class="btn btn-xs btn-primary">查看</a>',
        U('detail', ['id' => $data['id']])
    );
});
```

---

## Custom Form Item

### Custom Template

```php
// Use self type for custom template
$builder->addFormItem('custom_field', 'self', '自定义', [
    'template' => 'custom_field_template'
]);
```

Template file `custom_field_template.html`:

```html
<div class="form-group">
    <label class="col-sm-2 control-label">自定义字段</label>
    <div class="col-sm-10">
        <div class="custom-component">
            <!-- Custom HTML -->
            <input type="text" name="custom_field" value="{$data.custom_field|default=''}" class="form-control">
            <span class="help-block">帮助文本</span>
        </div>
    </div>
</div>
```

### JavaScript Enhancement

```javascript
// Custom form component
$(function() {
    // Color picker
    $('.color-picker').colorpicker();

    // Date range
    $('.date-range').daterangepicker({
        locale: {
            format: 'YYYY-MM-DD'
        }
    });

    // Tag input
    $('.tag-input').tagsinput();
});
```

---

## Custom Button

### Custom Top Button

```php
$builder->addTopButton('custom', [
    'title' => '批量审核',
    'href' => U('batchAudit'),
    'icon' => 'fa fa-check',
    'class' => 'btn btn-warning must-select-item',
    'must-select-msg' => '请选择要审核的记录',
    'ajax' => true,
    'confirm' => '确定要批量审核通过吗？'
]);
```

### Custom Right Button

```php
$builder->addRightButton('custom', [
    'title' => '查看详情',
    'href' => U('detail', ['id' => '@id@']),
    'icon' => 'fa fa-eye',
    'class' => 'label label-primary'
]);

// Conditional button
$builder->addRightButton('custom', [
    'title' => '审核',
    'href' => U('audit', ['id' => '@id@']),
    'icon' => 'fa fa-check',
    'showCondition' => [
        'field' => 'status',
        'operator' => 'eq',
        'value' => 0  // Only show when status = 0
    ]
]);
```

---

## Inline Edit

### Enable Inline Edit

```php
// In migration, add @save=true metadata
$table->integer('sort')->comment('@title=排序;@type=num;@save=true;');

// Column will be editable in list view
$builder->addTableColumn('sort', '排序', 'num');
```

### Editable with Callback

```php
$builder->addTableColumn('amount', '支出金额', 'num', '', function($data) {
    return $data['manual'] == 1;  // Only editable when manual = 1
});
```

---

## Common Patterns

### Multi-Column Display

```php
$builder->addTableColumn('product_info', '商品信息', 'fun', function($value, $data) {
    return sprintf(
        '<div class="product-info">
            <div class="product-name">%s</div>
            <div class="product-code text-muted">编码: %s</div>
            <div class="product-price text-danger">¥%s</div>
        </div>',
        $data['name'],
        $data['code'],
        number_format($data['price'], 2)
    );
});
```

### Progress Bar

```php
$builder->addTableColumn('progress', '进度', 'fun', function($value, $data) {
    $percent = min(100, max(0, $data['progress']));
    $color = $percent >= 80 ? 'success' : ($percent >= 50 ? 'warning' : 'danger');
    return sprintf(
        '<div class="progress" style="margin-bottom:0;">
            <div class="progress-bar progress-bar-%s" style="width:%d%%">%d%%</div>
        </div>',
        $color, $percent, $percent
    );
});
```

### Rating Stars

```php
$builder->addTableColumn('rating', '评分', 'fun', function($value, $data) {
    $rating = $data['rating'];
    $stars = '';
    for ($i = 1; $i <= 5; $i++) {
        $class = $i <= $rating ? 'fa-star text-warning' : 'fa-star-o text-muted';
        $stars .= '<i class="fa ' . $class . '"></i> ';
    }
    return $stars;
});
```

---

## Related Rules

- [ListBuilder API](../listbuilder-api.md) - Column types
- [FormBuilder API](../formbuilder-api.md) - Form types
- [Legacy jQuery](../legacy-jquery.md) - JavaScript patterns

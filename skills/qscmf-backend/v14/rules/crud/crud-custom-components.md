---
title: Custom Components (v14)
impact: MEDIUM
impactDescription: Required for custom table/form rendering
tags: crud, custom, components, v14, antdadmin
---

## Custom Components (v14)

Create custom renderers and components for v14 admin pages using AntdAdmin Component API.

### When to Use This Rule

- Custom table column rendering
- Complex form field types
- Special display logic
- Reusable component patterns

---

## Custom Table Column Renderer

### Using setRender() Method

```php
use AntdAdmin\Component\Table;

$table->columns(function (Table\ColumnsContainer $container) {
    // Simple callback
    $container->text('full_name', '全名')
        ->setRender(function($value, $row) {
            return $row['first_name'] . ' ' . $row['last_name'];
        });

    // Complex callback with data
    $container->text('user_info', '用户信息')
        ->setRender(function($value, $row) {
            $user = D('User')->find($row['user_id']);
            if ($user) {
                return sprintf(
                    '<div><strong>%s</strong></div><div class="text-muted">%s</div>',
                    $user['username'],
                    $user['email']
                );
            }
            return '未知用户';
        });
});
```

### Status with Color

```php
$container->text('status_display', '状态')
    ->setRender(function($value, $row) {
        $color_map = [
            0 => 'default',
            1 => 'success',
            2 => 'warning',
            3 => 'error'
        ];
        $text_map = [
            0 => '待处理',
            1 => '已完成',
            2 => '处理中',
            3 => '已取消'
        ];

        $status = $row['status'];
        $color = $color_map[$status] ?? 'default';
        $text = $text_map[$status] ?? '未知';

        return sprintf(
            '<span class="ant-tag ant-tag-%s">%s</span>',
            $color, $text
        );
    });
```

### Image with Preview

```php
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
```

### Price with Currency

```php
$container->text('price_display', '价格')
    ->setRender(function($value, $row) {
        $price = number_format($row['price'], 2);
        return '<span style="color: red;">¥' . $price . '</span>';
    });
```

### Link with Action

```php
$container->text('action_link', '操作')
    ->setRender(function($value, $row) {
        return sprintf(
            '<a href="%s" class="ant-btn ant-btn-link">查看</a>',
            U('detail', ['id' => $row['id']])
        );
    });
```

---

## Custom Form Field

### Using setProps() for Custom Props

```php
use AntdAdmin\Component\Form;

$form->columns(function (Form\ColumnsContainer $columns) {
    // Custom field with additional props
    $columns->text('custom_field', '自定义字段')
        ->setProps([
            'prefix' => '¥',
            'suffix' => '元',
            'placeholder' => '请输入金额'
        ]);

    // Textarea with custom rows
    $columns->textarea('description', '描述')
        ->setProps([
            'rows' => 6,
            'maxLength' => 500,
            'showCount' => true
        ]);

    // Number with step
    $columns->number('price', '价格')
        ->setProps([
            'min' => 0,
            'max' => 999999.99,
            'step' => 0.01,
            'precision' => 2
        ]);
});
```

### Custom Upload Configuration

```php
$columns->image('cover_id', '封面图')
    ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
    ->setCrop('16/9')
    ->setProps([
        'maxCount' => 1,
        'accept' => 'image/*'
    ]);

$columns->file('attachment', '附件')
    ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('file'))
    ->setProps([
        'maxCount' => 5,
        'maxSize' => 10 * 1024 * 1024  // 10MB
    ]);
```

---

## Creating Custom Column Types

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
    // Using custom column type
    $status = new StatusColumn('status', '状态');
    $status->setStatusMap(DBCont::getStatusList())
        ->setDefaultBadge()
        ->enableSearch();

    $container->addColumn($status);
});
```

---

## Custom Action Buttons

### Custom Row Action

```php
$container->action('', '操作')
    ->actions(function (Table\ColumnType\ActionsContainer $container) {
        // View detail button
        $container->button('查看')
            ->setProps(['type' => 'link', 'size' => 'small'])
            ->modal((new Modal())
                ->setWidth('600px')
                ->setUrl(U('detail', ['id' => '__id__']))
                ->setTitle('详情'));

        // Custom action with confirmation
        $container->button('审核')
            ->setProps(['type' => 'link', 'size' => 'small'])
            ->request('post', U('audit', ['id' => '__id__']))
            ->setConfirm('确定要审核通过吗？');

        // Conditional button
        $container->button('发货')
            ->setProps(['type' => 'link', 'size' => 'small'])
            ->request('post', U('ship', ['id' => '__id__']))
            ->setShowCondition([
                'field' => 'status',
                'operator' => 'eq',
                'value' => 1  // Only show when status = 1
            ]);
    });
```

### Custom Top Action

```php
$table->actions(function (Table\ActionsContainer $container) {
    // Custom export button
    $container->button('导出Excel')
        ->setProps(['type' => 'default'])
        ->request('get', U('export'))
        ->setDownload(true);

    // Batch operation with selection
    $container->button('批量审核')
        ->setProps(['type' => 'primary'])
        ->request('post', U('batchAudit'))
        ->setConfirm('确定要批量审核通过吗？')
        ->setRequireSelection(true, '请选择要审核的记录');

    // Custom modal button
    $container->button('批量导入')
        ->setProps(['type' => 'default'])
        ->modal((new Modal())
            ->setWidth('500px')
            ->setUrl(U('importForm'))
            ->setTitle('批量导入'));
});
```

---

## Common Patterns

### Multi-Column Display

```php
$container->text('product_info', '商品信息')
    ->setRender(function($value, $row) {
        return sprintf(
            '<div class="product-info">
                <div class="product-name"><strong>%s</strong></div>
                <div class="product-code text-muted">编码: %s</div>
                <div class="product-price text-danger">¥%s</div>
            </div>',
            $row['name'],
            $row['code'],
            number_format($row['price'], 2)
        );
    });
```

### Progress Bar

```php
$container->text('progress', '进度')
    ->setRender(function($value, $row) {
        $percent = min(100, max(0, $row['progress']));
        $color = $percent >= 80 ? 'success' : ($percent >= 50 ? 'warning' : 'exception');
        return sprintf(
            '<div class="ant-progress ant-progress-line">
                <div class="ant-progress-outer">
                    <div class="ant-progress-inner">
                        <div class="ant-progress-bg" style="width: %d%%; background-color: var(--ant-%s-color);"></div>
                    </div>
                </div>
                <span class="ant-progress-text">%d%%</span>
            </div>',
            $percent, $color, $percent
        );
    });
```

### Rating Stars

```php
$container->text('rating', '评分')
    ->setRender(function($value, $row) {
        $rating = $row['rating'];
        $stars = '';
        for ($i = 1; $i <= 5; $i++) {
            if ($i <= $rating) {
                $stars .= '<span class="anticon anticon-star" style="color: #fadb14;"></span>';
            } else {
                $stars .= '<span class="anticon anticon-star" style="color: #d9d9d9;"></span>';
            }
        }
        return $stars . ' <span class="text-muted">' . $rating . '</span>';
    });
```

### Avatar with Name

```php
$container->text('user', '用户')
    ->setRender(function($value, $row) {
        $user = D('User')->find($row['user_id']);
        if (!$user) return '未知';

        $avatar = !empty($user['avatar'])
            ? get_image_url($user['avatar'])
            : 'https://ui-avatars.com/api/?name=' . urlencode($user['name']);

        return sprintf(
            '<div style="display: flex; align-items: center;">
                <img src="%s" style="width: 32px; height: 32px; border-radius: 50%; margin-right: 8px;">
                <span>%s</span>
            </div>',
            $avatar, $user['name']
        );
    });
```

### Tags Display

```php
$container->text('tags', '标签')
    ->setRender(function($value, $row) {
        $tag_ids = explode(',', $row['tag_ids']);
        $tags = D('Tag')->where(['id' => ['in', $tag_ids]])->select();

        $html = '';
        foreach ($tags as $tag) {
            $color = $tag['color'] ?? 'blue';
            $html .= sprintf(
                '<span class="ant-tag ant-tag-%s" style="margin-bottom: 4px;">%s</span> ',
                $color, $tag['name']
            );
        }
        return $html ?: '<span class="text-muted">无标签</span>';
    });
```

---

## Custom Form Layout

### Grouping Fields

```php
$form->columns(function (Form\ColumnsContainer $columns) {
    // Basic Info Group (full width)
    $columns->text('name', '商品名称')
        ->addRule(new Required())
        ->setFormItemWidth(24);

    $columns->text('code', '商品编码')
        ->addRule(new Required())
        ->setFormItemWidth(12);

    $columns->select('cate_id', '分类')
        ->setValueEnum(D('Category')->getField('id,name'))
        ->setFormItemWidth(12);

    // Price Group (half width each)
    $columns->number('price', '价格')
        ->setFormItemWidth(12);

    $columns->number('stock', '库存')
        ->setFormItemWidth(12);

    // Rich Text (full width)
    $columns->ueditor('content', '商品详情')
        ->setFormItemWidth(24);
});
```

### Width Grid Reference

| Width | Percentage | Use Case |
|-------|------------|----------|
| 24 | 100% | Full width (titles, content) |
| 12 | 50% | Half width (paired fields) |
| 8 | 33.3% | One third |
| 6 | 25% | Quarter (small fields) |

---

## Related Rules

- [AntdAdmin Components](../antdadmin.md) - Complete component reference
- [Table Columns v14](crud-table-columns-v14.md) - Column types
- [Form Validation](crud-form-validation.md) - Validation rules
- [CRUD Batch Actions](crud-batch-actions.md) - Batch operations

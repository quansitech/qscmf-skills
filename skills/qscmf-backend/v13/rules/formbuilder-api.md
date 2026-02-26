---
title: FormBuilder API Reference (v13)
impact: CRITICAL
impactDescription: Core API for form creation in v13 (100% usage)
tags: api, formbuilder, form, v13, core
---

## FormBuilder API Reference (v13)

The FormBuilder API is used for creating add/edit forms in QSCMF v13 admin panels.

### When to Use This Rule

- Creating add/edit forms in v13
- Configuring form field types
- Adding validation rules
- Setting up form callbacks

---

## Quick Reference

### Core Method

```php
$builder->addFormItem($name, $type, $title, $options = '', $require = false);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `$name` | string | Field name (database column) |
| `$type` | string | Field type (text, select, etc.) |
| `$title` | string | Display label |
| `$options` | mixed | Options array or placeholder text |
| `$require` | bool | Whether field is required |

---

## Form Field Types

### 1. Text Input

```php
$builder->addFormItem('name', 'text', '名称', '请输入名称');

// Required field
$builder->addFormItem('code', 'text', '编码', '请输入编码', true);
```

### 2. Textarea

```php
$builder->addFormItem('description', 'textarea', '描述', '请输入描述');

// With options
$builder->addFormItem('content', 'textarea', '内容', [
    'rows' => 5,
    'placeholder' => '请输入内容'
]);
```

### 3. Rich Text Editor (UEditor)

```php
$builder->addFormItem('content', 'editor', '内容');
$builder->addFormItem('article_content', 'ueditor', '文章内容');
```

### 4. Select Dropdown

```php
// Static options
$builder->addFormItem('status', 'select', '状态', [1 => '启用', 0 => '禁用']);

// Using DBCont
$builder->addFormItem('status', 'select', '状态', DBCont::getStatusList());

// From model
$builder->addFormItem('cate_id', 'select', '分类', D('Category')->getFieldOptions());

// With empty option
$builder->addFormItem('cate_id', 'select', '分类', ['' => '请选择'] + D('Category')->getFieldOptions());
```

### 5. Radio Buttons

```php
$builder->addFormItem('status', 'radio', '状态', [1 => '启用', 0 => '禁用']);

// Using DBCont
$builder->addFormItem('is_show', 'radio', '是否显示', DBCont::getBoolStatusList());
```

### 6. Checkbox Group

```php
$builder->addFormItem('tags', 'checkbox', '标签', [
    1 => '标签一',
    2 => '标签二',
    3 => '标签三'
]);

// From model
$builder->addFormItem('role_ids', 'checkbox', '角色', D('Role')->getFieldOptions());
```

### 7. Date Picker

```php
$builder->addFormItem('publish_date', 'date', '发布日期');

// With format
$builder->addFormItem('start_date', 'date', '开始日期', ['format' => 'Y-m-d']);
```

### 8. DateTime Picker

```php
$builder->addFormItem('publish_time', 'datetime', '发布时间');

// With options
$builder->addFormItem('create_time', 'datetime', '创建时间', [
    'format' => 'Y-m-d H:i:s'
]);
```

### 9. Time Picker

```php
$builder->addFormItem('start_time', 'time', '开始时间');
```

### 10. Image Upload

```php
// Single image
$builder->addFormItem('cover', 'picture', '封面图');

// With crop
$builder->addFormItem('cover_id', 'picture', '封面图', [
    'crop' => '866/490'
]);

// With tips
$builder->addFormItem('avatar', 'picture', '头像', [
    'tips' => '推荐尺寸: 200x200'
]);
```

### 11. Multiple Images Upload

```php
$builder->addFormItem('images', 'pictures', '图片集');

// With limit
$builder->addFormItem('gallery', 'pictures', '相册', [
    'limit' => 9
]);
```

### 12. File Upload

```php
// Single file
$builder->addFormItem('attachment', 'file', '附件');

// With allowed types
$builder->addFormItem('document', 'file', '文档', [
    'exts' => 'doc,docx,pdf,xls,xlsx'
]);
```

### 13. Multiple Files Upload

```php
$builder->addFormItem('attachments', 'files', '附件集');
```

### 14. Number Input

```php
$builder->addFormItem('sort', 'num', '排序');

// With range
$builder->addFormItem('price', 'num', '价格', [
    'min' => 0,
    'max' => 999999,
    'step' => 0.01
]);
```

### 15. Password Input

```php
$builder->addFormItem('password', 'password', '密码');
$builder->addFormItem('confirm_password', 'password', '确认密码');
```

### 16. Hidden Field

```php
$builder->addFormItem('id', 'hidden', '');
$builder->addFormItem('is_submit', 'hidden', 1);
```

### 17. Color Picker

```php
$builder->addFormItem('color', 'color', '颜色');
```

### 18. District (Address)

```php
$builder->addFormItem('address', 'district', '地区');
```

---

## Form Configuration

### Set Form Data (Edit Mode)

```php
public function edit()
{
    $id = I('get.id', 0, 'intval');
    $data = D('Product')->find($id);

    $builder = $this->builder();
    $this->buildFormItems($builder);
    $builder->setData($data);
    $builder->display();
}
```

### Form Layout

```php
// Group fields
$builder->addGroupField('basic', '基本信息', [
    'name' => 'text',
    'code' => 'text'
]);

// Tab layout
$builder->setFormTabs([
    ['title' => '基本信息', 'fields' => ['name', 'code']],
    ['title' => '详细内容', 'fields' => ['content', 'images']]
]);
```

---

## Validation Rules

### In Controller

```php
// Required validation via parameter
$builder->addFormItem('name', 'text', '名称', '请输入名称', true);
```

### In Model

```php
protected $_validate = [
    // Required
    ['name', 'require', '名称不能为空', self::MUST_VALIDATE],

    // Length
    ['name', '1,200', '名称长度不正确', self::VALUE_VALIDATE, 'length'],

    // Email
    ['email', 'email', '邮箱格式不正确', self::VALUE_VALIDATE],

    // URL
    ['url', 'url', 'URL格式不正确', self::VALUE_VALIDATE],

    // Unique
    ['code', 'unique', '编码已存在', self::MUST_VALIDATE],

    // In list
    ['status', [0, 1, 2], '状态值不正确', self::VALUE_VALIDATE, 'in'],

    // Regex
    ['phone', '/^1[3-9]\d{9}$/', '手机号格式不正确', self::VALUE_VALIDATE, 'regex'],

    // Callback
    ['custom_field', 'checkCustom', '自定义验证失败', self::MUST_VALIDATE, 'callback'],
];
```

---

## Form Callbacks

### Before Save

```php
protected function save()
{
    $data = I('post.');

    // Pre-process data
    if (isset($data['tags']) && is_array($data['tags'])) {
        $data['tags'] = implode(',', $data['tags']);
    }

    // Generate slug
    if (empty($data['slug'])) {
        $data['slug'] = $this->generateSlug($data['name']);
    }

    $result = parent::save($data);

    if ($result !== false) {
        $this->success('保存成功', U('index'));
    } else {
        $this->error('保存失败');
    }
}
```

### After Save

```php
protected function save()
{
    $data = I('post.');
    $is_new = empty($data['id']);

    $result = parent::save($data);

    if ($result !== false) {
        $id = $is_new ? $result : $data['id'];

        // Sync related data
        if (isset($data['tags'])) {
            D('ProductTag')->syncTags($id, $data['tags']);
        }

        // Clear cache
        D('Product')->clearCache($id);

        $this->success('保存成功', U('index'));
    }
}
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

    public function add()
    {
        $builder = $this->builder();
        $this->buildFormItems($builder);
        $builder->addFormItem('is_submit', 'hidden', 1);
        $builder->display();
    }

    public function edit()
    {
        $id = I('get.id', 0, 'intval');
        $data = D('Product')->find($id);

        if (!$data) {
            $this->error('记录不存在');
        }

        $builder = $this->builder();
        $this->buildFormItems($builder);
        $builder->setData($data);
        $builder->display();
    }

    protected function buildFormItems($builder)
    {
        // Basic info
        $builder->addFormItem('product_name', 'text', '商品名称', '请输入商品名称', true);
        $builder->addFormItem('product_code', 'text', '商品编码', '请输入编码');

        // Category
        $builder->addFormItem('cate_id', 'select', '分类', D('Category')->getFieldOptions());

        // Images
        $builder->addFormItem('cover', 'picture', '封面图', ['crop' => '16/9']);
        $builder->addFormItem('images', 'pictures', '图片集', ['limit' => 9]);

        // Price and stock
        $builder->addFormItem('price', 'num', '价格', ['min' => 0, 'step' => 0.01]);
        $builder->addFormItem('stock', 'num', '库存', ['min' => 0]);

        // Content
        $builder->addFormItem('summary', 'textarea', '摘要');
        $builder->addFormItem('content', 'editor', '详情内容');

        // Status
        $builder->addFormItem('sort', 'num', '排序');
        $builder->addFormItem('status', 'radio', '状态', DBCont::getStatusList());
    }

    public function save()
    {
        $data = I('post.');

        // Validation
        if (empty($data['product_name'])) {
            $this->error('商品名称不能为空');
        }

        // Process images
        if (isset($data['images']) && is_array($data['images'])) {
            $data['images'] = implode(',', $data['images']);
        }

        $result = parent::save($data);

        if ($result !== false) {
            $this->success('保存成功', U('index'));
        } else {
            $this->error('保存失败: ' . D('Product')->getError());
        }
    }
}
```

---

## Related Rules

- [ListBuilder API](listbuilder-api.md) - Table configuration
- [Form Validation](crud/crud-form-validation.md) - Detailed validation rules
- [Table Columns v13](crud/crud-table-columns-v13.md) - Column configuration

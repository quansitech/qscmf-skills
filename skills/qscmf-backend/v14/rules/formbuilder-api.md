# FormBuilder API Reference

Complete reference for the FormBuilder API used in QSCMF for building admin forms.

## API Choice in v14

QSCMF v14 supports TWO form APIs:

1. **AntdAdmin Component API** (recommended for new projects)
   - Use: `new \AntdAdmin\Component\Form()`
   - See: [antdadmin.md](antdadmin.md)

2. **FormBuilder API** (legacy, backward compatible)
   - Use: `new \Qscmf\Builder\FormBuilder()`
   - Rendering: jQuery or React (controlled by `ANTD_ADMIN_BUILDER_ENABLE`)

This document covers the **FormBuilder API** (legacy).

---

## Core Methods

### Form Configuration

| Method | Parameters | Description |
|--------|-----------|-------------|
| `setMetaTitle($title)` | string | Set page title |
| `setPostUrl($url)` | string | Set form submission URL |
| `setFormData($data)` | array | Set form data (for edit) |
| `setShowBtn($show)` | bool | Show/hide submit button |
| `setNIDByNode($module, $controller, $action)` | string, string, string | Set permission node |
| `display()` | - | Render the form |

### Form Items

```php
$builder->addFormItem($name, $type, $title, $options, $required, $extra);
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `$name` | string | Field name |
| `$type` | string | Field type (see below) |
| `$title` | string | Field label |
| `$options` | mixed | Type-specific options |
| `$required` | bool | Is required field |
| `$extra` | string | Extra attributes |

### Field Types

| Type | Description | Options Format |
|------|-------------|----------------|
| `text` | Text input | Placeholder string |
| `textarea` | Multi-line text | Placeholder string |
| `editor` / `ueditor` | Rich text editor | - |
| `select` | Dropdown select | Array of options |
| `radio` | Radio buttons | Array of options |
| `checkbox` | Checkbox group | Array of options |
| `date` | Date picker | Format string |
| `time` | Time picker | Format string |
| `datetime` | DateTime picker | Format string |
| `picture` | Single image upload | - |
| `pictures` | Multiple image upload | - |
| `file` | File upload | - |
| `files` | Multiple file upload | - |
| `num` | Number input | - |
| `hidden` | Hidden field | Default value |
| `password` | Password input | - |
| `color` | Color picker | - |
| `linkage` | Linkage select | Configuration array |
| `distpicker` | District picker | Configuration array |

---

## Form Item Configuration

### Text Input

```php
// Basic text input
$builder->addFormItem('product_name', 'text', '商品名称');

// With placeholder
$builder->addFormItem('product_name', 'text', '商品名称', '请输入商品名称');

// Required field
$builder->addFormItem('product_name', 'text', '商品名称', '请输入商品名称', true);

// With extra attributes
$builder->addFormItem('product_name', 'text', '商品名称', '', false, 'maxlength="100"');
```

### Select Dropdown

```php
// Static options
$builder->addFormItem('status', 'select', '状态', [
    1 => '启用',
    0 => '禁用'
]);

// From model
$builder->addFormItem('cate_id', 'select', '分类', D('Category')->getField('id,name'));

// With placeholder
$builder->addFormItem('cate_id', 'select', '分类', ['' => '请选择分类'] + D('Category')->getField('id,name'));
```

### Radio Buttons

```php
$builder->addFormItem('status', 'radio', '状态', [
    1 => '启用',
    0 => '禁用'
]);
```

### Checkbox Group

```php
$builder->addFormItem('tags', 'checkbox', '标签', [
    'tag1' => '标签1',
    'tag2' => '标签2',
    'tag3' => '标签3'
]);
```

### Date/DateTime Picker

```php
// Date picker
$builder->addFormItem('publish_date', 'date', '发布日期');

// DateTime picker
$builder->addFormItem('publish_time', 'datetime', '发布时间');
```

### Image Upload

```php
// Single image
$builder->addFormItem('cover', 'picture', '封面图');

// Multiple images
$builder->addFormItem('gallery', 'pictures', '图片集');
```

### File Upload

```php
// Single file
$builder->addFormItem('attachment', 'file', '附件');

// Multiple files
$builder->addFormItem('documents', 'files', '文档');
```

### Rich Text Editor

```php
$builder->addFormItem('content', 'editor', '内容');
// or
$builder->addFormItem('content', 'ueditor', '内容');
```

### Linkage Select

```php
$builder->addFormItem('city', 'linkage', '城市', [
    'table' => 'city',           // Data table
    'pid_field' => 'pid',        // Parent ID field
    'name_field' => 'name',      // Name field
    'level' => 3,                // Levels
    'default' => [$province, $city, $district]  // Default values
]);
```

---

## Form Submission

### Standard Form

```php
public function add()
{
    $builder = new \Qscmf\Builder\FormBuilder();
    $builder->setMetaTitle('新增')
        ->setPostUrl(U('add'))
        ->addFormItem('product_name', 'text', '商品名称', '', true)
        ->addFormItem('status', 'select', '状态', DBCont::getStatusList())
        ->setShowBtn(true);

    if (IS_POST) {
        $data = I('post.');
        $result = D('Product')->createAdd($data);
        if ($result === false) {
            $this->error(D('Product')->getError());
        }
        $this->success('添加成功', U('index'));
    } else {
        $builder->display();
    }
}
```

### Modal Form

```php
protected function buildAddModal()
{
    $modal = new \Qs\ModalButton\ModalButtonBuilder();
    return $modal
        ->bindFormBuilder($this->add($modal->getModalDom()))
        ->setTitle("新增")
        ->setBackdrop(false)
        ->setKeyboard(false);
}

public function add($modal_id = null)
{
    $builder = new \Qscmf\Builder\FormBuilder();
    $builder->setMetaTitle('新增')
        ->setPostUrl(U('add'))
        ->addFormItem('name', 'text', '名称', '', true)
        ->setShowBtn(true);

    if (IS_POST) {
        // Handle submission
    }

    return $builder;
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
        if (IS_POST) {
            $data = I('post.');

            $model = D('Product');
            $result = $model->createAdd($data);

            if ($result === false) {
                $this->error($model->getError());
            }

            $this->success('添加成功', U('index'));
        }

        $builder = new \Qscmf\Builder\FormBuilder();
        $builder->setMetaTitle('新增商品')
            ->setPostUrl(U('add'))
            ->addFormItem('product_name', 'text', '商品名称', '请输入商品名称', true)
            ->addFormItem('product_code', 'text', '商品编码', '请输入商品编码', true)
            ->addFormItem('cate_id', 'select', '分类', D('Category')->getFieldOptions())
            ->addFormItem('price', 'num', '价格')
            ->addFormItem('stock', 'num', '库存')
            ->addFormItem('cover', 'picture', '封面图')
            ->addFormItem('gallery', 'pictures', '图片集')
            ->addFormItem('description', 'textarea', '描述')
            ->addFormItem('content', 'editor', '详情')
            ->addFormItem('sort', 'num', '排序')
            ->addFormItem('status', 'radio', '状态', DBCont::getStatusList())
            ->setShowBtn(true)
            ->display();
    }

    public function edit()
    {
        $id = I('get.id', 0, 'intval');
        $data = D('Product')->find($id);

        if (!$data) {
            $this->error('记录不存在');
        }

        if (IS_POST) {
            $data = I('post.');
            $result = D('Product')->createSave($data);

            if ($result === false) {
                $this->error(D('Product')->getError());
            }

            $this->success('保存成功', U('index'));
        }

        $builder = new \Qscmf\Builder\FormBuilder();
        $builder->setMetaTitle('编辑商品')
            ->setPostUrl(U('edit', ['id' => $id]))
            ->setFormData($data)
            ->addFormItem('id', 'hidden', '', $id)
            ->addFormItem('product_name', 'text', '商品名称', '请输入商品名称', true)
            ->addFormItem('product_code', 'text', '商品编码', '请输入商品编码', true)
            ->addFormItem('cate_id', 'select', '分类', D('Category')->getFieldOptions())
            ->addFormItem('price', 'num', '价格')
            ->addFormItem('stock', 'num', '库存')
            ->addFormItem('cover', 'picture', '封面图')
            ->addFormItem('gallery', 'pictures', '图片集')
            ->addFormItem('description', 'textarea', '描述')
            ->addFormItem('content', 'editor', '详情')
            ->addFormItem('sort', 'num', '排序')
            ->addFormItem('status', 'radio', '状态', DBCont::getStatusList())
            ->setShowBtn(true)
            ->display();
    }
}
```

---

## Related Documentation

- [ListBuilder API](listbuilder-api.md) - List page building
- [AntdAdmin Components](antdadmin.md) - Modern React API (v14)
- [Form Validation](crud/crud-form-validation.md) - Validation rules

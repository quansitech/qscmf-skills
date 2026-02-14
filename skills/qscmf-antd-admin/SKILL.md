---
name: qscmf-antd-admin
description: Use when working with AntdAdmin UI components (Table, Form, Modal, Tabs) in QSCMF admin interfaces. Triggers include "Table列表", "Form表单", "Modal弹窗", "图片上传", "下拉选择", "富文本", "AntdAdmin" or issues like "搜索不工作", "上传失败", "Modal打不开". For Model/Controller/Migration use qscmf-backend instead.
---

# AntdAdmin Component Library

Component-based admin UI framework for QSCMF built on Ant Design.

**Core Pattern**: Container pattern with fluent interface

## Quick Start

### Table (Data Display)

```php
use AntdAdmin\Component\Table;

$table = new Table();
$table->setMetaTitle('产品列表')
      ->setDataSource($products)
      ->columns(function (Table\ColumnsContainer $container) {
          $container->text('id', 'ID')->setSearch(false);
          $container->text('name', '名称');
          $container->digit('price', '价格');
          $container->dateTime('created_at', '创建时间');
          $container->action('', '操作')->actions(function ($container) {
              $container->edit();
              $container->delete();
          });
      })
      ->actions(function (Table\ActionsContainer $container) {
          $container->addNew();
      })
      ->render();
```

### Form (Data Entry)

```php
use AntdAdmin\Component\Form;
use Qscmf\Core\Validator\Rule\Required;
use FormItem\ObjectStorage\Lib\Common;

$form = new Form();
$form->setMetaTitle('新增产品')
     ->setInitialValues($defaults)
     ->setSubmitRequest('post', U('add'))
     ->columns(function (Form\ColumnsContainer $container) {
         $container->text('name', '名称')->addRule(new Required());
         $container->digit('price', '价格');
         $container->image('cover_id', '封面图')
                   ->setUploadRequest(Common::genItemDataUrl('image'))
                   ->setCrop('16/9');
     })
     ->actions(function (Form\ActionsContainer $container) {
         $container->button('提交')->submit();
     })
     ->render();
```

### Modal Integration

```php
use AntdAdmin\Component\Modal\Modal;

$modal = new Modal();
$modal->setTitle('编辑')
      ->setContent(new Form(...))  // or setUrl(U('edit'))
      ->setWidth('800px');

$container->button('添加')->modal($modal);
```

### Tabs (Tabbed Interface)

```php
use AntdAdmin\Component\Tabs;
use AntdAdmin\Component\Form;

// Create forms for each tab
$basicForm = new Form();
$basicForm->columns(function ($container) {
    $container->text('name', '名称');
    $container->digit('price', '价格');
});

// Create tabs
$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', $basicForm)        // Direct content
     ->addTab('seo', 'SEO设置', null, U('seo'))       // URL-based (lazy load)
     ->addTab('logs', '操作日志', null, U('logs'))    // URL-based
     ->render();
```

**Use cases**:
- Multiple forms in one page
- Separate edit sections (basic info, SEO, settings)
- Mix forms and tables in tabs
- Lazy load content for performance

---

## Key Concepts

### Container Pattern
All nested elements use containers with closures:
```php
$table->columns(function (Table\ColumnsContainer $container) {
    $container->text('field', 'Label');
});
```

### Fluent Interface
All setter methods return `$this` for chaining:
```php
$container->text('name', '名称')
          ->setWidth(200)
          ->setSearch(false);
```

### Table vs Form Columns
- **Table**: For display, most types supported, search enabled by default
- **Form**: For input, all types supported, has validation
- **Difference**: `ueditor` only in Form, `link` only in Table

### Actions
- **Table actions**: Top-level batch operations (`$table->actions()`)
- **Row actions**: Per-row operations in action column
- **Shortcuts**: `addNew()`, `delete()`, `edit()`, `forbid()`, `resume()`

---

## Quick Decision Guide

### Which Component?

```
Display data? → Table
Add/Edit data? → Form
Need popup? → Modal
Multiple tabs? → Tabs
```

### Which Column Type?

```
Short text? → text
Long text? → textarea
Number? → digit
Date? → date / dateTime
Choice? → select / radio / checkbox
Image? → image (setUploadRequest + setCrop)
File? → file (setUploadRequest)
Rich text? → ueditor (Form only!)
Money? → money
```

### Which Action?

```
Simple CRUD? → Use shortcuts (addNew, delete, edit)
Custom link? → button()->link($url)
AJAX request? → button()->request($method, $url)
Modal popup? → button()->modal($modal)
Inline edit? → defaultEditMode() + editable()
```

---

## Common Mistakes

### ❌ Wrong Container Pattern
```php
// WRONG
$column = new Table\ColumnType\Text('id', 'ID');

// ✅ RIGHT
$table->columns(function ($container) {
    $container->text('id', 'ID');
});
```

### ❌ Missing Render
```php
// WRONG
return $table;

// ✅ RIGHT
return $table->render();
```

### ❌ Wrong Action Placement
```php
// WRONG: Actions in columns
$table->columns(function ($container) {
    $container->addNew();  // Wrong!
});

// ✅ RIGHT: Separate actions
$table->columns(...)
      ->actions(function ($container) {
          $container->addNew();  // Right
      });
```

### ❌ Wrong Select Setup
```php
// WRONG
$container->select('status', '状态')
          ->setFieldProps(['options' => [...]]);

// ✅ RIGHT
$container->select('status', '状态')
          ->setValueEnum([1 => '启用', 0 => '禁用']);
```

---

## Related Skills

### When to Use Which Skill?

| Task | Use This Skill |
|------|---------------|
| Create Model, Migration | qscmf-backend |
| Create Controller structure | qscmf-backend |
| Design database schema | qscmf-backend |
| Configure Table columns | **qscmf-antd-admin** (this) |
| Setup Form validation | **qscmf-antd-admin** (this) |
| Integrate Modal popup | **qscmf-antd-admin** (this) |
| Configure image upload | **qscmf-antd-admin** (this) |
| Setup action buttons | **qscmf-antd-admin** (this) |

---

## Troubleshooting

### Column not showing?
- ✅ Check `dataIndex` matches field name in data
- ✅ Ensure container closure syntax is correct
- ✅ Verify `setDataSource()` is called

### Search not working?
- ✅ `setSearchUrl()` must be set on table
- ✅ Column must not have `setSearch(false)`
- ✅ Server must handle query parameters (I('get.'))
- ✅ Check network request in browser console

### Modal not opening?
- ✅ Modal must be attached with `->modal($modal)` on button
- ✅ Check Modal has `setContent()` or `setUrl()`
- ✅ Verify URL is accessible (if using setUrl)
- ✅ Check browser console for errors

### Upload failing?
- ✅ Ensure `setUploadRequest()` is called with valid URL
- ✅ Check object-storage package is installed
- ✅ Verify upload policy endpoint works
- ✅ Check file size limits (php.ini, nginx config)

### Form not submitting?
- ✅ `setSubmitRequest()` must be set
- ✅ Check server endpoint accepts the method
- ✅ Verify button has `->submit()` action
- ✅ Check validation rules aren't blocking

**More troubleshooting**: See [troubleshooting.md](references/troubleshooting.md)

---

## Detailed References

### 📦 By Component

#### Table Component
- **Patterns**: [Table Patterns](references/patterns.md#table-patterns) - Search, CRUD actions, inline editing, tree tables
- **API**: [Table API](references/api-reference.md#table-api) - Core methods, search, pagination, editing
- **Troubleshooting**: [Table Issues](references/troubleshooting.md#table-issues) - Column not showing, search not working

#### Form Component
- **Patterns**: [Form Patterns](references/patterns.md#form-patterns) - Validation, image upload, dependencies, dynamic lists
- **API**: [Form API](references/api-reference.md#form-api) - Core methods, submission, validation
- **Troubleshooting**: [Form Issues](references/troubleshooting.md#form-issues) - Not submitting, validation, upload failing

#### Modal Component
- **Patterns**: [Modal Patterns](references/patterns.md#modal-patterns) - Form modal, URL modal, nested modals
- **API**: [Modal API](references/api-reference.md#modal-api) - Configuration, content setup

#### Tabs Component
- **Patterns**: [Tabs Patterns](references/patterns.md#tabs-patterns) - Basic tabs, lazy load, mixed content, tabs in modal
- **API**: [Tabs API](references/api-reference.md#tabs-api) - Tab configuration

---

### 📚 By Content Type

#### Column Types Reference
- **[Column Types](references/column-types.md)** - All 20+ column types
  - Basic: text, textarea, digit, password
  - Date/Time: date, dateTime, ranges
  - Selection: select, radio, checkbox, switch
  - Upload: image, file
  - Special: ueditor, area, cascader, money

#### API Documentation
- **[API Reference](references/api-reference.md)** - Complete API documentation
  - Table API: Core methods, search, pagination, editing
  - Form API: Core methods, submission, validation
  - Column API: Base methods, table-only, form-only
  - Action API: Shortcuts, button/link methods

#### Troubleshooting Guide
- **[Troubleshooting](references/troubleshooting.md)** - Common issues and solutions
  - Table issues: Column not showing, search not working, pagination problems
  - Form issues: Not submitting, validation, upload failing
  - Modal issues: Not opening, content not loading
  - Performance issues: Slow loading, N+1 queries
  - Security issues: XSS vulnerability

#### Advanced Patterns
- **[Advanced Patterns](references/patterns.md#advanced-patterns)** - Cross-component patterns
  - Permission-based actions
  - Batch operations with selection
  - Conditional rendering
  - Custom render values

---

## Integration with QSCMF

### Controller Pattern
```php
use Qscmf\Controller\QsListController;
use AntdAdmin\Component\Table;

class ProductController extends QsListController
{
    public function index()
    {
        $list = D('Product')->getList(I('get.'));
        $table = new Table();
        $table->setMetaTitle('产品管理')
              ->setDataSource($list['data'])
              ->setPagination(new Table\Pagination($list['total'], $list['per_page']))
              ->columns(...)
              ->actions(...)
              ->render();
    }
}
```

### Data Format
```php
// Table expects array of arrays
$data = [
    ['id' => 1, 'name' => 'Product 1'],
    ['id' => 2, 'name' => 'Product 2'],
];
$table->setDataSource($data);
```

### Image Upload
```php
use FormItem\ObjectStorage\Lib\Common;

$container->image('cover_id', '封面图')
          ->setUploadRequest(Common::genItemDataUrl('image'))
          ->setCrop('16/9');
```

---

## Official Docs

Located at `/mnt/www/antd-admin/doc/`:
- Table.md - Table component
- Form.md - Form component
- Columns.md - Column types
- Modal.md - Modal component
- Tabs.md - Tabs component
- Condition.md - Condition operators

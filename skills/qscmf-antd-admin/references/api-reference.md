# API Reference

Complete API documentation for AntdAdmin components.

## Table API

### Constructor

```php
$table = new Table();
```

### Core Methods

#### setMetaTitle(string $title)
Set page title displayed in browser.

```php
$table->setMetaTitle('产品列表');
```

---

#### setDataSource(array $data)
Set table data source.

```php
$table->setDataSource($products);
```

**Data format**: Array of arrays or objects with field names matching column dataIndex.

---

#### columns(Closure $callback)
Define table columns using container pattern.

```php
$table->columns(function (Table\ColumnsContainer $container) {
    $container->text('id', 'ID');
    $container->text('name', '名称');
});
```

**Required**: Yes

---

#### actions(Closure $callback)
Define table-level actions (batch operations).

```php
$table->actions(function (Table\ActionsContainer $container) {
    $container->addNew();
    $container->delete();
});
```

---

#### render()
Render the table component. **Must be called at the end**.

```php
return $table->render();
```

**Required**: Yes

---

### Search & Pagination

#### setSearchUrl(string $url)
Enable search and set search endpoint.

```php
$table->setSearchUrl(U('index'));
```

When set, search filters will be sent to this URL with GET parameters.

---

#### setSearch(bool $search)
Show or hide search bar.

```php
$table->setSearch(true);  // Show search
$table->setSearch(false); // Hide search
```

**Default**: true

---

#### setPagination(Pagination|false $pagination)
Configure pagination.

```php
use AntdAdmin\Component\Table\Pagination;

$table->setPagination(new Pagination($total, $pageSize));
$table->setPagination(false); // Disable pagination
```

---

#### setDefaultSearchValue(array $values)
Set default search filter values.

```php
$table->setDefaultSearchValue([
    'status' => 1,
    'category' => 'electronics'
]);
```

---

### Editing

#### defaultEditMode()
Enable inline editing mode by default.

```php
$table->defaultEditMode();
```

When enabled, editable columns will show edit inputs.

---

#### setRowKey(string $key)
Set row key field (default: 'id').

```php
$table->setRowKey('product_id');
```

Used for row selection and editing operations.

---

### Other

#### setDateFormatter(string $format)
Set date display format.

```php
$table->setDateFormatter('Y-m-d H:i:s');
```

---

#### setExpandable(array $config)
Configure tree/expandable rows.

```php
$table->setExpandable([
    'childrenColumnName' => 'children',
    'defaultExpandAllRows' => true
]);
```

See: [Ant Design Table expandable](https://ant.design/components/table-cn#expandable)

---

#### setDescription(string $html)
Add description above table.

```php
$table->setDescription('<p>提示信息</p>');
```

---

#### setExtraRenderValues(array $values)
Pass additional data to frontend.

```php
$table->setExtraRenderValues([
    'categories' => $categories,
    'customConfig' => $config
]);
```

---

#### setRowSelection(array $config)
Enable row selection.

```php
$table->setRowSelection([
    'type' => 'checkbox'
]);
```

---

## Form API

### Constructor

```php
$form = new Form();
```

### Core Methods

#### setMetaTitle(string $title)
Set page title.

```php
$form->setMetaTitle('新增产品');
```

---

#### setInitialValues(array $values)
Set form initial/default values.

```php
$form->setInitialValues([
    'name' => '默认名称',
    'status' => 1
]);
```

Used for edit forms to populate existing data.

---

#### setSubmitRequest(string $method, string $url, array $data = null, array $headers = null, array $afterAction = null)
Configure form submission.

```php
$form->setSubmitRequest('post', U('add'));
$form->setSubmitRequest('put', U('update', ['id' => $id]));
```

**Parameters**:
- `$method`: HTTP method (post, put, delete, etc.)
- `$url`: Submission URL
- `$data`: Extra data to send
- `$headers`: Custom headers
- `$afterAction`: Actions after submission (default: close modal + reload table)

---

#### columns(Closure $callback)
Define form fields.

```php
$form->columns(function (Form\ColumnsContainer $container) {
    $container->text('name', '名称');
    $container->digit('price', '价格');
});
```

**Required**: Yes

---

#### actions(Closure $callback)
Define form action buttons.

```php
$form->actions(function (Form\ActionsContainer $container) {
    $container->button('提交')->submit();
    $container->button('重置')->reset();
});
```

---

#### render()
Render the form. **Must be called at the end**.

```php
return $form->render();
```

**Required**: Yes

---

### Other

#### setReadonly(bool $readonly)
Make form read-only.

```php
$form->setReadonly(true);
```

---

#### setExtraRenderValues(array $values)
Pass additional data to frontend.

```php
$form->setExtraRenderValues([
    'categories' => $categories
]);
```

---

## Base Column API

Common methods available on all column types.

### Constructor

```php
$column = $container->text('dataIndex', 'Title');
```

**Parameters**:
- `$dataIndex`: Field name in data
- `$title`: Display label

---

### Common Methods

#### setWidth(string $width)
Set column width.

```php
$container->text('id', 'ID')->setWidth(60);
$container->text('name', 'Name')->setWidth('200px');
```

---

#### setFormItemProps(array $props)
Set Ant Design Form.Item properties.

```php
$container->text('name', '名称')
          ->setFormItemProps([
              'labelCol' => ['span' => 4],
              'wrapperCol' => ['span' => 20]
          ]);
```

See: [Ant Design Form.Item](https://ant.design/components/form-cn/#Form.Item)

---

#### setFieldProps(array $props)
Set field component properties.

```php
$container->digit('price', '价格')
          ->setFieldProps([
              'prefix' => '¥',
              'precision' => 2
          ]);
```

See component-specific docs (Input, Select, etc.)

---

#### setAuthNode(string $node)
Set permission node for access control.

```php
$container->text('secret', '机密信息')
          ->setAuthNode('view_secret');
```

---

### Table-Only Methods

#### setSearch(bool $search)
Enable/disable search for this column.

```php
$container->text('id', 'ID')->setSearch(false);  // Don't search ID
$container->text('name', 'Name');  // Searchable by default
```

---

#### editable(bool $edit)
Enable inline editing for this column.

```php
$container->digit('sort', '排序')->editable(true);
```

**Requires**: `$table->defaultEditMode()` to be set

---

### Form-Only Methods

#### setFormItemWidth(int $md, int $lg)
Set grid width for form item.

```php
$container->text('name', '名称')->setFormItemWidth(12);  // Half width
$container->ueditor('content', '内容')->setFormItemWidth(24);  // Full width
```

**Grid system**: 24 columns total

---

#### setTips(string $tips)
Add help text below field.

```php
$container->text('password', '密码')
          ->setTips('密码长度至少8位');
```

---

#### readonly()
Make field read-only.

```php
$container->text('created_at', '创建时间')->readonly();
```

---

#### addRule(Rule $rule)
Add validation rule.

```php
use Qscmf\Core\Validator\Rule\Required;

$container->text('title', '标题')
          ->addRule(new Required());
```

---

## Action API

### Table Actions (Top Level)

#### Shortcuts

```php
$container->addNew();     // Add new button
$container->delete();     // Batch delete
$container->forbid();     // Batch disable
$container->resume();     // Batch enable
$container->editSave();   // Edit + save
```

---

#### button(string $title)
Create custom button.

```php
$action = $container->button('自定义按钮');
```

**Returns**: Button action object

---

#### startEditable(string $title)
Create editable mode trigger button.

```php
$container->startEditable('批量编辑')
          ->saveRequest('put', U('batchUpdate'));
```

---

### Row Actions (Per Row)

#### Shortcuts

```php
$container->edit();     // Edit row
$container->delete();   // Delete row
$container->forbid();   // Disable row
$container->resume();   // Enable row
```

---

#### link(string $title)
Create link action.

```php
$action = $container->link('查看详情');
```

**Returns**: Link action object

---

### Button/Link Methods

#### setHref(string $url)
Set link URL (Link actions only).

```php
$container->link('编辑')
          ->setHref(U('edit', ['id' => '__id__']));
```

Supports `__fieldName__` placeholders for row data.

---

#### link(string $url)
Set link URL (Button actions only).

```php
$container->button('添加')
          ->link(U('add'));
```

---

#### request(string $method, string $url, array $data = null, array $headers = null, string $confirm = '')
Set AJAX request action.

```php
$container->button('导出')
          ->request('post', U('export'), [], [], '确定导出吗？');

$container->link('删除')
          ->request('delete', U('delete'), ['id' => '__id__']);
```

**Supports placeholders**: `__fieldName__` in $url and $data

---

#### modal(Modal $modal)
Open modal on click.

```php
$modal = new Modal();
$modal->setTitle('编辑')->setUrl(U('edit'));

$container->link('编辑')->modal($modal);
```

---

#### saveRequest(string $method, string $url, array $data = null)
Set save request for editable mode.

```php
$container->startEditable('批量编辑')
          ->saveRequest('put', U('batchUpdate'));
```

---

#### relateSelection()
Use selected rows in request.

```php
$container->button('批量删除')
          ->relateSelection()
          ->request('post', U('batchDelete'));
```

---

#### setShowCondition(string $field, string $operator, mixed $value)
Conditionally show action.

```php
$container->link('审核')
          ->setShowCondition('status', 'eq', DBCont::AUDIT_STATUS);

$container->link('删除')
          ->setShowCondition('is_deletable', 'neq', 0);
```

**Operators**: `eq`, `=`, `neq`, `!=`, `<>`, `gt`, `>`, `gte`, `>=`, `lt`, `<`, `lte`, `<=`, `in`, `not in`

---

#### setAuthNode(string $node)
Set permission node.

```php
$container->edit()->setAuthNode('product_edit');
```

---

#### setBadge(string $badge)
Set badge text.

```php
$container->link('新功能')->setBadge('NEW');
```

---

#### setProps(array $props)
Set button properties.

```php
$container->button('提交')
          ->setProps([
              'type' => 'primary',
              'danger' => true
          ]);
```

See: [Ant Design Button](https://ant.design/components/button-cn/#API)

---

## Modal API

### Constructor

```php
use AntdAdmin\Component\Modal\Modal;

$modal = new Modal();
```

---

### Methods

#### setTitle(string $title)
Set modal title.

```php
$modal->setTitle('编辑产品');
```

---

#### setWidth(string $width)
Set modal width.

```php
$modal->setWidth('800px');
$modal->setWidth('80%');
```

---

#### setContent(Renderable $component)
Set modal content (Form, Table, or Tabs).

```php
$form = new Form();
$modal->setContent($form);
```

**Accepts**: Form, Table, Tabs components

---

#### setUrl(string $url)
Set URL to load content lazily.

```php
$modal->setUrl(U('edit', ['id' => '__id__']));
```

**Supports placeholders**: `__fieldName__`

**Advantages**:
- Lazy loads content
- Can use row data
- Better for large forms

---

## Tabs API

### Constructor

```php
use AntdAdmin\Component\Tabs;

$tabs = new Tabs();
```

---

### Methods

#### addTab(string $key, string $title, Renderable $pane = null, string $url = null)
Add a tab.

```php
// Direct content
$tabs->addTab('basic', '基本信息', $form);

// URL-based (lazy load)
$tabs->addTab('logs', '操作日志', null, U('logs'));
```

**Parameters**:
- `$key`: Unique tab identifier
- `$title`: Tab title
- `$pane`: Content component (Form, Table)
- `$url`: URL to load content

---

#### render()
Render tabs. **Must be called at the end**.

```php
return $tabs->render();
```

---

## Pagination API

### Constructor

```php
use AntdAdmin\Component\Table\Pagination;

$pagination = new Pagination(int $total, int $pageSize);
```

```php
$pagination = new Pagination(100, 20);
```

---

## Common Interfaces

### Renderable Interface

All components implement this interface.

```php
interface Renderable {
    public function render();
}
```

---

### PaneInterface

Components that can be used as tab panes (Form, Table, Tabs).

---

### ModalPropsInterface

Components that can be used in modals (Form, Table, Tabs).

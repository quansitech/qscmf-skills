# QSCMF Core Concepts

This document explains the fundamental concepts shared across QSCMF versions, with clear distinctions between rendering modes.

## API Overview

QSCMF has **two different UI builder APIs** depending on the rendering mode:

| Mode | Primary API | Namespace | Rendering |
|------|-------------|-----------|-----------|
| **jQuery Mode** | ListBuilder | `\Qscmf\Builder\ListBuilder` | jQuery + Bootstrap |
| **React Mode** | AntdAdmin Component | `\AntdAdmin\Component\Table` | React + Ant Design |
| **React Mode** | ListBuilder (legacy) | `\Qscmf\Builder\ListBuilder` | jQuery (backward compat) |

---

## jQuery Mode API: ListBuilder

ListBuilder is the primary UI builder for jQuery mode. It provides a fluent API for creating admin data tables with jQuery rendering.

### Basic Usage (jQuery Mode)

```php
use Qscmf\Builder\ListBuilder;

public function index() {
    $model = D('Product');
    $count = $model->getListForCount([]);
    $page = new \Gy_Library\GyPage($count, 20);
    $data_list = $model->getListForPage([], $page->nowPage, $page->listRows, 'id desc');

    $builder = new ListBuilder();
    $builder->setMetaTitle('Product List')
        // Table columns
        ->addTableColumn('id', 'ID')
        ->addTableColumn('name', 'Name')
        ->addTableColumn('status', 'Status', 'status')
        ->addTableColumn('create_time', 'Created', 'time')
        // Top buttons
        ->addTopButton('addnew', ['title' => 'Add Product', 'href' => U('add')])
        // Right buttons (per-row actions)
        ->addRightButton('edit')
        ->addRightButton('delete')
        // Search items
        ->addSearchItem('keyword', 'text', 'Search by name')
        ->addSearchItem('status', 'select', 'Status', [1 => 'Active', 0 => 'Inactive'])
        // Data and pagination
        ->setTableDataList($data_list)
        ->setTableDataPage($page->show())
        ->build();
}
```

### ListBuilder Key Methods

| Method | Purpose |
|--------|---------|
| `setMetaTitle($title)` | Set page title |
| `addTableColumn($name, $title, $type, $value, ...)` | Add table column |
| `addTopButton($type, $attribute, ...)` | Add toolbar button |
| `addRightButton($type, $attribute, ...)` | Add row action button |
| `addSearchItem($name, $type, $title, $options, ...)` | Add search filter |
| `setCheckBox($enable, $callback)` | Enable row checkboxes |
| `setTableDataList($data)` | Set data rows |
| `setTableDataPage($pagination)` | Set pagination HTML |
| `setSearchUrl($url)` | Set search form action URL |
| `setLockRow($rows)` | Lock table rows (freeze) |
| `setLockCol($cols)` | Lock table columns (freeze left) |
| `setLockColRight($cols)` | Lock table columns (freeze right) |
| `build()` | Render the table |

### ListBuilder Column Types

| Type | Description | Usage |
|------|-------------|-------|
| `null` (default) | Plain text | `->addTableColumn('name', 'Name')` |
| `status` | Status badge | `->addTableColumn('status', 'Status', 'status')` |
| `date` | Date format | `->addTableColumn('date', 'Date', 'date', 'Y-m-d')` |
| `time` | DateTime format | `->addTableColumn('create_time', 'Created', 'time')` |
| `picture` | Single image | `->addTableColumn('cover', 'Cover', 'picture')` |
| `pictures` | Multiple images | `->addTableColumn('images', 'Images', 'pictures')` |
| `icon` | Icon display | `->addTableColumn('icon', 'Icon', 'icon')` |
| `num` | Number with format | `->addTableColumn('price', 'Price', 'num')` |
| `btn` | Right button column | `->addTableColumn('right_button', 'Actions', 'btn')` |
| `fun` | Custom callback | `->addTableColumn('custom', 'Custom', 'fun', function($data){...})` |
| `self` | Self-defined | `->addTableColumn('link', 'Link', 'self', ['href' => '...'])` |

### Top Button Types

| Type | Description | Default Title |
|------|-------------|---------------|
| `addnew` | Add new button | "Add" |
| `delete` | Batch delete | "Delete" |
| `modal` | Modal dialog | Custom |
| `self` | Custom button | Custom |

### Right Button Types

| Type | Description | Default Title |
|------|-------------|---------------|
| `edit` | Edit button | "Edit" |
| `delete` | Delete button | "Delete" |
| `forbid` | Disable button | "Disable" |
| `resume` | Enable button | "Enable" |
| `self` | Custom button | Custom |

### Search Item Types

| Type | Description | Usage |
|------|-------------|-------|
| `text` | Text input | `->addSearchItem('keyword', 'text', 'Search')` |
| `select` | Dropdown select | `->addSearchItem('status', 'select', 'Status', $options)` |
| `select_text` | Select or text | Combined search |
| `date` | Date picker | `->addSearchItem('date', 'date', 'Date')` |
| `date_range` | Date range picker | `->addSearchItem('date_range', 'date_range', 'Date Range')` |
| `hidden` | Hidden field | `->addSearchItem('id', 'hidden', '', $value)` |
| `select_city` | City selector | Province/City/District |

### Placeholders in Buttons

Use `__field_name__` to reference row data:

```php
->addRightButton('self', [
    'title' => 'View Details',
    'href' => U('detail', ['id' => '__id__', 'name' => '__name__'])
])
```

---

## React Mode API: AntdAdmin Component

React mode introduces a **new React-based API** using `\AntdAdmin\Component\Table`. This is the primary API for new projects using React rendering.

### Basic Usage (React Mode)

```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;
use AntdAdmin\Component\Table\ActionsContainer;
use AntdAdmin\Component\Table\ColumnsContainer;

public function index() {
    $model = D('Product');
    $count = $model->getListForCount([]);
    $page = I('get.page', 1);
    $limit = I('get.limit', 20);
    $data_list = $model->getListForPage([], $page, $limit, 'id desc');

    $table = new Table();
    $table->setMetaTitle('Product List')
        ->actions(function (ActionsContainer $container) {
            $container->button('Add Product')
                ->setProps(['type' => 'primary'])
                ->modal((new \AntdAdmin\Component\Modal\Modal())
                    ->setTitle('Add Product')
                    ->setUrl(U('add')));
        })
        ->columns(function (ColumnsContainer $container) {
            $container->text('id', 'ID');
            $container->text('name', 'Name');
            $container->status('status', 'Status');
            $container->date('create_time', 'Created');

            $container->action('', '操作')->actions(function ($container) {
                $container->edit();
                $container->delete();
            });
        })
        ->setDataSource($data_list)
        ->setPagination(new Pagination($page, $limit, $count))
        ->setSearch(false)
        ->render();
}
```

### AntdAdmin Component Key Methods

| Method | Purpose |
|--------|---------|
| `setMetaTitle($title)` | Set page title |
| `actions(function($container){})` | Define toolbar buttons |
| `columns(function($container){})` | Define table columns |
| `setDataSource($data)` | Set data rows |
| `setPagination($pagination)` | Set pagination object |
| `setSearch($enable)` | Enable/disable search |
| `render()` | Render the table (returns Inertia response) |

### AntdAdmin Column Types

| Method | Description | Usage |
|--------|-------------|-------|
| `text($name, $title)` | Plain text | `$container->text('name', 'Name')` |
| `status($name, $title)` | Status badge | `$container->status('status', 'Status')` |
| `date($name, $title)` | Date format | `$container->date('create_time', 'Created')` |
| `money($name, $title)` | Money format | `$container->money('price', 'Price')` |
| `number($name, $title)` | Number format | `$container->number('count', 'Count')` |
| `picture($name, $title)` | Image display | `$container->picture('cover', 'Cover')` |
| `action($name, $title)` | Action column | `$container->action('', '操作')` |

### AntdAdmin Action Types

```php
$container->action('', '操作')->actions(function ($container) {
    $container->edit();                    // Edit button
    $container->delete();                  // Delete button
    $container->button('Custom')           // Custom button
        ->setProps(['type' => 'primary'])
        ->setHref(U('custom', ['id' => '__id__']));
});
```

---

## FormBuilder

Both modes use `FormBuilder` for admin forms, but React mode also has a new React-based form API.

### FormBuilder (Legacy API)

```php
use Qscmf\Builder\FormBuilder;

public function add() {
    if (IS_POST) {
        $data = I('post.');
        $result = D('Product')->createAdd($data);
        if ($result === false) {
            $this->error(D('Product')->getError());
        }
        $this->success('Added successfully', U('index'));
    } else {
        $builder = new FormBuilder();
        $builder->setPostUrl(U('add'))
            ->addFormItem('name', 'text', 'Product Name')
            ->addFormItem('category_id', 'select', 'Category', $category_options)
            ->addFormItem('price', 'num', 'Price')
            ->addFormItem('description', 'textarea', 'Description')
            ->addFormItem('cover', 'picture', 'Cover Image')
            ->addFormItem('status', 'radio', 'Status', [1 => 'Active', 0 => 'Inactive'])
            ->setFormData(['status' => 1])
            ->setShowBtn(true);

        return $builder->build();
    }
}
```

### React Mode Form (Modern API)

```php
use AntdAdmin\Component\Form;
use AntdAdmin\Component\ColumnType\RuleType\Required;

public function add() {
    if (IS_POST) {
        $data = I('post.');
        $result = D('Product')->createAdd($data);
        if ($result === false) {
            $this->error(D('Product')->getError());
        }
        $this->success('Added successfully');
    } else {
        $form = new Form();
        $form->setSubmitRequest('post', U('add'))
            ->setInitialValues(['status' => 1])
            ->columns(function (Form\ColumnsContainer $columns) use ($category_options) {
                $columns->text('name', 'Product Name')
                    ->addRule(new Required())
                    ->setFormItemWidth(24);
                $columns->select('category_id', 'Category')
                    ->setOptions($category_options)
                    ->setFormItemWidth(24);
                $columns->money('price', 'Price')
                    ->addRule(new Required())
                    ->setFormItemWidth(24);
                $columns->textarea('description', 'Description')
                    ->setFormItemWidth(24);
                $columns->picture('cover', 'Cover Image')
                    ->setFormItemWidth(24);
                $columns->radio('status', 'Status')
                    ->setOptions([1 => 'Active', 0 => 'Inactive'])
                    ->setFormItemWidth(24);
            })
            ->actions(function (Form\ActionsContainer $actions) {
                $actions->button('Submit')->submit();
                $actions->button('Reset')->reset();
            });

        return $form->render();
    }
}
```

### Form Item Types Comparison

| Legacy FormBuilder | AntdAdmin Form | Description |
|-------------------|----------------|-------------|
| `text` | `text()` | Text input |
| `num` | `number()` or `money()` | Number input |
| `textarea` | `textarea()` | Multi-line text |
| `select` | `select()` | Dropdown |
| `radio` | `radio()` | Radio buttons |
| `checkbox` | `checkbox()` | Checkboxes |
| `date` | `date()` | Date picker |
| `time` | `dateTime()` | DateTime picker |
| `picture` | `picture()` | Image upload |
| `file` | `upload()` | File upload |
| `ueditor` | `ueditor()` | Rich text editor |
| `password` | `password()` | Password input |
| `hidden` | `hidden()` | Hidden field |

---

## GyListModel

GyListModel is the base model class that provides caching, validation, and common CRUD methods. This is shared across all versions.

### Basic Usage

```php
namespace Common\Model;
use Gy_Library\GyListModel;
use Gy_Library\DBCont;

class ProductModel extends GyListModel {
    protected $tableName = 'product';

    // Validation rules
    protected $_validate = [
        ['name', 'require', 'Product name is required'],
        ['name', '', 'Product name already exists', 0, 'unique'],
        ['price', 'number', 'Price must be a number'],
        ['category_id', 'require', 'Category is required'],
    ];

    // Auto-fill rules
    protected $_auto = [
        ['create_time', 'time', 1, 'function'],
        ['update_time', 'time', 3, 'function'],
        ['status', '1', 1, 'string'],
    ];

    // Custom method
    public function getActiveProducts() {
        return $this->where(['status' => DBCont::NORMAL_STATUS])
            ->order('sort asc, id desc')
            ->select();
    }
}
```

### Key Methods

| Method | Purpose |
|--------|---------|
| `getListForPage($map, $page, $rows, $order)` | Get paginated list |
| `getListForCount($map)` | Get total count |
| `createAdd($data)` | Validate and insert |
| `createSave($data)` | Validate and update |
| `getItemById($id)` | Get single record (cached) |
| `deleteItem($id)` | Delete record |
| `getError()` | Get last error message |

### Validation Rules

```php
protected $_validate = [
    // Format: [field, rule, message, validation_type, additional]
    ['name', 'require', 'Name is required'],                    // Required
    ['name', '', 'Name exists', 0, 'unique'],                   // Unique
    ['price', 'number', 'Must be number'],                      // Number
    ['email', 'email', 'Invalid email'],                        // Email
    ['phone', '/^1[3-9]\d{9}$/', 'Invalid phone'],             // Regex
    ['password', '6,20', '6-20 chars', 0, 'length'],            // Length
    ['status', [0, 1, 2], 'Invalid status', 0, 'in'],           // In array
    ['confirm_password', 'password', 'Not match', 0, 'confirm'], // Confirm
];
```

### Auto-Fill Rules

```php
protected $_auto = [
    // Format: [field, value, timing, type]
    // Timing: 1=insert, 2=update, 3=both
    ['create_time', 'time', 1, 'function'],       // Call time() on insert
    ['update_time', 'time', 3, 'function'],       // Call time() on both
    ['status', '1', 1, 'string'],                 // Set to '1' on insert
    ['ip', 'get_client_ip', 1, 'function'],       // Call function
    ['user_id', 'getUserId', 1, 'callback'],      // Call $this->getUserId()
];
```

---

## DBCont (Database Constants)

DBCont provides standard status and type constants for consistency.

### Status Values

```php
use Gy_Library\DBCont;

DBCont::NORMAL_STATUS = 1;      // Active/Enabled
DBCont::DISABLE_STATUS = 0;     // Inactive/Disabled
DBCont::AUDIT_STATUS = 2;       // Pending Review
DBCont::DELETE_STATUS = -1;     // Soft Deleted
```

### Usage Examples

```php
// In model query
$active_products = D('Product')->where([
    'status' => DBCont::NORMAL_STATUS
])->select();

// In jQuery Mode ListBuilder status column
->addTableColumn('status', 'Status', 'status', [
    1 => ['title' => 'Active', 'class' => 'success'],
    0 => ['title' => 'Inactive', 'class' => 'danger']
])

// In React Mode AntdAdmin status column
$container->status('status', 'Status')
    ->setValueEnum([
        1 => ['text' => 'Active', 'status' => 'Success'],
        0 => ['text' => 'Inactive', 'status' => 'Error']
    ]);
```

---

## RestController

RestController is the base controller for RESTful API endpoints. This is shared across all versions.

### Basic Usage

```php
namespace Api\Controller;
use Gy_Library\RestController;

class ProductController extends RestController {

    // GET /api/products
    public function index() {
        $page = I('get.page', 1);
        $limit = I('get.limit', 20);

        $model = D('Product');
        $count = $model->getListForCount([]);
        $list = $model->getListForPage([], $page, $limit);

        $this->apiSuccess([
            'list' => $list,
            'total' => $count,
            'page' => $page,
            'limit' => $limit
        ]);
    }

    // GET /api/products/:id
    public function detail() {
        $id = I('get.id');
        $product = D('Product')->getItemById($id);

        if (!$product) {
            $this->apiError('Product not found');
        }

        $this->apiSuccess($product);
    }

    // POST /api/products
    public function create() {
        $data = I('post.');
        $result = D('Product')->createAdd($data);

        if ($result === false) {
            $this->apiError(D('Product')->getError());
        }

        $this->apiSuccess(['id' => $result], 'Created successfully');
    }
}
```

### Response Methods

| Method | Purpose | Response Format |
|--------|---------|-----------------|
| `apiSuccess($data, $msg)` | Success response | `{success: true, data: ..., msg: ...}` |
| `apiError($msg, $code)` | Error response | `{success: false, msg: ..., code: ...}` |

---

## API Comparison Summary

Comparison between jQuery Mode and React Mode APIs:

| jQuery Mode ListBuilder | React Mode AntdAdmin Component |
|-------------------------|-------------------------------|
| `new \Qscmf\Builder\ListBuilder()` | `new \AntdAdmin\Component\Table()` |
| `->addTableColumn('name', 'Name')` | `$container->text('name', 'Name')` |
| `->addTableColumn('status', 'Status', 'status')` | `$container->status('status', 'Status')` |
| `->addTopButton('addnew', [...])` | `$container->button('Add')->modal(...)` |
| `->addRightButton('edit')` | `$container->action('')->edit()` |
| `->addRightButton('delete')` | `$container->action('')->delete()` |
| `->addSearchItem(...)` | `$container->text(...)->setSearch(true)` |
| `->setTableDataList($data)` | `->setDataSource($data)` |
| `->setTableDataPage($page->show())` | `->setPagination(new Pagination(...))` |
| `->build()` | `->render()` |

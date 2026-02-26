# Migration Guide: v13 to v14

This guide helps you migrate QSCMF projects from v13 to v14, covering code changes, API migration, and breaking changes.

## Prerequisites

Before starting migration:

1. **Backup your project**: Create a complete backup
2. **Update PHP**: Ensure PHP 8.2+ is installed
3. **Update Composer dependencies**:
   ```bash
   composer require tiderjian/think-core:^14.0
   composer update
   ```
4. **Run tests**: Ensure all existing tests pass

## Step-by-Step Migration

### Step 1: Update Configuration

Update `app/Common/Conf/config.php`:

```php
// Add v14 feature flag
'ANTD_ADMIN_BUILDER_ENABLE' => env('ANTD_ADMIN_ENABLE', true),
```

### Step 2: Migrate a Simple Controller

Start with a simple admin controller.

#### Before (v13)

```php
<?php
namespace Admin\Controller;

use Gy_Library\GyListController;

class ProductController extends GyListController {

    public function index() {
        $model = D('Product');
        $count = $model->getListForCount([]);
        $page = new \Gy_Library\GyPage($count, 20);
        $data_list = $model->getListForPage([], $page->nowPage, $page->listRows, 'id desc');

        $builder = new \Qscmf\Builder\ListBuilder();
        $builder->setMetaTitle('Product List')
            ->addTableColumn('id', 'ID')
            ->addTableColumn('name', 'Name')
            ->addTableColumn('status', 'Status', 'status')
            ->addTableColumn('create_time', 'Created', 'time')
            ->addTopButton('addnew', ['title' => 'Add', 'href' => U('add')])
            ->addRightButton('edit')
            ->addRightButton('delete')
            ->setTableDataList($data_list)
            ->setTableDataPage($page->show())
            ->build();
    }
}
```

#### After (v14 - AntdAdmin Component API)

```php
<?php
namespace Admin\Controller;

use Gy_Library\GyListController;
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;
use AntdAdmin\Component\Table\ActionsContainer;
use AntdAdmin\Component\Table\ColumnsContainer;

class ProductController extends GyListController {

    public function index() {
        $model = D('Product');
        $count = $model->getListForCount([]);
        $page = I('get.page', 1);
        $limit = I('get.limit', 20);
        $data_list = $model->getListForPage([], $page, $limit, 'id desc');

        $table = new Table();
        $table->setMetaTitle('Product List')
            ->actions(function (ActionsContainer $container) {
                $container->button('Add')
                    ->setProps(['type' => 'primary'])
                    ->modal((new \AntdAdmin\Component\Modal\Modal())
                        ->setTitle('Add Product')
                        ->setUrl(U('add')));
            })
            ->columns(function (ColumnsContainer $container) {
                $container->text('id', 'ID');
                $container->text('name', 'Name');
                $container->status('status', 'Status');
                $container->dateTime('create_time', 'Created');

                $container->action('', 'Operations')->actions(function ($container) {
                    $container->edit();
                    $container->delete();
                });
            })
            ->setDataSource($data_list)
            ->setPagination(new Pagination($page, $limit, $count))
            ->render();
    }
}
```

### Step 3: Migrate Form

#### Before (v13)

```php
public function add() {
    if (IS_POST) {
        $data = I('post.');
        $result = D('Product')->createAdd($data);
        if ($result === false) {
            $this->error(D('Product')->getError());
        }
        $this->success('Added successfully', U('index'));
    } else {
        $builder = new \Qscmf\Builder\FormBuilder();
        $builder->setPostUrl(U('add'))
            ->addFormItem('name', 'text', 'Name')
            ->addFormItem('status', 'radio', 'Status', [1 => 'Active', 0 => 'Inactive'])
            ->setFormData(['status' => 1]);

        return $builder->build();
    }
}
```

#### After (v14 - AntdAdmin Form API)

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
            ->columns(function (Form\ColumnsContainer $columns) {
                $columns->text('name', 'Name')
                    ->addRule(new Required())
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

## API Migration Reference

| v13 ListBuilder | v14 AntdAdmin Component |
|-----------------|-------------------------|
| `new \Qscmf\Builder\ListBuilder()` | `new \AntdAdmin\Component\Table()` |
| `->setMetaTitle($title)` | `->setMetaTitle($title)` |
| `->addTableColumn('name', 'Name')` | `$container->text('name', 'Name')` |
| `->addTableColumn('status', 'Status', 'status')` | `$container->status('status', 'Status')` |
| `->addTableColumn('date', 'Date', 'date')` | `$container->date('date', 'Date')` |
| `->addTableColumn('time', 'Time', 'time')` | `$container->dateTime('time', 'Time')` |
| `->addTableColumn('price', 'Price', 'num')` | `$container->money('price', 'Price')` |
| `->addTableColumn('cover', 'Cover', 'picture')` | `$container->picture('cover', 'Cover')` |
| `->addTopButton('addnew', [...])` | `$container->button('Add')->modal(...)` |
| `->addTopButton('delete', [...])` | `$container->button('Delete')->setDanger(true)` |
| `->addRightButton('edit')` | `$container->action('')->edit()` |
| `->addRightButton('delete')` | `$container->action('')->delete()` |
| `->addRightButton('forbid')` | `$container->action('')->forbid()` |
| `->addRightButton('resume')` | `$container->action('')->resume()` |
| `->addSearchItem('keyword', 'text', 'Search')` | `$container->text('keyword', 'Search')->setSearch(true)` |
| `->addSearchItem('status', 'select', 'Status', $options)` | `$container->select('status', 'Status')->setOptions($options)->setSearch(true)` |
| `->setCheckBox(true)` | `$table->setRowSelection(true)` |
| `->setTableDataList($data)` | `->setDataSource($data)` |
| `->setTableDataPage($page->show())` | `->setPagination(new Pagination(...))` |
| `->build()` | `->render()` |

## Column Type Mapping

| v13 Type | v14 Method | Notes |
|---------|------------|-------|
| `null` (default) | `text()` | Plain text |
| `status` | `status()` | Status badge with colors |
| `date` | `date()` | Date only |
| `time` | `dateTime()` | Date and time |
| `picture` | `picture()` | Single image |
| `pictures` | `pictures()` | Multiple images |
| `num` | `number()` or `money()` | Numeric values |
| `icon` | `icon()` | Icon display |
| `btn` | `action()` | Action buttons |
| `fun` | Custom renderer | Use `setRender()` callback |
| `self` | Custom type | Use custom column class |

## Breaking Changes

### PHPUnit 10

Update test files:

```php
// Before (PHPUnit 9)
$this->assertDatabaseHas('users', ['email' => 'test@example.com']);

// After (PHPUnit 10)
$this->assertDatabaseHas('users', ['email' => 'test@example.com']);
// Same syntax, but stricter type checking
```

### Response Handling

```php
// Before (v13) - Full page reload
$this->success('Success', U('index'));

// After (v14) - Inertia response (no reload needed)
$this->success('Success');
// Client-side handles update
```

### JavaScript Events

```php
// Before (v13) - jQuery events
$('body').on('click', '.btn-delete', function() {
    // ...
});

// After (v14) - React handles events
// Events handled in React components
// No jQuery dependency
```

## Backward Compatibility

v14 supports the legacy ListBuilder API for gradual migration:

### Enabling Legacy Mode Per Controller

```php
class LegacyController extends QsListController {
    protected $antdAdminEnable = false;  // Use jQuery rendering

    public function index() {
        // v13 style code still works
        $builder = new \Qscmf\Builder\ListBuilder();
        // ...
        $builder->build();
    }
}
```

### Global Legacy Mode

```php
// In config.php - disable for entire project
'ANTD_ADMIN_BUILDER_ENABLE' => false,
```

## Testing Migration

### Update Test Cases

```php
// Before (v13)
class ProductTest extends TestCase {
    public function testIndex() {
        $response = $this->get('/admin/product/index');
        $response->assertStatus(200);
        $response->assertSee('Product List');
    }
}

// After (v14) - Inertia responses
class ProductTest extends TestCase {
    public function testIndex() {
        $response = $this->get('/admin/product/index');

        // Check Inertia response
        $response->assertHeader('X-Inertia', 'true');
        $response->assertJsonStructure([
            'component',
            'props' => [
                'table',
                'title'
            ]
        ]);
    }
}
```

## Common Issues and Solutions

### Issue: jQuery Events Not Working

**Cause**: v14 React components don't use jQuery events

**Solution**: Migrate to React event handlers or use legacy mode

### Issue: Page Reload After Form Submit

**Cause**: v14 uses Inertia for SPA navigation

**Solution**: Return success without redirect URL

```php
// v13
$this->success('Success', U('index'));

// v14
$this->success('Success');  // Client handles navigation
```

### Issue: Styles Not Loading

**Cause**: v14 uses Ant Design instead of Bootstrap

**Solution**: Update CSS imports and class names

```php
// v13
<link href="/assets/bootstrap.css" rel="stylesheet">

// v14
<link href="/assets/antd.css" rel="stylesheet">
```

## Migration Checklist

- [ ] Backup project before migration
- [ ] Update composer.json to require think-core ^14.0
- [ ] Run composer update
- [ ] Update config.php with ANTD_ADMIN_BUILDER_ENABLE setting
- [ ] Run all tests
- [ ] Migrate one controller as test
- [ ] Test migrated controller thoroughly
- [ ] Migrate remaining controllers
- [ ] Update PHPUnit to ^10.0
- [ ] Update test cases for Inertia responses
- [ ] Remove jQuery dependencies (optional)
- [ ] Update frontend assets (optional)
- [ ] Final testing of all features
- [ ] Deploy to staging environment
- [ ] Production deployment

# Common Patterns

Detailed examples and patterns for using AntdAdmin components.

## Table Patterns

### 1. Basic Table with Search

```php
use AntdAdmin\Component\Table;

$table = new Table();
$table->setMetaTitle('产品列表')
      ->setSearchUrl(U('index'))  // Enable search
      ->setDataSource($list['data'])
      ->setPagination(new Table\Pagination($list['total'], $list['per_page']))
      ->columns(function (Table\ColumnsContainer $container) {
          $container->text('id', 'ID')->setSearch(false);
          $container->text('name', '名称');
          $container->digit('price', '价格');
          $container->select('status', '状态')->setValueEnum(DBCont::getStatusList());
          $container->dateTime('created_at', '创建时间');
      })
      ->actions(function (Table\ActionsContainer $container) {
          $container->addNew();
      })
      ->render();
```

---

### 2. Table with CRUD Actions (Shortcuts)

```php
$table->columns(function (Table\ColumnsContainer $container) {
    $container->text('id', 'ID')->setSearch(false);
    $container->text('name', '名称');
    $container->action('', '操作')->actions(function ($container) {
        $container->edit();     // Edit row
        $container->delete();   // Delete row
        $container->forbid();   // Disable row
    });
})
->actions(function (Table\ActionsContainer $container) {
    $container->addNew();    // Add new button
    $container->delete();    // Batch delete
    $container->forbid();    // Batch disable
    $container->resume();    // Batch enable
});
```

**Available Shortcuts**:
- **Row Actions**: `edit()`, `delete()`, `forbid()`, `resume()`
- **Table Actions**: `addNew()`, `delete()`, `forbid()`, `resume()`, `editSave()`

---

### 3. Table with Custom Actions

```php
$table->actions(function (Table\ActionsContainer $container) {
    // Link button
    $container->button('添加')->link(U('add'));

    // Request button
    $container->button('导出')
              ->request('post', U('export'), [], [], '确定要导出吗？');

    // Editable table
    $container->startEditable('批量编辑')
              ->saveRequest('put', U('batchUpdate'));
});

// Row actions
$container->action('', '操作')->actions(function ($container) {
    // Modal edit
    $modal = new Modal();
    $modal->setTitle('编辑')->setUrl(U('edit', ['id' => '__id__']));
    $container->link('编辑')->modal($modal);

    // Conditional action
    $container->link('审核')
              ->request('post', U('audit'), ['id' => '__id__'])
              ->setShowCondition('status', 'eq', DBCont::AUDIT_STATUS);
});
```

---

### 4. Inline Editing Table

```php
$table->defaultEditMode()  // Enable edit mode
      ->columns(function (Table\ColumnsContainer $container) {
          $container->text('name', '名称');
          $container->digit('sort', '排序')->editable();
          $container->select('status', '状态')
                    ->setValueEnum(DBCont::getStatusList())
                    ->editable();
      })
      ->actions(function (Table\ActionsContainer $container) {
          $container->editSave();  // Save button
      });
```

---

### 5. Tree/Expandable Table

```php
$table->setExpandable([
          'childrenColumnName' => 'children',
          'defaultExpandAllRows' => true
      ])
      ->setDataSource($treeData)
      ->columns(function (Table\ColumnsContainer $container) {
          $container->text('name', '名称');
          $container->text('level', '层级');
      });
```

---

## Form Patterns

### 1. Basic Add/Edit Form

```php
use AntdAdmin\Component\Form;
use Qscmf\Core\Validator\Rule\Required;

// Controller
public function add()
{
    if (IS_POST) {
        $result = D('Product')->add(I('post.'));
        if ($result) {
            $this->success('添加成功');
        } else {
            $this->error('添加失败');
        }
    } else {
        $form = new Form();
        $form->setMetaTitle('新增产品')
             ->setSubmitRequest('post', U('add'))
             ->columns(function (Form\ColumnsContainer $container) {
                 $container->text('name', '名称')->addRule(new Required());
                 $container->digit('price', '价格');
                 $container->textarea('description', '描述');
             })
             ->actions(function (Form\ActionsContainer $container) {
                 $container->button('提交')->submit();
                 $container->button('重置')->reset();
             })
             ->render();
    }
}

// Edit with initial values
public function edit()
{
    $id = I('get.id');
    $data = D('Product')->find($id);

    $form = new Form();
    $form->setMetaTitle('编辑产品')
         ->setInitialValues($data)
         ->setSubmitRequest('put', U('update', ['id' => $id]))
         ->columns(...)
         ->render();
}
```

---

### 2. Form with Image Upload

```php
use FormItem\ObjectStorage\Lib\Common;

$form->columns(function (Form\ColumnsContainer $container) {
    // Single image with crop
    $container->image('cover_id', '封面图')
              ->setUploadRequest(Common::genItemDataUrl('image'))
              ->setCrop('16/9')
              ->setMaxCount(1)
              ->addRule(new Required());

    // Multiple images
    $container->image('gallery', '图集')
              ->setUploadRequest(Common::genItemDataUrl('image'))
              ->setMaxCount(9);
});
```

**Crop Ratios**:
- `'16/9'` - Widescreen
- `'4/3'` - Standard
- `'1/1'` - Square
- `'3/4'` - Portrait

---

### 3. Form with Validation

```php
use Qscmf\Core\Validator\Rule\Required;

$form->columns(function (Form\ColumnsContainer $container) {
    // Required field
    $container->text('title', '标题')
              ->addRule(new Required())
              ->setFormItemWidth(24);

    // Select with validation
    $container->select('category_id', '分类')
              ->setValueEnum(D('Category')->getField('id,name'))
              ->addRule(new Required());

    // Number with range
    $container->digit('age', '年龄')
              ->setFormItemProps([
                  'min' => 0,
                  'max' => 150
              ]);
});
```

---

### 4. Form with Dependencies

```php
$form->columns(function (Form\ColumnsContainer $container) {
    $container->select('type', '类型')
              ->setValueEnum([
                  'article' => '文章',
                  'video' => '视频'
              ]);

    // Show only when type = article
    $container->dependency()
              ->setShowCondition('type', 'eq', 'article')
              ->columns(function (Form\ColumnsContainer $container) {
                  $container->ueditor('content', '内容')
                            ->setFormItemWidth(24);
              });

    // Show only when type = video
    $container->dependency()
              ->setShowCondition('type', 'eq', 'video')
              ->columns(function (Form\ColumnsContainer $container) {
                  $container->text('video_url', '视频链接')
                            ->setFormItemWidth(24);
              });
});
```

---

### 5. Form with Tabs

```php
use AntdAdmin\Component\Tabs;

// Create forms for each tab
$basicForm = new Form();
$basicForm->columns(function (Form\ColumnsContainer $container) {
    $container->text('name', '名称');
    $container->digit('price', '价格');
});

$seoForm = new Form();
$seoForm->columns(function (Form\ColumnsContainer $container) {
    $container->text('meta_title', 'SEO标题');
    $container->textarea('meta_description', 'SEO描述');
});

// Combine into tabs
$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', $basicForm)
     ->addTab('seo', 'SEO设置', $seoForm)
     ->render();
```

---

### 6. Form with Dynamic List (FormList)

```php
$form->columns(function (Form\ColumnsContainer $container) {
    $container->text('order_no', '订单号');

    // Dynamic product list
    $container->formList('products', '产品列表')
              ->columns(function (Form\ColumnsContainer $container) {
                  $container->select('product_id', '产品')
                            ->setValueEnum(D('Product')->getField('id,name'));
                  $container->digit('quantity', '数量');
                  $container->digit('price', '单价');
              });
});
```

---

## Modal Patterns

### 1. Modal with Form

```php
use AntdAdmin\Component\Modal\Modal;
use AntdAdmin\Component\Form;

// Create form
$form = new Form();
$form->setSubmitRequest('post', U('add'))
     ->columns(function (Form\ColumnsContainer $container) {
         $container->text('name', '名称');
     });

// Create modal
$modal = new Modal();
$modal->setTitle('新增产品')
      ->setWidth('800px')
      ->setContent($form);

// Attach to button
$table->actions(function (Table\ActionsContainer $container) use ($modal) {
    $container->button('添加')->modal($modal);
});
```

---

### 2. Modal with URL (Lazy Load)

```php
$modal = new Modal();
$modal->setTitle('编辑')
      ->setWidth('800px')
      ->setUrl(U('edit', ['id' => '__id__']));  // __id__ placeholder

// Attach to row action
$container->action('', '操作')->actions(function ($container) use ($modal) {
    $container->link('编辑')->modal($modal);
});
```

**Advantages of URL Modal**:
- Lazy loads content only when opened
- Can use row data in URL (with `__field__` placeholders)
- Better for large/complex forms

---

### 3. Nested Modals (Table in Modal)

```php
// Create table for modal
$table = new Table();
$table->setDataSource($logs)
      ->columns(function (Table\ColumnsContainer $container) {
          $container->text('action', '操作');
          $container->text('user', '用户');
          $container->dateTime('created_at', '时间');
      });

// Modal with table
$modal = new Modal();
$modal->setTitle('操作日志')
      ->setWidth('1000px')
      ->setContent($table);
```

---

## Advanced Patterns

### 1. Permission-Based Actions

```php
$container->action('', '操作')->actions(function ($container) {
    $container->edit()
              ->setAuthNode('product_edit');

    $container->delete()
              ->setAuthNode('product_delete')
              ->setShowCondition('is_deletable', 'eq', 1);
});

$table->actions(function (Table\ActionsContainer $container) {
    $container->addNew()
              ->setAuthNode('product_add');
});
```

---

### 2. Batch Operations with Selection

```php
$table->setRowSelection([
    'type' => 'checkbox'
])
->actions(function (Table\ActionsContainer $container) {
    $container->button('批量删除')
              ->relateSelection()  // Use selected rows
              ->request('post', U('batchDelete'), ['ids' => '__id__'])
              ->setConfirmMessage('确定删除选中的记录吗？');
});
```

---

### 3. Conditional Rendering

```php
// Table column condition
$container->link('审核')
          ->setShowCondition('status', 'eq', DBCont::AUDIT_STATUS);

// Form field condition
$container->dependency()
          ->setShowCondition('type', 'in', ['article', 'news'])
          ->columns(function (Form\ColumnsContainer $container) {
              $container->ueditor('content', '内容');
          });

// Operators
// eq, =, neq, !=, <>, gt, >, gte, >=, lt, <, lte, <=, in, not in
```

---

### 4. Custom Render Values

```php
// Pass extra data to frontend
$table->setExtraRenderValues([
    'categories' => D('Category')->getField('id,name'),
    'statuses' => DBCont::getStatusList()
]);

// Access in custom column renderer
```

---

## Tabs Patterns

### 1. Basic Tabs with Forms

```php
use AntdAdmin\Component\Tabs;
use AntdAdmin\Component\Form;

// Create multiple forms
$basicForm = new Form();
$basicForm->columns(function ($container) {
    $container->text('name', '名称');
    $container->digit('price', '价格');
});

$detailForm = new Form();
$detailForm->columns(function ($container) {
    $container->ueditor('content', '详情');
});

// Combine into tabs
$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', $basicForm)
     ->addTab('detail', '详细信息', $detailForm)
     ->render();
```

---

### 2. Tabs with URL-based Content (Lazy Load)

```php
$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', null, U('basic'))       // Load from URL
     ->addTab('seo', 'SEO设置', null, U('seo'))            // Load from URL
     ->addTab('logs', '操作日志', null, U('logs'))         // Load from URL
     ->render();

// In controller
public function basic() {
    $id = I('get.id');
    $form = new Form();
    $form->setInitialValues(D('Product')->find($id))
         ->columns(...)
         ->render();  // Returns content for tab
}

public function seo() {
    $id = I('get.id');
    $form = new Form();
    $form->setInitialValues(D('ProductSeo')->find($id))
         ->columns(...)
         ->render();
}

public function logs() {
    $id = I('get.id');
    $table = new Table();
    $table->setDataSource(D('ProductLog')->where(['product_id' => $id])->select())
          ->columns(...)
          ->render();
}
```

**Advantages**:
- Lazy loads content only when tab is clicked
- Better performance for complex forms
- Can mix forms and tables in tabs

---

### 3. Tabs with Mixed Content

```php
// Mix forms, tables, and URLs
$basicForm = new Form();
$basicForm->columns(...);

$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', $basicForm)        // Direct form
     ->addTab('images', '图片管理', null, U('images'))  // URL (lazy load)
     ->addTab('comments', '评论列表', $commentTable)   // Direct table
     ->render();
```

---

### 4. Tabs in Modal

```php
use AntdAdmin\Component\Modal\Modal;

// Create tabs
$basicForm = new Form();
$basicForm->columns(...);

$settingsForm = new Form();
$settingsForm->columns(...);

$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', $basicForm)
     ->addTab('settings', '设置', $settingsForm);

// Put tabs in modal
$modal = new Modal();
$modal->setTitle('编辑产品')
      ->setContent($tabs)
      ->setWidth('1000px');

// Attach to button
$container->link('编辑')->modal($modal);
```

---

### 5. Tabs with Independent Forms

Each tab has its own submit button:

```php
// Basic info form with submit
$basicForm = new Form();
$basicForm->setSubmitRequest('post', U('updateBasic'))
          ->columns(...)
          ->actions(function ($container) {
              $container->button('保存基本信息')->submit();
          });

// SEO form with submit
$seoForm = new Form();
$seoForm->setSubmitRequest('post', U('updateSeo'))
        ->columns(...)
        ->actions(function ($container) {
            $container->button('保存SEO设置')->submit();
        });

$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', $basicForm)
     ->addTab('seo', 'SEO设置', $seoForm)
     ->render();
```

**Note**: Each form submits independently. After submit, only that tab's form is saved.

---

### 6. Tabs with Shared Form Data

All tabs share the same form data:

```php
// Load shared data
$id = I('get.id');
$product = D('Product')->find($id);

// Create forms with same initial values
$basicForm = new Form();
$basicForm->setInitialValues($product)
          ->setSubmitRequest('post', U('update', ['id' => $id]))
          ->columns(function ($container) {
              $container->text('name', '名称');
              $container->digit('price', '价格');
          });

$seoForm = new Form();
$seoForm->setInitialValues($product)
        ->setSubmitRequest('post', U('update', ['id' => $id]))
        ->columns(function ($container) {
            $container->text('meta_title', 'SEO标题');
            $container->textarea('meta_description', 'SEO描述');
        });

$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', $basicForm)
     ->addTab('seo', 'SEO设置', $seoForm)
     ->render();
```

---

### 7. Conditional Tab Display

Show/hide tabs based on conditions:

```php
$product = D('Product')->find($id);

$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', $basicForm);

// Only show SEO tab for published products
if ($product['status'] == DBCont::NORMAL_STATUS) {
    $tabs->addTab('seo', 'SEO设置', $seoForm);
}

// Only show logs tab for admin users
if (session('user.role') == 'admin') {
    $tabs->addTab('logs', '操作日志', null, U('logs'));
}

$tabs->render();
```

---

### 8. Tabs with State Persistence

Keep track of active tab across page reloads:

```php
// In controller
$activeTab = I('get.tab', 'basic');  // Default to 'basic'

$tabs = new Tabs();
$tabs->addTab('basic', '基本信息', $basicForm)
     ->addTab('seo', 'SEO设置', $seoForm)
     ->render();

// URLs will include tab parameter
// e.g., U('edit', ['id' => $id, 'tab' => 'seo'])
```

---

## Controller Integration

### Standard CRUD Controller

```php
use Qscmf\Controller\QsListController;
use AntdAdmin\Component\Table;

class ProductController extends QsListController
{
    public function index()
    {
        $get = I('get.');
        $list = D('Product')->getList($get);

        $table = new Table();
        $table->setMetaTitle('产品管理')
              ->setSearchUrl(U('index'))
              ->setDataSource($list['data'])
              ->setPagination(new Table\Pagination($list['total'], $list['per_page']))
              ->columns(function (Table\ColumnsContainer $container) {
                  // ... columns
              })
              ->actions(function (Table\ActionsContainer $container) {
                  // ... actions
              })
              ->render();
    }
}
```

### Data Format Expected

```php
// Table expects array of arrays/objects
$data = [
    ['id' => 1, 'name' => 'Product 1', 'price' => 100],
    ['id' => 2, 'name' => 'Product 2', 'price' => 200],
];

// From model with pagination
$list = [
    'data' => D('Product')->where($where)->page($page, $size)->select(),
    'total' => D('Product')->where($where)->count(),
    'per_page' => $size
];
```

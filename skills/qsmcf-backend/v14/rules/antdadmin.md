# AntdAdmin Components Reference (v14)

Reference for using AntdAdmin React components directly in QSCMF v14.

## When to Use

- New v14 projects with React rendering
- Need advanced features beyond ListBuilder
- Custom UI requirements
- Inertia.js integration

## API Choice

v14 supports two APIs:

| API | Use Case | Rendering |
|-----|----------|-----------|
| **AntdAdmin\Component** | New projects, advanced UI | React/AntdAdmin |
| **ListBuilder** (legacy) | Backward compatibility | jQuery or React |

---

## Table Component

### Basic Usage

```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;

$table = new Table();
$table->setMetaTitle('商品列表')
    ->columns(function (Table\ColumnsContainer $container) {
        $container->text('product_name', '商品名称');
        $container->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList());
    })
    ->setDataSource($data)
    ->setPagination(new Pagination($page, $pageSize, $total))
    ->render();
```

### Complete Table Example

```php
public function index()
{
    $model = D('Product');
    $count = $model->count();
    $page = new \Gy_Library\GyPage($count);
    $data_list = $model->page($page->nowPage, $page->listRows)->select();

    $table = new Table();
    $table->setMetaTitle('商品列表')
        ->actions(function (Table\ActionsContainer $container) {
            $container->button('新增')
                ->setProps(['type' => 'primary'])
                ->modal((new \AntdAdmin\Component\Modal\Modal())
                    ->setWidth('800px')
                    ->setUrl(U('add'))
                    ->setTitle('新增商品'));
            $container->forbid();
            $container->resume();
            $container->delete();
        })
        ->columns(function (Table\ColumnsContainer $container) {
            $container->text('product_name', '商品名称')
                ->setSearch(true);
            $container->select('cate_id', '分类')
                ->setValueEnum(D('Category')->getField('id,name'))
                ->setSearch(true);
            $container->image('cover', '封面');
            $container->money('price', '价格')
                ->setSearch(true);
            $container->number('stock', '库存')
                ->editable();
            $container->select('status', '状态')
                ->setValueEnum(DBCont::getStatusList())
                ->setBadge([1 => 'success', 0 => 'default'])
                ->setSearch(true);
            $container->number('sort', '排序')
                ->editable();
            $container->datetime('create_time', '创建时间');
            $container->action('', '操作')
                ->actions(function (Table\ColumnType\ActionsContainer $container) {
                    $container->edit()->modal(
                        (new \AntdAdmin\Component\Modal\Modal())
                            ->setWidth('800px')
                            ->setUrl(U('edit', ['id' => '__id__']))
                            ->setTitle('编辑')
                    );
                    $container->forbid();
                    $container->resume();
                    $container->delete();
                });
        })
        ->setDataSource($data_list)
        ->setPagination(new Pagination($page->nowPage, $page->listRows, $count))
        ->setSearch(false)
        ->render();
}
```

### Table Column Types

| Method | Description |
|--------|-------------|
| `text($field, $title)` | Text column |
| `select($field, $title)` | Select/enumeration column |
| `number($field, $title)` | Number column |
| `money($field, $title)` | Money/currency column |
| `date($field, $title)` | Date column |
| `datetime($field, $title)` | DateTime column |
| `image($field, $title)` | Image column |
| `action($field, $title)` | Action buttons column |

### Table Column Methods

| Method | Description |
|--------|-------------|
| `setSearch($enabled)` | Enable/disable search |
| `setValueEnum($values)` | Set enum values for select |
| `setBadge($colors)` | Set badge colors |
| `editable()` | Enable inline editing |
| `setFormItemWidth($width)` | Set column width |

### Table Actions

| Method | Description |
|--------|-------------|
| `button($title)` | Generic button |
| `addnew()` | Add new button |
| `forbid()` | Disable button |
| `resume()` | Enable button |
| `delete()` | Delete button |
| `editSave()` | Save changes button |

---

## Form Component

### Basic Usage

```php
use AntdAdmin\Component\Form;
use AntdAdmin\Component\ColumnType\RuleType\Required;

$form = new Form();
$form->setSubmitRequest('post', U('add'))
    ->setInitialValues(['status' => 1])
    ->columns(function (Form\ColumnsContainer $columns) {
        $columns->text('product_name', '商品名称')
            ->addRule(new Required())
            ->setFormItemWidth(24);
    })
    ->actions(function (Form\ActionsContainer $actions) {
        $actions->button('提交')->submit();
        $actions->button('重置')->reset();
    });

return $form->render();
```

### Complete Form Example

```php
public function add()
{
    if (IS_POST) {
        parent::autoCheckToken();
        $data = I('post.');

        $model = D('Product');
        $result = $model->createAdd($data);

        if ($result === false) {
            $this->error($model->getError());
        }

        $this->success('添加成功');
    }

    $form = new Form();
    $form->setSubmitRequest('post', U('add'))
        ->setInitialValues([
            'status' => DBCont::NORMAL_STATUS,
            'sort' => 99,
        ])
        ->columns(function (Form\ColumnsContainer $columns) {
            $columns->text('product_name', '商品名称')
                ->addRule(new Required())
                ->setFormItemWidth(24);

            $columns->select('cate_id', '分类')
                ->setValueEnum(D('Category')->getField('id,name'))
                ->addRule(new Required())
                ->setFormItemWidth(24);

            $columns->image('cover_id', '封面图')
                ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
                ->setCrop('16/9')
                ->setFormItemWidth(24);

            $columns->ueditor('content', '商品详情')
                ->setFormItemWidth(24);

            $columns->number('price', '价格')
                ->addRule(new Required())
                ->setFormItemWidth(12);

            $columns->number('stock', '库存')
                ->setFormItemWidth(12);

            $columns->number('sort', '排序')
                ->setFormItemWidth(12);

            $columns->select('status', '状态')
                ->setValueEnum(DBCont::getStatusList())
                ->addRule(new Required())
                ->setFormItemWidth(12);
        })
        ->actions(function (Form\ActionsContainer $actions) {
            $actions->button('提交')->submit();
            $actions->button('重置')->reset();
        });

    return $form->render();
}
```

### Form Field Types

| Method | Description |
|--------|-------------|
| `text($field, $title)` | Text input |
| `textarea($field, $title)` | Textarea |
| `number($field, $title)` | Number input |
| `money($field, $title)` | Money input |
| `select($field, $title)` | Select dropdown |
| `radio($field, $title)` | Radio buttons |
| `checkbox($field, $title)` | Checkbox group |
| `date($field, $title)` | Date picker |
| `datetime($field, $title)` | DateTime picker |
| `image($field, $title)` | Image upload |
| `file($field, $title)` | File upload |
| `ueditor($field, $title)` | Rich text editor |
| `password($field, $title)` | Password input |
| `hidden($field, $title)` | Hidden field |

### Form Validation Rules

```php
use AntdAdmin\Component\ColumnType\RuleType\Required;
use AntdAdmin\Component\ColumnType\RuleType\Length;
use AntdAdmin\Component\ColumnType\RuleType\Email;

$columns->text('product_name', '商品名称')
    ->addRule(new Required())
    ->addRule(new Length(1, 200));

$columns->text('email', '邮箱')
    ->addRule(new Email());
```

### Form Width Grid

| Width | Percentage | Use Case |
|-------|------------|----------|
| 24 | 100% | Full width |
| 12 | 50% | Half width |
| 8 | 33.3% | One third |
| 6 | 25% | Quarter |

---

## Modal Component

```php
use AntdAdmin\Component\Modal\Modal;

$modal = new Modal();
$modal->setWidth('800px')
    ->setUrl(U('add'))
    ->setTitle('新增商品')
    ->setBackdrop(false)
    ->setKeyboard(false);

// Attach to button
$container->button('新增')
    ->setProps(['type' => 'primary'])
    ->modal($modal);

// Attach to edit action
$container->edit()->modal($modal);
```

### Modal Methods

| Method | Description |
|--------|-------------|
| `setWidth($width)` | Set modal width |
| `setUrl($url)` | Set content URL |
| `setTitle($title)` | Set modal title |
| `setBackdrop($enabled)` | Enable/disable backdrop click |
| `setKeyboard($enabled)` | Enable/disable ESC key |

---

## Badge Colors

| Value | Color |
|-------|-------|
| `success` | Green |
| `processing` | Blue (animated) |
| `warning` | Orange |
| `error` | Red |
| `default` | Gray |

---

## Related Documentation

- [ListBuilder API](listbuilder-api.md) - Legacy API
- [FormBuilder API](formbuilder-api.md) - Legacy form API
- [Inertia.js Integration](inertia.md) - SPA navigation

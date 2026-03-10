# v14-Specific Features

> This file documents v14-specific features: Inertia.js integration, direct AntdAdmin component usage, and ListAdapter pattern.
>
> **When to Use This Rule**:
> - Implementing SPA-like navigation with Inertia.js
> - Using AntdAdmin components directly (beyond ListBuilder)
> - Customizing the rendering layer via ListAdapter

**Impact**: MEDIUM

---

## Inertia.js Integration

v14 supports Inertia.js for SPA-like navigation.

### HasLayoutProps Trait

```php
use Qscmf\Lib\Inertia\HasLayoutProps;

class DashboardController extends QsListController
{
    use HasLayoutProps;

    public function index()
    {
        $this->shareLayoutProps([
            'title' => 'Dashboard',
            'breadcrumbs' => [
                ['title' => 'Home', 'href' => '/'],
                ['title' => 'Dashboard'],
            ],
        ]);

        // ... rest of controller
    }
}
```

### X-Inertia Header Detection

```php
public function detail()
{
    $data = D('Product')->find(I('get.id'));

    if ($this->isInertiaRequest()) {
        // Return Inertia props for SPA navigation
        return Inertia::render('Product/Detail', [
            'product' => $data,
        ]);
    }

    // Traditional page render
    $this->assign('data', $data);
    $this->display();
}

protected function isInertiaRequest(): bool
{
    return !empty($_SERVER['HTTP_X_INERTIA']);
}
```

---

## Direct AntdAdmin Component Usage

For advanced scenarios beyond ListBuilder, use direct AntdAdmin components.

### Table Component

```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;
use AntdAdmin\Component\Modal\Modal;

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
                ->modal((new Modal())
                    ->setWidth('800px')
                    ->setUrl(U('add'))
                    ->setTitle('新增商品'));
            $container->forbid();
            $container->resume();
            $container->delete();
        })
        ->columns(function (Table\ColumnsContainer $container) {
            $container->text('product_name', '商品名称');
            $container->select('status', '状态')
                ->setValueEnum(DBCont::getStatusList())
                ->setBadge([1 => 'success', 0 => 'default']);
            $container->number('sort', '排序')
                ->editable();
            $container->action('', '操作')
                ->actions(function (Table\ColumnType\ActionsContainer $container) {
                    $container->edit()->modal(
                        (new Modal())
                            ->setWidth('800px')
                            ->setUrl(U('edit', ['id' => '__id__']))
                            ->setTitle('编辑')
                    );
                    $container->delete();
                });
        })
        ->setDataSource($data_list)
        ->setPagination(new Pagination($page->nowPage, $page->listRows, $count))
        ->render();
}
```

### Form Component

```php
use AntdAdmin\Component\Form;
use AntdAdmin\Component\ColumnType\RuleType\Required;

public function add()
{
    if (IS_POST) {
        $data = I('post.');
        $result = D('Product')->createAdd($data);
        if ($result === false) {
            $this->error(D('Product')->getError());
        }
        $this->success('添加成功');
    }

    $form = new Form();
    $form->setSubmitRequest('post', U('add'))
        ->setInitialValues(['status' => 1])
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

            $columns->number('sort', '排序')
                ->setFormItemWidth(12);

            $columns->select('status', '状态')
                ->setValueEnum(DBCont::getStatusList())
                ->setFormItemWidth(12);
        })
        ->actions(function (Form\ActionsContainer $actions) {
            $actions->button('提交')->submit();
            $actions->button('重置')->reset();
        });

    return $form->render();
}
```

---

## ListAdapter Pattern

The ListAdapter converts ListBuilder calls to AntdAdmin components internally.

```
User Code (ListBuilder API)
         ↓
    ListBuilder
         ↓
    ListAdapter (converts to AntdAdmin format)
         ↓
    AntdAdmin\Component\Table
         ↓
    React Rendering
```

For custom rendering, extend the adapter:

```php
use Qscmf\Builder\ListAdapter;

class CustomListAdapter extends ListAdapter
{
    protected function convertColumn($name, $title, $type, $value)
    {
        // Custom column conversion logic
        return parent::convertColumn($name, $title, $type, $value);
    }
}
```

---

## Related Rules

- [ListBuilder API](listbuilder-api.md) - Standard ListBuilder usage
- [FormBuilder API](formbuilder-api.md) - Standard FormBuilder usage
- [Inertia Integration](../references/inertia-integration.md) - Complete Inertia guide

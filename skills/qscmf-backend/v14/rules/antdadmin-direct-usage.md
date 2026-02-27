# AntdAdmin 组件直接使用指南

> v14 跳过 ListBuilder 直接使用 AntdAdmin\Component 的模式

## 概述

v14 版本支持两种 API 风格：
1. **ListBuilder API** - 兼容层，底层转换为 AntdAdmin 组件
2. **AntdAdmin Component API** - 直接使用组件，更灵活

本文档介绍如何**直接使用 AntdAdmin\Component\*** 组件。

## 何时使用直接组件

| 场景 | 推荐方式 |
|------|---------|
| 简单 CRUD | ListBuilder API |
| 复杂表格（多级表头、可编辑） | 直接组件 |
| 自定义渲染逻辑 | 直接组件 |
| 需要细粒度控制 | 直接组件 |
| 跨版本兼容需求 | ListBuilder API |

## Table 组件

### 基础用法

```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;

public function index()
{
    $model = D('Product');
    $count = $model->where($map)->count();
    $page = I('get.page', 1);
    $limit = I('get.limit', 20);
    $data = $model->where($map)->page($page, $limit)->order('id desc')->select();

    $table = new Table();
    $table->setMetaTitle('商品列表')
        ->columns(function (Table\ColumnsContainer $container) {
            $container->text('id', 'ID')->setSorter(true);
            $container->text('name', '名称');
            $container->money('price', '价格');
            $container->status('status', '状态')
                ->setValueEnum([
                    1 => ['text' => '启用', 'status' => 'Success'],
                    0 => ['text' => '禁用', 'status' => 'Error'],
                ]);
            $container->dateTime('create_time', '创建时间');

            $container->action('', '操作')->actions(function ($container) {
                $container->edit();
                $container->delete();
                $container->button('详情')
                    ->setHref(U('detail', ['id' => '__id__']));
            });
        })
        ->actions(function (Table\ActionsContainer $container) {
            $container->button('新增')
                ->setProps(['type' => 'primary'])
                ->modal((new \AntdAdmin\Component\Modal\Modal())
                    ->setTitle('新增商品')
                    ->setUrl(U('add')));
            $container->delete();
            $container->forbid();
            $container->resume();
        })
        ->setDataSource($data)
        ->setPagination(new Pagination($page, $limit, $count))
        ->render();
}
```

### 多级表头

```php
$table->columns(function (Table\ColumnsContainer $container) {
    $container->group('基本信息', function ($container) {
        $container->text('name', '名称');
        $container->text('code', '编码');
    });
    $container->group('价格信息', function ($container) {
        $container->money('cost_price', '成本价');
        $container->money('sale_price', '售价');
    });
});
```

### 可编辑表格

```php
$container->text('sort', '排序')
    ->setEditable(true)
    ->setRules([
        ['required' => true, 'message' => '排序不能为空'],
        ['type' => 'number', 'min' => 0, 'message' => '必须为非负数'],
    ]);
```

### 自定义渲染

```php
$container->text('user_info', '用户信息')
    ->setRender(function ($value, $row) {
        $user = D('User')->find($row['user_id']);
        return $user ? "{$user['nickname']} ({$user['mobile']})" : '-';
    });
```

## Form 组件

### 基础用法

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
            $columns->text('name', '名称')
                ->addRule(new Required())
                ->setFormItemWidth(24);

            $columns->select('cate_id', '分类')
                ->setOptions(D('Category')->getFieldOptions())
                ->setFormItemWidth(12);

            $columns->money('price', '价格')
                ->addRule(new Required())
                ->setFormItemWidth(12);

            $columns->textarea('description', '描述')
                ->setFormItemWidth(24);

            $columns->picture('cover', '封面图')
                ->setFormItemWidth(24);

            $columns->radio('status', '状态')
                ->setOptions([1 => '启用', 0 => '禁用'])
                ->setFormItemWidth(24);
        })
        ->actions(function (Form\ActionsContainer $actions) {
            $actions->button('提交')->submit();
            $actions->button('重置')->reset();
        });

    return $form->render();
}
```

### 表单验证规则

```php
use AntdAdmin\Component\ColumnType\RuleType\Required;
use AntdAdmin\Component\ColumnType\RuleType\Email;
use AntdAdmin\Component\ColumnType\RuleType\Pattern;

$columns->text('email', '邮箱')
    ->addRule(new Required())
    ->addRule(new Email());

$columns->text('mobile', '手机号')
    ->addRule(new Pattern('/^1[3-9]\d{9}$/', '手机号格式不正确'));
```

## Modal 组件

### 弹窗表单

```php
$container->button('新增')
    ->setProps(['type' => 'primary'])
    ->modal((new \AntdAdmin\Component\Modal\Modal())
        ->setTitle('新增商品')
        ->setWidth('800px')
        ->setUrl(U('add')));
```

### 确认对话框

```php
$container->button('批量导入')
    ->confirm('确定要导入吗？', U('import'));
```

## 搜索配置

### 内联搜索

```php
$table->columns(function (Table\ColumnsContainer $container) {
    $container->text('name', '名称')
        ->setSearch(true);

    $container->select('status', '状态')
        ->setSearch(true)
        ->setValueEnum([
            1 => '启用',
            0 => '禁用',
        ]);

    $container->dateRange('create_time', '创建时间')
        ->setSearch(true);
});
```

## 完整示例

```php
<?php
namespace Admin\Controller;

use Gy_Library\GyListController;
use Gy_Library\DBCont;
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;
use AntdAdmin\Component\Form;
use AntdAdmin\Component\ColumnType\RuleType\Required;

class ProductController extends GyListController
{
    protected $modelName = 'Product';

    public function index()
    {
        $get_data = I('get.');
        $map = [];
        $this->buildSearchWhere($get_data, $map);

        $model = D($this->modelName);
        $count = $model->where($map)->count();
        $page = I('get.page', 1);
        $limit = I('get.limit', 20);
        $data = $model->where($map)->page($page, $limit)->order('id desc')->select();

        $table = new Table();
        $table->setMetaTitle('商品管理')
            ->columns(function (Table\ColumnsContainer $container) {
                $container->text('id', 'ID');
                $container->text('name', '名称')->setSearch(true);
                $container->money('price', '价格');
                $container->status('status', '状态')
                    ->setSearch(true)
                    ->setValueEnum([
                        DBCont::NORMAL_STATUS => ['text' => '启用', 'status' => 'Success'],
                        DBCont::FORBIDDEN_STATUS => ['text' => '禁用', 'status' => 'Error'],
                    ]);
                $container->dateTime('create_time', '创建时间');
                $container->action('', '操作')->actions(function ($container) {
                    $container->edit();
                    $container->delete();
                });
            })
            ->actions(function (Table\ActionsContainer $container) {
                $container->button('新增')
                    ->setProps(['type' => 'primary'])
                    ->modal((new \AntdAdmin\Component\Modal\Modal())
                        ->setTitle('新增商品')
                        ->setWidth('800px')
                        ->setUrl(U('add')));
                $container->delete();
                $container->forbid();
                $container->resume();
            })
            ->setDataSource($data)
            ->setPagination(new Pagination($page, $limit, $count))
            ->render();
    }

    public function add()
    {
        if (IS_POST) {
            $data = I('post.');
            $result = D($this->modelName)->createAdd($data);
            if ($result === false) {
                $this->error(D($this->modelName)->getError());
            }
            $this->success('添加成功');
        }

        $form = new Form();
        $form->setSubmitRequest('post', U('add'))
            ->setInitialValues(['status' => DBCont::NORMAL_STATUS])
            ->columns(function (Form\ColumnsContainer $columns) {
                $columns->text('name', '名称')
                    ->addRule(new Required())
                    ->setFormItemWidth(24);
                $columns->money('price', '价格')
                    ->addRule(new Required())
                    ->setFormItemWidth(12);
                $columns->radio('status', '状态')
                    ->setOptions([
                        DBCont::NORMAL_STATUS => '启用',
                        DBCont::FORBIDDEN_STATUS => '禁用',
                    ])
                    ->setFormItemWidth(12);
            });

        return $form->render();
    }
}
```

## API 参考

### Table 方法

| 方法 | 说明 |
|------|------|
| `setMetaTitle($title)` | 设置页面标题 |
| `columns($callback)` | 定义列配置 |
| `actions($callback)` | 定义顶部操作按钮 |
| `setDataSource($data)` | 设置数据源 |
| `setPagination($pagination)` | 设置分页 |
| `setSearch($enable)` | 启用/禁用搜索 |
| `setRowKey($key)` | 设置行唯一标识字段 |
| `render()` | 渲染表格 |

### Column 类型

| 方法 | 说明 |
|------|------|
| `text($name, $title)` | 文本列 |
| `number($name, $title)` | 数字列 |
| `money($name, $title)` | 金额列 |
| `status($name, $title)` | 状态列 |
| `date($name, $title)` | 日期列 |
| `dateTime($name, $title)` | 日期时间列 |
| `picture($name, $title)` | 图片列 |
| `action($name, $title)` | 操作列 |

### Form 方法

| 方法 | 说明 |
|------|------|
| `setSubmitRequest($method, $url)` | 设置提交方式和URL |
| `setInitialValues($values)` | 设置初始值 |
| `columns($callback)` | 定义表单字段 |
| `actions($callback)` | 定义表单按钮 |
| `render()` | 渲染表单 |

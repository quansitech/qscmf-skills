# Admin Controllers Reference

> QSCMF 后台管理控制器开发指南

## 概述

QSCMF 后台管理系统使用 `QsListController` 作为基础控制器，配合 AntdAdmin 组件实现 CRUD 功能。

## 标准模式

### 基本结构

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;

class XxxController extends QsListController
{
    protected $modelName = 'Xxx';

    public function index()
    {
        $table = new \Qscmf\Lib\AntdAdmin\Views\Table(
            $this,
            $this->buildTableColumns(...)
        );
        return $this->display($table);
    }

    protected function buildTableColumns($container)
    {
        // 表格列配置
    }
}
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `$modelName` | string | 关联的模型名称（如 'Demo', 'User'） |
| `$formWidth` | string | 表单宽度（如 '800px', '1000px'） |

### 核心方法

| 方法 | 说明 | 是否可重写 |
|------|------|-----------|
| `index()` | 列表页 | ⚠️ 可选 |
| `add()` | 新增页 | ⚠️ 可选 |
| `edit($id)` | 编辑页 | ⚠️ 可选 |
| `save()` | 保存（批量更新排序） | ⚠️ 可选 |
| `delete()` | 删除 | ⚠️ 可选 |
| `forbid()` | 禁用 | ⚠️ 可选 |
| `resume()` | 启用 | ⚠️ 可选 |
| `buildTableColumns()` | 构建表格列 | ✅ 推荐 |
| `addBuilderFormItem()` | 构建表单字段 | ✅ 推荐 |

## 表格列配置 (Table Columns)

### 基础列类型

```php
// 文本列
$container->text('field_name', '列标题');

// 下拉选择列
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList());

// 日期列
$container->date('create_date', '创建时间')
    ->setSearch(false);

// 图片列
$container->image('cover', '封面图');

// 操作列
$container->action('', '操作')
    ->actions(function ($actions) {
        $actions->edit()->modal(...);
        $actions->delete();
    });
```

### 列配置方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `setSearch(bool)` | 是否显示搜索 | `->setSearch(false)` |
| `editable()` | 可编辑（行内编辑） | `->editable()` |
| `setValueEnum(array)` | 设置枚举值 | `->setValueEnum([1=>'启用',0=>'禁用'])` |
| `setShowCondition()` | 条件显示 | `->setShowCondition('status', 'eq', 1)` |

### 操作列动作

```php
$actions->edit()->modal(
    (new \AntdAdmin\Component\Modal\Modal())
        ->setWidth('800px')
        ->setUrl(U('edit', ['id' => '__id__']))
        ->setTitle('编辑')
);

$actions->delete();

$actions->link('自定义操作')
    ->request('post', U('customAction'), ['id' => '__id__']);
```

## 表单字段配置 (Form Items)

### 基础字段类型

```php
// 文本输入
$columns->text('title', '标题')
    ->addRule(new \Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Required())
    ->setFormItemWidth(24);

// 文本域
$columns->textarea('summary', '摘要')
    ->setFormItemWidth(24);

// 数字输入
$columns->number('sort', '排序')
    ->setFormItemWidth(12);

// 下拉选择
$columns->select('cate_id', '分类')
    ->setValueEnum(D('Cate')->getField('id,name'))
    ->addRule(new Required())
    ->setFormItemWidth(24);
```

### 高级字段类型

```php
// 图片上传
$columns->image('cover_id', '封面图')
    ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
    ->setCrop('16/9')
    ->setTips('推荐尺寸 16:9')
    ->setFormItemWidth(24);

// 文件上传
$columns->file('file_id', '附件')
    ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('file'))
    ->setFormItemWidth(24);

// 富文本编辑器
$columns->ueditor('content', '详情内容')
    ->setFormItemWidth(24);

// 日期选择
$columns->date('publish_date', '发布日期')
    ->setFormItemWidth(12);

// 日期时间选择
$columns->datetime('create_time', '创建时间')
    ->setFormItemWidth(12);
```

### 表单验证规则

```php
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Required;
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Length;
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Email;

$columns->text('title', '标题')
    ->addRule(new Required())
    ->addRule(new Length(1, 200));

$columns->text('email', '邮箱')
    ->addRule(new Email());
```

### 依赖条件显示

```php
$columns->dependency()->columns(function (Form\ColumnsContainer $columns) {
    $columns->date('publish_date', '发布日期')
        ->addRule(new Required())
        ->setFormItemWidth(24);
})->setShowCondition('cate_id', 'gt', 0);
```

## 完整示例

### 简单 CRUD 控制器

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Form;
use AntdAdmin\Component\Modal\Modal;
use AntdAdmin\Component\ColumnType\RuleType\Required;

class XxxController extends QsListController
{
    protected $modelName = 'Xxx';
    protected $formWidth = '800px';

    public function index()
    {
        $get_data = I("get.");
        $map = [];
        $this->buildSearchWhere($get_data, $map);

        $model = D($this->modelName);
        $count = $model->where($map)->count();
        $per_page = C('ADMIN_PER_PAGE_NUM', null, false);

        if ($per_page === false) {
            $page = new \Gy_Library\GyPage($count);
        } else {
            $page = new \Gy_Library\GyPage($count, $per_page);
        }

        $data_list = $model->where($map)
            ->page($page->nowPage, $page->listRows)
            ->select();

        $table = new Table();
        $table->setMetaTitle('列表管理')
            ->actions(function (Table\ActionsContainer $container) {
                $container->button('新增')
                    ->setProps(['type' => 'primary'])
                    ->modal((new Modal())
                        ->setWidth($this->formWidth)
                        ->setUrl(U('add'))
                        ->setTitle('新增'));
                $container->forbid();
                $container->resume();
                $container->delete();
                $container->editSave();
            })
            ->columns(function (Table\ColumnsContainer $container) {
                $this->buildTableColumns($container);
            })
            ->setDataSource($data_list)
            ->setPagination(new Table\Pagination(
                $page->nowPage,
                $page->listRows,
                $count
            ))
            ->render();
    }

    protected function buildTableColumns(Table\ColumnsContainer $container)
    {
        $container->text('title', '标题');
        $container->select('cate_id', '分类')
            ->setValueEnum(D('Cate')->getField('id,name'));
        $container->text('sort', '排序')
            ->editable()->setSearch(false);
        $container->select('status', '状态')
            ->setValueEnum(\Qscmf\Lib\DBCont::getStatusList());
        $container->action('', '操作')
            ->actions(function (Table\ColumnType\ActionsContainer $container) {
                $container->edit()->modal(
                    (new Modal())
                        ->setWidth($this->formWidth)
                        ->setUrl(U('edit', ['id' => '__id__']))
                        ->setTitle('编辑')
                );
                $container->forbid();
                $container->delete();
            });
    }

    protected function addBuilderFormItem(Form &$form)
    {
        $form->columns(function (Form\ColumnsContainer $columns) {
            $columns->text('title', '标题')
                ->addRule(new Required())
                ->setFormItemWidth(24);

            $columns->select('cate_id', '分类')
                ->setValueEnum(D('Cate')->getField('id,name'))
                ->addRule(new Required())
                ->setFormItemWidth(24);

            $columns->image('cover_id', '封面图')
                ->setUploadRequest(\FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
                ->addRule(new Required())
                ->setCrop('16/9')
                ->setFormItemWidth(24);

            $columns->text('sort', '排序')
                ->setFormItemWidth(12);

            $columns->select('status', '状态')
                ->setValueEnum(\Qscmf\Lib\DBCont::getStatusList())
                ->addRule(new Required())
                ->setFormItemWidth(12);
        });
    }
}
```

## 扩展功能

### 批量操作

```php
public function batchProcess()
{
    $ids = I('ids');
    if (!$ids) {
        $this->error('请选择要操作的数据');
    }

    // 批量处理逻辑
    // ...
}
```

### Redis 锁

```php
use Qscmf\Lib\Redis\RedisLock;

public function batchProcess()
{
    $lock = new RedisLock('batch_process_' . $this->uid);

    if (!$lock->acquire()) {
        $this->error('操作进行中，请稍候');
    }

    try {
        // 批量逻辑
    } finally {
        $lock->release();
    }
}
```

### 知识库同步集成

```php
use Common\Lib\KnowledgeStore\KnowledgeStoreTrait;

class XxxController extends QsListController
{
    use KnowledgeStoreTrait;

    public function add()
    {
        if (IS_POST) {
            $result = parent::add();

            if ($result->status) {
                $this->syncToKnowledgeStore($data);
            }

            return $result;
        }
    }
}
```

## 最佳实践

### 1. 使用 DBCont 常量

```php
use Gy_Library\DBCont;

DBCont::NORMAL_STATUS    // = 1 (启用)
DBCont::DISABLE_STATUS   // = 0 (禁用)
DBCont::AUDIT_STATUS     // = 2 (待审核)

DBCont::getStatusList()  // [1 => '启用', 0 => '禁用']
```

### 2. 验证规则分离

在模型中定义验证规则，控制器中只定义表单规则：

```php
// Model
protected $_validate = [
    ['title', 'require', '标题不能为空', self::MUST_VALIDATE],
];

// Controller
$columns->text('title', '标题')
    ->addRule(new Required());
```

### 3. 表单宽度规范

```php
// 24 为一行（100%宽度）
$columns->text('title', '标题')->setFormItemWidth(24);

// 12 为半行（50%宽度）
$columns->text('field1', '字段1')->setFormItemWidth(12);
$columns->text('field2', '字段2')->setFormItemWidth(12);
```

### 4. 操作按钮规范

```php
// 顶部操作按钮
$container->button('新增')
    ->setProps(['type' => 'primary'])
    ->modal(...);

$container->forbid();    // 禁用
$container->resume();    // 启用
$container->delete();    // 删除
$container->editSave();  // 保存（排序）
```

### 5. 日志记录

```php
sysLogs('操作描述, id:' . $id);
```

## 相关文档

- [Abstract Base Patterns](abstract-base-patterns.md) - 抽象基类模式
- [Migration Metadata](migration-metadata.md) - 迁移文件元数据
- [Migration Guide](migration-guide.md) - 数据库迁移指南
- [Development Standards](development-standards.md) - 开发规范

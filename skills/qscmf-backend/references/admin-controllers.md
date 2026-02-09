# Admin Controllers Reference

> 详细的 QSCMF Admin Controller 开发指南
>
> 完整文档请查看：`app/Admin/Controller/` 目录下的现有实现

## Standard CRUD Pattern

基本结构继承 `QsListController`：

```php
<?php
namespace Admin\Controller;
use Admin\Controller\QsListController;

class DemoController extends QsListController
{
    protected $modelName = 'Demo';

    public function index()
    {
        $table = new \Qscmf\Lib\AntdAdmin\Views\Table($this, $this->buildTableColumns(...));
        return $this->display($table);
    }

    protected function buildTableColumns($container)
    {
        // Table columns configuration
    }
}
```

## Key Components

### Table Columns (列表页)

```php
$container->text('title', '标题');
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList());
$container->image('cover', '封面');
$container->date('create_time', '创建时间')->setSearch(false);
$container->action('操作', 'actions')
    ->actions(function ($actions) {
        $actions->edit()->modal(...);
        $actions->delete();
    });
```

### Form Items (表单)

```php
$columns->text('title', '标题')
    ->addRule(new Required());
$columns->ueditor('content', '详情');
$columns->image('cover_id', '封面')
    ->setCrop('16/9');
$columns->select('cate_id', '分类')
    ->setValueEnum(D('Cate')->getField('id,name'));
```

## Abstract Base Pattern

多个相似模块可使用抽象基类：

```php
abstract class BaseCategoryController extends QsListController
{
    abstract protected function getModelName(): string;

    protected function buildTableColumns($container) {
        // 共同的列配置
    }
}
```

## Knowledge Store Sync

知识库同步集成：

```php
public function save()
{
    $result = parent::save();

    if ($result->status) {
        // 触发知识库同步
        KnowledgeStoreHelper::sync('resource', $this->save_id);
    }

    return $result;
}
```

## Redis Lock Usage

批量操作加锁：

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

---

**更多示例**：
- `app/Admin/Controller/ProductController.class.php`
- `app/Admin/Controller/ArticleController.class.php`
- `app/Admin/Controller/DemoController.class.php`

---
title: Guide Mode (v14)
version: v14
impact: MEDIUM
when: "QSCMF 开发问题、框架使用指南、最佳实践咨询"
---

# Guide Mode (v14)

## Triggers

Default mode for QSCMF development questions.

Examples:
- "如何实现 QsListController 的 CRUD?"
- "AntdAdmin Table 组件如何使用?"
- "如何编写 PHPUnit 测试?"
- "怎样配置表单验证?"

---

## Stance

作为 QSCMF 开发助手，提供：

1. **框架指南** - 解释 QSCMF 架构和组件用法
2. **代码示例** - 提供可直接使用的代码片段
3. **最佳实践** - 推荐符合项目规范的做法
4. **问题诊断** - 帮助排查开发中遇到的问题

---

## Quick Reference

### Admin CRUD (QsListController)

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;

class ProductController extends QsListController
{
    protected $modelName = 'Product';

    public function index()
    {
        $map = $this->buildSearchMap(I('get.'));
        $model = D('Product')->where($map);
        $total = $model->count();

        $builder = $this->builder();
        $this->buildTableColumns($builder);
        $this->buildSearchForm($builder);
        $this->buildButtons($builder);

        $list = $model->order('id desc')->select();
        $builder->setData($list);
        $builder->display();
    }
}
```

### RESTful API (RestController)

```php
<?php
namespace Api\Controller;

use Api\Controller\RestController;

class ProductController extends RestController
{
    protected $modelName = 'Product';

    public function index_get()
    {
        $page = I('get.page', 1, 'intval');
        $pageSize = I('get.page_size', 20, 'intval');

        $map = ['status' => DBCont::NORMAL_STATUS];
        $list = D('Product')->where($map)
            ->page($page, $pageSize)
            ->select();

        $this->response([
            'status' => true,
            'data' => $list,
            'meta' => ['total' => D('Product')->where($map)->count()]
        ]);
    }
}
```

### Model (GyListModel)

```php
<?php
namespace Common\Model;

use Gy_Library\GyListModel;

class ProductModel extends GyListModel
{
    protected $tableName = 'product';

    protected $_validate = [
        ['product_name', 'require', '商品名称不能为空', self::MUST_VALIDATE],
    ];

    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT, 'function'],
    ];
}
```

---

## Key References

| Topic | Reference |
|-------|-----------|
| ListBuilder API | [rules/listbuilder-api.md](../rules/listbuilder-api.md) |
| FormBuilder API | [rules/formbuilder-api.md](../rules/formbuilder-api.md) |
| v14 Features | [rules/v14-features.md](../rules/v14-features.md) |
| Inertia.js | [rules/inertia.md](../rules/inertia.md) |
| Testing | [references/testing.md](../references/testing.md) |
| CRUD Patterns | [references/crud-patterns.md](../references/crud-patterns.md) |

---

## Common Questions

### Q: 如何添加表格列？

```php
$builder->addTableColumn('field_name', '显示名称', $typeOrOptions);
```

### Q: 如何添加搜索条件？

```php
$builder->addSearchItem('field_name', 'text|select|date', '标签', $options);
```

### Q: 如何使用 Redis Lock？

```php
use Gy_Library\RedisLock;

$lock = new RedisLock('batch_job_' . $id, 300);
if ($lock->acquire()) {
    try {
        // 执行批量操作
    } finally {
        $lock->release();
    }
}
```

> 详见 [pattern-redis-lock.md](../rules/pattern/pattern-redis-lock.md)

---
title: Guide Mode (v13)
version: v13
impact: MEDIUM
when: "QSCMF 开发问题、框架使用指南、最佳实践咨询"
---

# Guide Mode (v13)

## Triggers

Default mode for QSCMF v13 development questions.

Examples:
- "如何实现 QsListController 的 CRUD?"
- "ListBuilder API 如何使用?"
- "如何编写 PHPUnit 测试?"
- "怎样配置表单验证?"

---

## Stance

作为 QSCMF v13 开发助手，提供：

1. **框架指南** - 解释 QSCMF v13 架构和组件用法
2. **代码示例** - 提供可直接使用的代码片段（jQuery 风格）
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

    protected function buildTableColumns($builder)
    {
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('name', '名称');
        $builder->addTableColumn('status', '状态', DBCont::getStatusList());
    }

    protected function buildSearchForm($builder)
    {
        $builder->addSearchItem('keyword', 'text', '关键词');
        $builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());
    }
}
```

### RESTful API (RestController)

```php
<?php
namespace Api\Controller;

use Qscmf\Api\RestController;
use QscmfApiCommon\Cache\Response;

class ProductController extends RestController
{
    protected $noAuthorization = ['gets', 'detail'];

    public function gets(): Response
    {
        $page = (int)I('get.page', 1);
        $limit = (int)I('get.limit', 10);

        $map = ['status' => DBCont::NORMAL_STATUS];
        $list = D('Product')->where($map)
            ->page($page, $limit)
            ->select();

        $total = D('Product')->where($map)->count();

        return new Response('成功', 1, [
            'list' => $list,
            'total' => $total,
            'page' => $page,
            'limit' => $limit
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
| Legacy jQuery | [rules/legacy-jquery.md](../rules/legacy-jquery.md) |
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
$builder->addSearchItem('field_name', 'text|select|date', '标签', $default, $options);
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

---

## v13-Specific: jQuery Rendering

v13 使用 jQuery + Bootstrap 3 渲染模式：

```php
// 环境变量
ANTD_ADMIN_BUILDER_ENABLE = false  // v13 默认值
```

### Bootstrap CSS Classes

```html
<!-- 状态徽章 -->
<span class="label label-success">启用</span>
<span class="label label-default">禁用</span>

<!-- 按钮 -->
<button class="btn btn-primary">新增</button>
<button class="btn btn-danger">删除</button>
```

### jQuery 事件处理

```javascript
// 表单提交
$('#myForm').on('submit', function(e) {
    e.preventDefault();
    $.post($(this).attr('action'), $(this).serialize(), function(res) {
        if (res.status) {
            location.reload();
        } else {
            alert(res.msg);
        }
    });
});
```

> 详见 [legacy-jquery.md](../rules/legacy-jquery.md)

---
title: Abstract Base Pattern (v13)
impact: HIGH
impactDescription: Reduces code duplication for similar modules
tags: pattern, abstract, base, v13
---

## Abstract Base Pattern (v13)

Create reusable base classes for similar modules in QSCMF v13.

### When to Use This Rule

- Multiple modules with similar functionality
- Reducing code duplication
- Creating consistent CRUD behavior

---

## Abstract Base Controller

```php
// app/Admin/Controller/BaseCateController.class.php

namespace Admin\Controller;

use Admin\Controller\QsListController;
use Gy_Library\DBCont;

abstract class BaseCateController extends QsListController
{
    // Subclass must define these
    abstract protected function getCateType(): string;
    abstract protected function getModelName(): string;
    abstract protected function getTableName(): string;

    public function index()
    {
        $map = [
            'cate_type' => $this->getCateType()
        ];
        $map = array_merge($map, $this->buildSearchMap(I('get.')));

        $list = D($this->getModelName())
            ->where($map)
            ->order('sort asc, id desc')
            ->select();

        $builder = $this->builder();
        $builder->setMetaTitle($this->getTitle() . '列表');
        $builder->setCheckBox(true);

        $this->buildTableColumns($builder);
        $this->buildSearchForm($builder);
        $this->buildButtons($builder);

        $builder->setData($list);
        $builder->display();
    }

    protected function buildTableColumns($builder)
    {
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('name', '名称');
        $builder->addTableColumn('sort', '排序', 'num');
        $builder->addTableColumn('status', '状态', DBCont::getStatusList());
        $builder->addTableColumn('create_time', '创建时间');
    }

    protected function buildButtons($builder)
    {
        $builder->addTopButton('addnew', ['title' => '新增']);
        $builder->addTopButton('forbid');
        $builder->addTopButton('resume');
        $builder->addTopButton('delete');
        $builder->addRightButton('edit');
        $builder->addRightButton('delete');
    }

    public function save()
    {
        $data = I('post.');

        // Auto-set cate_type
        $data['cate_type'] = $this->getCateType();

        $result = parent::save($data);

        if ($result !== false) {
            $this->success('保存成功', U('index'));
        } else {
            $this->error('保存失败');
        }
    }
}
```

---

## Concrete Implementation

```php
// app/Admin/Controller/ArticleCateController.class.php

namespace Admin\Controller;

use Admin\Controller\BaseCateController;

class ArticleCateController extends BaseCateController
{
    protected function getCateType(): string
    {
        return 'article';
    }

    protected function getModelName(): string
    {
        return 'Cate';
    }

    protected function getTableName(): string
    {
        return 'cate';
    }

    protected function getTitle(): string
    {
        return '文章分类';
    }

    // Can override parent methods for customization
    protected function buildTableColumns($builder)
    {
        parent::buildTableColumns($builder);

        // Add article-specific column
        $builder->addTableColumn('article_count', '文章数', 'num');
    }
}
```

```php
// app/Admin/Controller/ProductCateController.class.php

namespace Admin\Controller;

use Admin\Controller\BaseCateController;

class ProductCateController extends BaseCateController
{
    protected function getCateType(): string
    {
        return 'product';
    }

    protected function getModelName(): string
    {
        return 'Cate';
    }

    protected function getTableName(): string
    {
        return 'cate';
    }

    protected function getTitle(): string
    {
        return '商品分类';
    }
}
```

---

## Abstract Base Model

```php
// app/Common/Model/BaseCateModel.class.php

namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;

abstract class BaseCateModel extends GyListModel
{
    protected $tableName = 'cate';
    protected $pk = 'id';

    // Subclass must define cate_type
    abstract protected function getCateType(): string;

    protected function _initialize()
    {
        parent::_initialize();

        // Auto-scope by cate_type
        $this->where(['cate_type' => $this->getCateType()]);
    }

    public function getList(array $map = []): array
    {
        $map['cate_type'] = $this->getCateType();
        return $this->where($map)->order('sort asc')->select();
    }

    public function addCate(array $data): int
    {
        $data['cate_type'] = $this->getCateType();
        return $this->add($data);
    }
}
```

---

## Benefits

1. **Code Reuse** - Common logic in one place
2. **Consistency** - All similar modules behave the same
3. **Maintainability** - Fix bug in one place
4. **Extensibility** - Override specific methods when needed

---

## Related Rules

- [Pattern Redis Lock](pattern-redis-lock.md) - Distributed locking
- [Pattern Queue Job](pattern-queue-job.md) - Async processing
- [Abstract Base Patterns Reference](../../references/abstract-base-patterns.md) - Complete guide

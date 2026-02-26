# Abstract Base Patterns

Reusable base class patterns for QSCMF v14.

## Abstract Model

```php
abstract class CategoryModel extends GyListModel
{
    abstract protected function getTableName(): string;
    abstract protected function getModuleTitle(): string;

    public function getTree(): array
    {
        return $this->where(['status' => DBCont::NORMAL_STATUS])
            ->order('sort asc')
            ->select();
    }
}
```

## Concrete Implementation

```php
class ProductCateModel extends CategoryModel
{
    protected function getTableName(): string
    {
        return 'product_cate';
    }

    protected function getModuleTitle(): string
    {
        return '商品分类';
    }
}
```

## When to Use

- Multiple similar modules
- Shared behavior across entities
- Code reuse without duplication

---

## Related Documentation
- [Model Guide](model-guide.md)
- [Abstract Base Pattern](../rules/pattern/pattern-abstract-base.md)

# Model Guide

Complete guide for GyListModel in QSCMF v14.

## Base Class

```php
use Gy_Library\GyListModel;

class ProductModel extends GyListModel
{
    protected $tableName = 'product';
}
```

## Validation

```php
protected $_validate = [
    ['product_name', 'require', '名称不能为空', self::MUST_VALIDATE],
    ['product_code', '', '编码已存在', self::VALUE_VALIDATE, 'unique'],
];
```

## Auto Complete

```php
protected $_auto = [
    ['create_time', 'time', self::MODEL_INSERT, 'function'],
    ['update_time', 'time', self::MODEL_BOTH, 'function'],
];
```

## Common Methods

```php
public function getActiveList(): array
{
    return $this->where(['status' => DBCont::NORMAL_STATUS])
        ->order('sort asc')
        ->select();
}
```

---

## Related Documentation
- [Admin Controllers](admin-controllers.md)
- [Migration Guide](migration-guide.md)

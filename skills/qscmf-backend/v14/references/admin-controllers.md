# Admin Controllers Reference

Complete guide for building admin CRUD controllers in QSCMF v14.

## Base Class

```php
use Gy_Library\GyListController;

class ProductController extends GyListController
{
    protected $modelName = 'Product';
}
```

## AntdAdmin Component API

```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;
use AntdAdmin\Component\Form;
use AntdAdmin\Component\Modal\Modal;

public function index()
{
    $table = new Table();
    $table->setMetaTitle('列表')
        ->columns(function (Table\ColumnsContainer $container) {
            $container->text('name', '名称');
        })
        ->setDataSource($data)
        ->render();
}
```

## Key Methods

| Method | Description |
|--------|-------------|
| `index()` | List page |
| `add()` | Add form |
| `edit()` | Edit form |
| `delete()` | Delete record |
| `forbid()` | Disable record |
| `resume()` | Enable record |

## Status Constants

```php
use Gy_Library\DBCont;

DBCont::NORMAL_STATUS    // = 1
DBCont::DISABLE_STATUS   // = 0
DBCont::getStatusList()  // [1 => '启用', 0 => '禁用']
```

---

## Related Documentation
- [Table Columns](../rules/crud/crud-table-columns-v14.md)
- [AntdAdmin Components](../rules/antdadmin.md)

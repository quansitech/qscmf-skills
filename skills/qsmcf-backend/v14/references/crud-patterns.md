# CRUD Patterns

Common development patterns for QSCMF v14.

## Standard CRUD

```php
class ProductController extends GyListController
{
    protected $modelName = 'Product';

    public function index() { /* List */ }
    public function add() { /* Create */ }
    public function edit() { /* Update */ }
    public function delete() { /* Delete */ }
}
```

## Search Pattern

```php
protected function buildSearchWhere($get_data, &$map)
{
    if (!empty($get_data['keyword'])) {
        $map['product_name'] = ['like', '%' . $get_data['keyword'] . '%'];
    }
    if (isset($get_data['status']) && $get_data['status'] !== '') {
        $map['status'] = $get_data['status'];
    }
}
```

## Transaction Pattern

```php
D('Product')->startTrans();
try {
    // Operations
    D('Product')->commit();
} catch (\Exception $e) {
    D('Product')->rollback();
    throw $e;
}
```

## Cache Pattern

```php
public function getById($id)
{
    $cache_key = 'product_' . $id;
    $data = S($cache_key);
    if ($data === false) {
        $data = $this->find($id);
        S($cache_key, $data, 3600);
    }
    return $data;
}
```

---

## Related Documentation
- [Admin Controllers](admin-controllers.md)
- [Model Guide](model-guide.md)

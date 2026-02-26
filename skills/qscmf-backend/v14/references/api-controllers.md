# API Controllers Reference

Complete guide for building RESTful API controllers in QSCMF v14.

## Base Class

```php
use Api\Controller\RestController;

class ProductController extends RestController
{
    protected $modelName = 'Product';
}
```

## Standard Methods

```php
// GET /api/product
public function index_get() {}

// GET /api/product/:id
public function detail_get($id = null) {}

// POST /api/product
public function index_post() {}

// PUT /api/product/:id
public function detail_put($id = null) {}

// DELETE /api/product/:id
public function detail_delete($id = null) {}
```

## Response Format

```php
// Success
$this->response([
    'status' => true,
    'data' => $data,
]);

// Error
$this->response([
    'status' => false,
    'msg' => 'Error message',
], 400);
```

---

## Related Documentation
- [API Response Format](../rules/api/api-response-format.md)
- [API Pagination](../rules/api/api-pagination-cursor.md)

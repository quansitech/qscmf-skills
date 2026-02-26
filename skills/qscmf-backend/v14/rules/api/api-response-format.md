---
title: API Response Format (v14)
impact: HIGH
impactDescription: Required for all API endpoints
tags: api, response, format, v14, php82
---

## API Response Format (v14)

Standard JSON response format for QSCMF v14 API endpoints with PHP 8.2+ modern patterns.

### When to Use This Rule

- Creating new API endpoints
- Formatting API responses
- Handling errors consistently
- Building RESTful APIs with Laravel response helpers

---

## Standard Response Format

All API responses follow a consistent JSON structure with proper HTTP status codes:

```php
// Success response structure
[
    'status' => true,      // boolean: success indicator
    'data' => mixed,       // Response payload (nullable on error)
    'msg' => string,       // Message (optional on success)
    'meta' => array        // Metadata for pagination, etc. (optional)
]

// Error response structure
[
    'status' => false,     // boolean: failure indicator
    'msg' => string,       // Error message
    'errors' => array      // Validation errors (optional)
]
```

---

## Success Responses

### Simple Success

```php
public function delete_delete(int $id): void
{
    $result = D('Product')->softDelete($id);

    $this->response([
        'status' => true,
        'msg' => '删除成功',
    ]);
}
```

### With Data

```php
public function detail_get(int $id): void
{
    $data = D('Product')->find($id);

    if (!$data) {
        $this->response([
            'status' => false,
            'msg' => '记录不存在',
        ], 404);
        return;
    }

    $this->response([
        'status' => true,
        'data' => $data,
    ]);
}
```

### Created Resource

```php
public function create_post(): void
{
    $data = I('post.');

    $id = D('Product')->createAdd($data);

    $this->response([
        'status' => true,
        'data' => ['id' => $id],
        'msg' => '创建成功',
    ], 201);
}
```

### List with Pagination

```php
public function index_get(): void
{
    $page = (int)I('get.page', 1);
    $pageSize = (int)I('get.page_size', 15);

    $list = D('Product')->where(['status' => DBCont::NORMAL_STATUS])
        ->page($page, $pageSize)
        ->select();

    $total = D('Product')->where(['status' => DBCont::NORMAL_STATUS])->count();

    $this->response([
        'status' => true,
        'data' => $list,
        'meta' => [
            'total' => $total,
            'page' => $page,
            'page_size' => $pageSize,
            'total_pages' => (int)ceil($total / $pageSize),
        ],
    ]);
}
```

---

## Error Responses

### Validation Error

```php
public function create_post(): void
{
    $data = I('post.');

    $errors = $this->validate($data, [
        'product_name' => 'required',
        'price' => 'required|numeric|min:0',
    ]);

    if (!empty($errors)) {
        $this->response([
            'status' => false,
            'msg' => '验证失败',
            'errors' => $errors,
        ], 422);
        return;
    }

    // Continue with creation
}
```

### Not Found Error

```php
public function detail_get(int $id): void
{
    $data = D('Product')->find($id);

    if (!$data) {
        $this->response([
            'status' => false,
            'msg' => '记录不存在',
        ], 404);
        return;
    }

    $this->response([
        'status' => true,
        'data' => $data,
    ]);
}
```

### Unauthorized Error

```php
public function profile_get(): void
{
    $user = $this->getCurrentUser();

    if (!$user) {
        $this->response([
            'status' => false,
            'msg' => '请先登录',
        ], 401);
        return;
    }

    $this->response([
        'status' => true,
        'data' => $user,
    ]);
}
```

### Forbidden Error

```php
public function adminOnly_get(): void
{
    $user = $this->getCurrentUser();

    if ($user['role_id'] !== ROLE_ADMIN) {
        $this->response([
            'status' => false,
            'msg' => '无权限访问',
        ], 403);
        return;
    }

    // Admin logic
}
```

### Server Error

```php
public function process_post(): void
{
    try {
        $result = $this->complexOperation();

        $this->response([
            'status' => true,
            'data' => $result,
        ]);
    } catch (\Exception $e) {
        // Log error for debugging
        Log::error('API Error: ' . $e->getMessage(), [
            'trace' => $e->getTraceAsString(),
        ]);

        $this->response([
            'status' => false,
            'msg' => '服务器错误，请稍后重试',
        ], 500);
    }
}
```

---

## HTTP Status Codes

Use appropriate HTTP status codes to indicate response type:

| Code | Use Case | Example |
|------|----------|---------|
| 200 | Success | GET, PUT, PATCH success |
| 201 | Created | POST creates new resource |
| 204 | No Content | DELETE success |
| 400 | Bad Request | Invalid request format |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Valid token, insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 422 | Validation Error | Invalid input data |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Unexpected server error |

---

## Laravel Response Helpers (v14)

v14 projects can use Laravel response helpers for richer responses:

```php
use Illuminate\Http\JsonResponse;

public function index_get(): JsonResponse
{
    $list = D('Product')->where(['status' => DBCont::NORMAL_STATUS])->select();

    return response()->json([
        'status' => true,
        'data' => $list,
    ]);
}

// With headers
public function export_get(): JsonResponse
{
    $data = $this->getExportData();

    return response()->json([
        'status' => true,
        'data' => $data,
    ])->withHeaders([
        'X-Export-Count' => count($data),
        'X-Export-Time' => time(),
    ]);
}
```

---

## PHP 8.2+ Type Declarations

Use strict typing in v14:

```php
public function detail_get(int $id): void
{
    $product = D('Product')->findOrFail($id);

    $this->response([
        'status' => true,
        'data' => $product->toArray(),
    ]);
}

private function validate(array $data, array $rules): array
{
    $errors = [];

    foreach ($rules as $field => $rule) {
        $ruleList = explode('|', $rule);

        if (in_array('required', $ruleList) && empty($data[$field])) {
            $errors[$field] = "{$field} 不能为空";
        }
    }

    return $errors;
}
```

---

## Response Helper Trait

Create a reusable trait for consistent responses:

```php
<?php
namespace Api\Traits;

trait ApiResponseTrait
{
    protected function successResponse(mixed $data = null, string $msg = '操作成功', int $code = 200): void
    {
        $response = [
            'status' => true,
            'msg' => $msg,
        ];

        if ($data !== null) {
            $response['data'] = $data;
        }

        $this->response($response, $code);
    }

    protected function errorResponse(string $msg, int $code = 400, array $errors = []): void
    {
        $response = [
            'status' => false,
            'msg' => $msg,
        ];

        if (!empty($errors)) {
            $response['errors'] = $errors;
        }

        $this->response($response, $code);
    }

    protected function paginatedResponse(array $list, int $total, int $page, int $pageSize): void
    {
        $this->response([
            'status' => true,
            'data' => $list,
            'meta' => [
                'total' => $total,
                'page' => $page,
                'page_size' => $pageSize,
                'total_pages' => (int)ceil($total / $pageSize),
            ],
        ]);
    }
}
```

---

## Related Rules

- [API Pagination](api-pagination-cursor.md) - Pagination strategies
- [API Auth JWT](api-auth-jwt.md) - JWT authentication
- [API Controllers Reference](../../references/api-controllers.md) - Complete guide

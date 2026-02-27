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
    'status' => 1,         // integer: 1 = success, 0 = failure
    'info' => string,      // Message
    'data' => mixed,       // Response payload (nullable on error)
]

// Error response structure
[
    'status' => 0,         // integer: 1 = success, 0 = failure
    'info' => string,      // Error message
    'data' => null,        // Response payload
]
```

**注意**: `status` 是整数 (1/0)，不是布尔值。消息字段是 `info`，不是 `msg`。

---

## Two Response Patterns

QSCMF v14 支持两种响应模式：

### Pattern 1: Response 对象 (推荐用于新代码)

使用 `QscmfApiCommon\Cache\Response` 类返回响应对象：

```php
use QscmfApiCommon\Cache\Response;

class LoginController extends RestController
{
    public function create()
    {
        // Success
        return new Response('登录成功', 1, $formattedUser);

        // Error
        return new Response('token不能为空', 0);
    }
}
```

**Response 构造函数**:
```php
__construct(
    string $message,    // 用户消息
    int $status,        // 1 = 成功, 0 = 失败
    mixed $data = '',   // 响应数据
    int $code = 200,    // HTTP 状态码
    array $extra_res_data = []
)
```

### Pattern 2: response() 方法 (传统方式)

使用 `$this->response()` 方法直接输出：

```php
$this->response('删除成功', 1);
$this->response('记录不存在', 0, null, 404);
```

**response() 签名**:
```php
protected function response(
    string $message,    // 用户消息
    int $status,        // 1 = 成功, 0 = 失败
    mixed $data = '',   // 响应数据
    int $code = 200,    // HTTP 状态码
    array $extra_res_data = []
): void
```

---

## Success Responses

### Simple Success

```php
public function delete_delete(int $id): void
{
    $result = D('Product')->softDelete($id);

    $this->response('删除成功', 1);
}
```

### With Data

```php
public function detail_get(int $id): void
{
    $data = D('Product')->find($id);

    if (!$data) {
        $this->response('记录不存在', 0, null, 404);
        return;
    }

    $this->response('获取成功', 1, $data);
}
```

### Created Resource

```php
public function create_post(): void
{
    $data = I('post.');

    $id = D('Product')->createAdd($data);

    $this->response('创建成功', 1, ['id' => $id], 201);
}
```

---

## Error Responses

### Validation Error

```php
public function create_post(): void
{
    $data = I('post.');

    if (empty($data['product_name'])) {
        $this->response('产品名称不能为空', 0);
        return;
    }

    if (!is_numeric($data['price']) || $data['price'] < 0) {
        $this->response('价格必须为非负数', 0);
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
        $this->response('记录不存在', 0, null, 404);
        return;
    }

    $this->response('获取成功', 1, $data);
}
```

### Unauthorized Error

```php
public function profile_get(): void
{
    $user = $this->getCurrentUser();

    if (!$user) {
        $this->response('请先登录', 0, null, 401);
        return;
    }

    $this->response('获取成功', 1, $user);
}
```

### Forbidden Error

```php
public function adminOnly_get(): void
{
    $user = $this->getCurrentUser();

    if ($user['role_id'] !== ROLE_ADMIN) {
        $this->response('无权限访问', 0, null, 403);
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
        $this->response('操作成功', 1, $result);
    } catch (\Exception $e) {
        Log::error('API Error: ' . $e->getMessage(), [
            'trace' => $e->getTraceAsString(),
        ]);

        $this->response('服务器错误，请稍后重试', 0, null, 500);
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

v14 projects can use Laravel response helpers,但推荐使用 RestController 的 `$this->response()` 方法或 `Response` 对象：

```php
// 推荐：使用 RestController 的 response 方法
public function index_get(): void
{
    $list = D('Product')->where(['status' => DBCont::NORMAL_STATUS])->select();
    $this->response('获取成功', 1, $list);
}

// 或者使用 Response 对象（支持缓存）
use QscmfApiCommon\Cache\Response;

public function index_get(): Response
{
    $list = D('Product')->where(['status' => DBCont::NORMAL_STATUS])->select();
    return new Response('获取成功', 1, $list);
}
```

---

## PHP 8.2+ Type Declarations

Use strict typing in v14:

```php
public function detail_get(int $id): void
{
    $product = D('Product')->find($id);

    if (!$product) {
        $this->response('记录不存在', 0, null, 404);
        return;
    }

    $this->response('获取成功', 1, $product);
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
        $this->response($msg, 1, $data, $code);
    }

    protected function errorResponse(string $msg, int $code = 400): void
    {
        $this->response($msg, 0, null, $code);
    }

    protected function paginatedResponse(array $list, int $total, int $page, int $pageSize): void
    {
        $this->response('获取成功', 1, [
            'list' => $list,
            'total' => $total,
            'page' => $page,
            'page_size' => $pageSize,
            'total_pages' => (int)ceil($total / $pageSize),
        ]);
    }
}
```

---

## Related Rules

- [API Pagination](api-pagination-cursor.md) - Pagination strategies
- [API Auth JWT](api-auth-jwt.md) - JWT authentication
- [API Controllers Reference](../../references/api-controllers.md) - Complete guide

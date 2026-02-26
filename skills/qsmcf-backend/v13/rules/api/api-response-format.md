---
title: API Response Format (v13)
impact: HIGH
impactDescription: Required for all API endpoints
tags: api, response, format, v13
---

## API Response Format (v13)

Standard response format for QSCMF v13 API endpoints.

### When to Use This Rule

- Creating new API endpoints
- Formatting API responses
- Handling errors consistently

---

## Standard Response Format

All API responses use `QscmfApiCommon\Cache\Response`:

```php
use QscmfApiCommon\Cache\Response;

// Success response
return new Response('成功', 1, $data);

// Error response
return new Response('错误信息', 0);
```

### Response Structure

```json
{
    "status": 1,        // 1 = success, 0 = failure
    "msg": "成功",       // Message
    "data": {}          // Response data (nullable)
}
```

---

## Success Responses

### Simple Success

```php
return new Response('操作成功', 1);
```

### With Data

```php
return new Response('成功', 1, [
    'id' => 1,
    'name' => 'Product'
]);
```

### List Response

```php
return new Response('成功', 1, [
    'list' => $list,
    'total' => $total,
    'page' => $page,
    'limit' => $limit
]);
```

---

## Error Responses

### Validation Error

```php
if (empty($data['name'])) {
    return new Response('名称不能为空', 0);
}
```

### Not Found Error

```php
$data = D('Product')->find($id);
if (!$data) {
    return new Response('记录不存在', 0);
}
```

### Method Error

```php
if (!IS_POST) {
    return new Response('请求方法错误', 0);
}
```

### Server Error

```php
try {
    // Operation
} catch (\Exception $e) {
    return new Response('操作失败: ' . $e->getMessage(), 0);
}
```

---

## HTTP Status Codes

Always return HTTP 200 with status in JSON body:

```php
// Correct
return new Response('成功', 1, $data);  // HTTP 200, status: 1

// Incorrect - don't use HTTP status codes for API errors
// return response()->json(['error' => 'Not found'], 404);
```

---

## Related Rules

- [API Pagination](api-pagination-cursor.md) - Pagination strategies
- [API Auth JWT](api-auth-jwt.md) - JWT authentication
- [API Controllers Reference](../../references/api-controllers.md) - Complete guide

---
title: RESTful API Response Format
impact: HIGH
impactDescription: Standard API response across all endpoints
tags: api, response, format, both
---

## RESTful API Response Format

Use standard response format for all API endpoints.

**Standard Response:**
```json
{
  "msg": "成功",
  "status": 1,
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "limit": 10
  }
}
```

**Response Fields:**
- `msg`: Message string
- `status`: Status code (1=success, 0=failure)
- `data`: Response data

**Status Codes:**
```php
use QscmfApiCommon\Cache\Response;

// Success
return new Response('操作成功', 1, $data);

// Error
return new Response('操作失败', 0, [], $errorCode);

// With custom message
return new Response('参数错误', 0, [], 'PARAM_ERROR');
```

**List Endpoint Example:**
```php
public function gets(): Response
{
    $get_data = I('get.');
    $page = (int)($get_data['page'] ?? 1);
    $limit = (int)($get_data['limit'] ?? 10);

    $where = $this->buildWhere($get_data);
    $total = D($this->modelName)->where($where)->count();
    $list = D($this->modelName)
        ->where($where)
        ->order('id desc')
        ->page($page, $limit)
        ->select();

    $data = $this->formatList($list);

    return new Response('成功', 1, [
        'list' => $data,
        'total' => $total,
        'page' => $page,
        'limit' => $limit
    ]);
}
```

**Error Response:**
```php
try {
    $result = $this->service->processData($data);
    return new Response('成功', 1, $result);
} catch (\Exception $e) {
    return new Response($e->getMessage(), 0, [], 'PROCESS_ERROR');
}
```

**See Also:**
- [Pagination](../api/api-pagination-cursor.md)
- [Authentication](../api/api-auth-jwt.md)
- [RestController Base](../../references/api-controllers.md)

**Version Differences:**
- **v14**: Refactored upload API
- **v13**: Legacy upload API

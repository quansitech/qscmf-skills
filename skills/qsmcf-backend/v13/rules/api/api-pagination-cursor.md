---
title: API Pagination (v13)
impact: HIGH
impactDescription: Required for all list endpoints
tags: api, pagination, cursor, v13
---

## API Pagination (v13)

Pagination strategies for QSCMF v13 API endpoints.

### When to Use This Rule

- Implementing list endpoints
- Handling large datasets
- Building infinite scroll

---

## Offset Pagination (Default)

Standard page-based pagination:

```php
public function gets(): Response
{
    $page = (int)I('get.page', 1);
    $limit = (int)I('get.limit', 10);
    $limit = min($limit, 100);  // Max limit

    $where = $this->buildWhere();

    $total = D('Product')->where($where)->count();
    $list = D('Product')
        ->where($where)
        ->page($page, $limit)
        ->order('id desc')
        ->select();

    return new Response('成功', 1, [
        'list' => $list,
        'total' => $total,
        'page' => $page,
        'limit' => $limit,
        'total_pages' => ceil($total / $limit)
    ]);
}
```

**Request:**
```
GET /api.php/Product/gets?page=1&limit=10
```

**Response:**
```json
{
    "status": 1,
    "msg": "成功",
    "data": {
        "list": [...],
        "total": 100,
        "page": 1,
        "limit": 10,
        "total_pages": 10
    }
}
```

---

## Cursor Pagination

For large datasets with consistent ordering:

```php
public function gets(): Response
{
    $cursor = I('get.cursor', 0, 'intval');
    $limit = (int)I('get.limit', 10);
    $limit = min($limit, 100);

    $where = $this->buildWhere();

    // Add cursor condition
    if ($cursor > 0) {
        $where['id'] = ['lt', $cursor];
    }

    $list = D('Product')
        ->where($where)
        ->limit($limit + 1)  // Get one extra to check has_more
        ->order('id desc')
        ->select();

    $has_more = count($list) > $limit;
    if ($has_more) {
        array_pop($list);  // Remove extra item
    }

    $next_cursor = 0;
    if (!empty($list) && $has_more) {
        $next_cursor = end($list)['id'];
    }

    return new Response('成功', 1, [
        'list' => $list,
        'cursor' => $cursor,
        'next_cursor' => $next_cursor,
        'has_more' => $has_more,
        'limit' => $limit
    ]);
}
```

**Request:**
```
GET /api.php/Product/gets?cursor=100&limit=10
```

**Response:**
```json
{
    "status": 1,
    "msg": "成功",
    "data": {
        "list": [...],
        "cursor": 100,
        "next_cursor": 90,
        "has_more": true,
        "limit": 10
    }
}
```

---

## Time-based Pagination

For chronological data:

```php
public function gets(): Response
{
    $last_time = I('get.last_time', 0, 'intval');
    $limit = (int)I('get.limit', 20);

    $where = [];
    if ($last_time > 0) {
        $where['create_time'] = ['lt', $last_time];
    }

    $list = D('Article')
        ->where($where)
        ->limit($limit + 1)
        ->order('create_time desc, id desc')
        ->select();

    $has_more = count($list) > $limit;
    if ($has_more) {
        array_pop($list);
    }

    $last_time = 0;
    if (!empty($list)) {
        $last_time = end($list)['create_time'];
    }

    return new Response('成功', 1, [
        'list' => $list,
        'last_time' => $last_time,
        'has_more' => $has_more
    ]);
}
```

---

## Best Practices

1. **Limit maximum page size** - Prevent abuse with max limit
2. **Use cursor for large datasets** - More efficient than offset
3. **Include total count carefully** - Can be expensive for large tables
4. **Consistent ordering** - Always use deterministic sort

```php
// Always include id in order for consistency
->order('create_time desc, id desc')
```

---

## Related Rules

- [API Response Format](api-response-format.md) - Standard response format
- [API Controllers Reference](../../references/api-controllers.md) - Complete guide

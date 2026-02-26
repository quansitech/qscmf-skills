# API Pagination

Pagination strategies for RESTful API endpoints.

## Offset Pagination

```php
public function index_get()
{
    $page = I('get.page', 1, 'intval');
    $pageSize = min(I('get.page_size', 20, 'intval'), 100);

    $map = ['status' => DBCont::NORMAL_STATUS];
    $model = D('Product');

    $total = $model->where($map)->count();
    $list = $model->where($map)
        ->page($page, $pageSize)
        ->select();

    $this->response([
        'status' => true,
        'data' => $list,
        'meta' => [
            'total' => $total,
            'page' => $page,
            'page_size' => $pageSize,
            'total_pages' => ceil($total / $pageSize),
        ],
    ]);
}
```

## Cursor Pagination

For large datasets:

```php
public function index_get()
{
    $cursor = I('get.cursor', 0, 'intval');
    $limit = min(I('get.limit', 20, 'intval'), 100);

    $map = ['status' => DBCont::NORMAL_STATUS];
    if ($cursor > 0) {
        $map['id'] = ['LT', $cursor];
    }

    $list = D('Product')->where($map)
        ->order('id desc')
        ->limit($limit + 1)
        ->select();

    $hasMore = count($list) > $limit;
    if ($hasMore) {
        array_pop($list);
    }

    $nextCursor = $hasMore ? end($list)['id'] : null;

    $this->response([
        'status' => true,
        'data' => $list,
        'meta' => [
            'cursor' => $nextCursor,
            'has_more' => $hasMore,
        ],
    ]);
}
```

## Pagination Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (offset) |
| `page_size` | int | Items per page |
| `cursor` | int | Last item ID (cursor) |
| `limit` | int | Items per page (cursor) |

---

## Related Documentation

- [API Response Format](api-response-format.md)
- [API Auth JWT](api-auth-jwt.md)

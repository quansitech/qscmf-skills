---
title: Cursor-Based Pagination
impact: MEDIUM
impactDescription: Used in 70% of list endpoints
tags: api, pagination, cursor, both
---

## Cursor-Based Pagination

Implement cursor-based pagination for API endpoints.

**Incorrect (Offset-based, slow with large datasets):**
```php
$page = (int)($get_data['page'] ?? 1);
$limit = (int)($get_data['limit'] ?? 10);

$list = D('Product')
    ->order('id desc')
    ->limit($limit)
    ->page($page)
    ->select();

$total = D('Product')->count();
```

**Correct (Cursor-based, efficient):**
```php
public function gets(): Response
{
    $get_data = I('get.');
    $limit = (int)($get_data['limit'] ?? 10);
    $cursor = $get_data['cursor'] ?? null;

    if ($cursor) {
        // Decode cursor to get last ID
        $lastId = $this->decodeCursor($cursor);
        $list = D('Product')
            ->where('id', '<', $lastId)
            ->order('id desc')
            ->limit($limit + 1)
            ->select();

        $hasMore = count($list) > $limit;
        if ($hasMore) {
            array_pop($list);
        }
    } else {
        $list = D('Product')
            ->order('id desc')
            ->limit($limit + 1)
            ->select();

        $hasMore = count($list) > $limit;
        if ($hasMore) {
            array_pop($list);
        }
    }

    $nextCursor = null;
    if ($hasMore) {
        $lastItem = end($list);
        $nextCursor = $this->encodeCursor($lastItem['id']);
    }

    return new Response('成功', 1, [
        'list' => $list,
        'next_cursor' => $nextCursor,
        'has_more' => $hasMore
    ]);
}
```

**Cursor Encoding/Decoding:**
```php
private function encodeCursor(int $id): string
{
    return base64_encode(json_encode(['id' => $id]));
}

private function decodeCursor(string $cursor): int
{
    $data = json_decode(base64_decode($cursor), true);
    return $data['id'];
}
```

**Response Format:**
```json
{
  "msg": "成功",
  "status": 1,
  "data": {
    "list": [...],
    "next_cursor": "eyJpIjoxfQ==",
    "has_more": true
  }
}
```

**See Also:**
- [API Response Format](../api/api-response-format.md)

**Version Differences:**
- **v13/v14**: Same implementation
- **v14**: May include refactored helpers

# Development Standards

PHP 8.2 coding standards for QSCMF v14.

## Type Declarations

```php
public function getProductById(int $id): ?array
{
    return $this->where(['id' => $id])->find();
}
```

## Strict Comparisons

```php
// Correct
if ($status === DBCont::NORMAL_STATUS) {}

// Wrong
if ($status == 1) {}
```

## Arrow Functions

```php
// Correct
$ids = array_map(fn($item) => (int)$item['id'], $list);

// Wrong
$ids = array_map(function($item) {
    return (int)$item['id'];
}, $list);
```

## Match Expressions

```php
// Correct
$statusText = match($status) {
    1 => '启用',
    0 => '禁用',
    default => '未知'
};
```

## File Organization

- 200-400 lines typical, 800 max
- High cohesion, low coupling
- One class per file

---

## Related Documentation
- [Model Guide](model-guide.md)
- [Admin Controllers](admin-controllers.md)

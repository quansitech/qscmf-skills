# Where Query Reference

ThinkPHP query syntax reference for QSCMF v14.

## Basic Queries

```php
// Equal
$map['status'] = 1;

// Not equal
$map['status'] = ['NEQ', 0];

// Like
$map['name'] = ['like', '%keyword%'];

// IN
$map['id'] = ['IN', [1, 2, 3]];

// NOT IN
$map['status'] = ['NOT IN', [0, 2]];

// Between
$map['price'] = ['BETWEEN', [100, 500]];

// Greater than
$map['create_time'] = ['GT', strtotime('-7 days')];

// Less than
$map['stock'] = ['LT', 10];

// Greater or equal
$map['price'] = ['EGT', 0];

// Less or equal
$map['stock'] = ['ELT', 100];
```

## Complex Queries

```php
// OR condition
$map['_complex'] = [
    'name' => ['like', '%keyword%'],
    'code' => ['like', '%keyword%'],
    '_logic' => 'OR'
];

// Multiple conditions
$map['status'] = 1;
$map['create_time'] = ['EGT', strtotime('-30 days')];
```

---

## Related Documentation
- [Model Guide](model-guide.md)
- [Admin Controllers](admin-controllers.md)

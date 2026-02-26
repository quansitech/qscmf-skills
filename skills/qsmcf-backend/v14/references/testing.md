# Testing

PHPUnit testing guide for QSCMF v14.

## Test Structure

```php
<?php
namespace Tests\Feature;

use Tests\TestCase;
use Gy_Library\DBCont;

class ProductTest extends TestCase
{
    public function test_index_returns_list(): void
    {
        $response = $this->get('/api/product');

        $response->assertStatus(200)
            ->assertJsonStructure(['status', 'data']);
    }
}
```

## Run Tests

```bash
vendor/bin/phpunit
vendor/bin/phpunit lara/tests/Feature/ProductTest.php
```

## Assertions

```php
$response->assertStatus(200);
$response->assertJson(['status' => true]);
$response->assertJsonStructure(['data' => ['id', 'name']]);
$this->assertDatabaseHas('product', ['id' => 1]);
```

---

## Related Documentation
- [TDD First](../rules/test/test-tdd-first.md)
- [Wall Mock](../rules/test/test-wall-mock.md)

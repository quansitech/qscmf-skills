---
title: TDD First (v14)
impact: HIGH
impactDescription: Required for quality code development
tags: test, tdd, v14, phpunit10
---

## TDD First (v14)

Test-Driven Development workflow for QSCMF v14 using PHPUnit 10.

### When to Use This Rule

- Writing new features
- Fixing bugs
- Ensuring code quality

---

## PHPUnit 10 Key Changes

PHPUnit 10 introduces several important changes from PHPUnit 9:

- **Strict type declarations** required on all test methods
- **`@test` annotation deprecated** - Use `test` prefix instead
- **`withConsecutive()` removed** - Use `willReturnCallback()` instead
- **`assertIsArray()` replaced** - Use native PHP type checks
- **No return types on test methods** - Tests should not return values
- **Coverage requires PCOV or Xdebug** - Whitelist configuration removed

---

## TDD Workflow

### Red-Green-Refactor Cycle

```
1. RED    - Write failing test
2. GREEN  - Write minimal code to pass
3. REFACTOR - Improve code while keeping tests green
```

---

## Step 1: Write Test First

```php
// lara/tests/Feature/ProductTest.php

<?php

namespace Lara\Tests\Feature;

use PHPUnit\Framework\TestCase;
use Gy_Library\DBCont;
use Illuminate\Support\Facades\DB;

class ProductTest extends TestCase
{
    public function testCreateProduct(): void
    {
        $data = [
            'product_name' => 'Test Product',
            'price' => 99.99,
            'status' => DBCont::NORMAL_STATUS,
        ];

        $response = $this->post('/api.php/Product/save', $data);

        $response->assertStatus(200)
            ->assertJson(['status' => 1])
            ->assertJsonStructure(['data' => ['id']]);

        // Cleanup
        $result = json_decode($response->getContent(), true);
        if (isset($result['data']['id'])) {
            DB::table('product')->delete($result['data']['id']);
        }
    }
}
```

### Step 2: Run Test (Should Fail)

```bash
vendor/bin/phpunit lara/tests/Feature/ProductTest.php --filter testCreateProduct
# FAILED - Product not found or endpoint doesn't exist
```

### Step 3: Write Minimal Code

```php
// app/Api/Controller/ProductController.php

public function save(): Response
{
    $data = I('post.');
    $id = D('Product')->add($data);

    if ($id) {
        return new Response('创建成功', 1, ['id' => $id]);
    }
    return new Response('创建失败', 0);
}
```

### Step 4: Run Test (Should Pass)

```bash
vendor/bin/phpunit lara/tests/Feature/ProductTest.php --filter testCreateProduct
# OK - Test passes
```

### Step 5: Refactor

```php
public function save(): Response
{
    if (!IS_POST) {
        return new Response('请求方法错误', 0);
    }

    $data = I('post.');

    // Validation
    if (empty($data['product_name'])) {
        return new Response('商品名称不能为空', 0);
    }

    $id = D('Product')->add($data);

    if ($id) {
        return new Response('创建成功', 1, ['id' => $id]);
    }

    return new Response('创建失败: ' . D('Product')->getError(), 0);
}
```

---

## Test Categories

### Unit Tests

Test individual methods in isolation:

```php
public function testModelValidation(): void
{
    $model = D('Product');

    // Test required field
    $result = $model->create(['product_name' => '']);
    $this->assertFalse($result);

    // Test valid data
    $result = $model->create(['product_name' => 'Valid Name']);
    $this->assertIsArray($result);
}
```

### Integration Tests

Test API endpoints:

```php
public function testGetList(): void
{
    $response = $this->get('/api.php/Product/gets');

    $response->assertStatus(200)
        ->assertJson(['status' => 1]);
}
```

### Feature Tests

Test complete user flows:

```php
public function testCompleteOrderFlow(): void
{
    // Create product
    $productResponse = $this->post('/api.php/Product/save', [
        'product_name' => 'Test Product',
        'price' => 100,
    ]);
    $productId = json_decode($productResponse->getContent(), true)['data']['id'];

    // Create order
    $orderResponse = $this->post('/api.php/Order/save', [
        'product_id' => $productId,
        'quantity' => 1,
    ]);

    $orderResponse->assertStatus(200)
        ->assertJson(['status' => 1]);

    // Cleanup
    DB::table('order')->where('product_id', $productId)->delete();
    DB::table('product')->delete($productId);
}
```

---

## PHPUnit 10 Data Providers

PHPUnit 10 requires data providers to be declared differently:

```php
<?php

namespace Lara\Tests\Feature;

use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

class ProductValidationTest extends TestCase
{
    public static function invalidProductDataProvider(): array
    {
        return [
            'empty name' => ['', 100, '商品名称不能为空'],
            'negative price' => ['Valid Name', -10, '价格不能为负数'],
            'zero price' => ['Valid Name', 0, '价格必须大于0'],
        ];
    }

    #[DataProvider('invalidProductDataProvider')]
    public function testCreateProductValidation(string $name, float $price, string $expectedError): void
    {
        $response = $this->post('/api.php/Product/save', [
            'product_name' => $name,
            'price' => $price,
        ]);

        $response->assertStatus(200)
            ->assertJson(['status' => 0, 'info' => $expectedError]);
    }
}
```

---

## PHPUnit 10 Test Attributes

Use PHP 8 attributes instead of annotations:

```php
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\Attributes\Group;
use PHPUnit\Framework\Attributes\Depends;
use PHPUnit\Framework\Attributes\Ticket;

class ProductTest extends TestCase
{
    #[Test]
    #[Group('product')]
    #[Ticket('PROD-123')]
    public function productCanBeCreated(): void
    {
        // Test implementation
    }

    #[Depends('productCanBeCreated')]
    public function testProductCanBeUpdated(int $productId): void
    {
        // This test receives $productId from the dependent test
    }
}
```

---

## Best Practices

1. **One assertion per test** - Keep tests focused
2. **Descriptive test names** - `testCreateProductWithEmptyNameReturnsError`
3. **Use data providers with attributes** - PHPUnit 10 style `#[DataProvider()]`
4. **Clean up test data** - Always remove created records
5. **Test edge cases** - Empty values, boundaries, errors
6. **No return types on test methods** - PHPUnit 10 convention
7. **Use strict types** - Add `declare(strict_types=1);` at file top

---

## Related Rules

- [Test Wall Mock](test-wall-mock.md) - Mocking external services
- [Test Transaction](test-transaction.md) - Transaction testing
- [Testing Reference](../../references/testing.md) - Complete testing guide

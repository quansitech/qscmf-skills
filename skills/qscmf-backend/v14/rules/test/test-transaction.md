---
title: Transaction Testing (v14)
impact: HIGH
impactDescription: Required for testing database operations
tags: test, transaction, v14, phpunit10
---

## Transaction Testing (v14)

Testing database transactions for data integrity in QSCMF v14 using PHPUnit 10.

### When to Use This Rule

- Testing operations that modify multiple tables
- Verifying rollback behavior
- Ensuring data consistency

---

## PHPUnit 10 Transaction Testing Changes

Key differences from PHPUnit 9:

- **`tearDown(): void`** - Must have void return type
- **No return types on test methods** - Tests should not return values
- **Strict type checking** - Type declarations enforced
- **Better exception assertions** - `expectExceptionMessageMatches()`

---

## Basic Transaction Test

```php
<?php

declare(strict_types=1);

namespace Lara\Tests\Feature;

use PHPUnit\Framework\TestCase;
use Gy_Library\DBCont;
use Illuminate\Support\Facades\DB;

class OrderTransactionTest extends TestCase
{
    public function testTransactionCommit(): void
    {
        $orderData = [
            'order_no' => 'ORD' . time(),
            'total_amount' => 100.00,
            'status' => DBCont::NORMAL_STATUS,
        ];

        $orderId = null;

        D('Order')->startTrans();
        try {
            // Create order
            $orderId = D('Order')->add($orderData);
            $this->assertGreaterThan(0, $orderId);

            // Create order items
            $itemId = D('OrderItem')->add([
                'order_id' => $orderId,
                'product_id' => 1,
                'quantity' => 2,
                'price' => 50.00,
            ]);
            $this->assertGreaterThan(0, $itemId);

            D('Order')->commit();

            // Verify data
            $this->assertDatabaseHas('order', ['id' => $orderId]);
            $this->assertDatabaseHas('order_item', ['order_id' => $orderId]);

        } catch (\Exception $e) {
            D('Order')->rollback();
            $this->fail('Transaction failed: ' . $e->getMessage());
        } finally {
            // Cleanup
            if ($orderId !== null) {
                DB::table('order_item')->where('order_id', $orderId)->delete();
                DB::table('order')->delete($orderId);
            }
        }
    }
}
```

---

## Testing Rollback

```php
public function testTransactionRollback(): void
{
    $initialCount = D('Order')->count();

    D('Order')->startTrans();
    try {
        // Create order
        $orderId = D('Order')->add([
            'order_no' => 'ORD' . time(),
            'total_amount' => 100.00,
        ]);

        // Simulate error
        throw new \Exception('Simulated error');

        D('Order')->commit();
    } catch (\Exception $e) {
        D('Order')->rollback();
    }

    // Verify no data was committed
    $finalCount = D('Order')->count();
    $this->assertEquals($initialCount, $finalCount);
}
```

---

## Using Laravel Transaction Helper

```php
public function testWithLaravelTransaction(): void
{
    $orderId = null;

    DB::transaction(function () use (&$orderId): void {
        $orderId = DB::table('order')->insertGetId([
            'order_no' => 'ORD' . time(),
            'total_amount' => 100.00,
            'status' => DBCont::NORMAL_STATUS,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        DB::table('order_item')->insert([
            'order_id' => $orderId,
            'product_id' => 1,
            'quantity' => 1,
            'price' => 100.00,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
    });

    // Verify both records exist
    $this->assertDatabaseHas('order', ['id' => $orderId]);
    $this->assertDatabaseHas('order_item', ['order_id' => $orderId]);

    // Cleanup
    DB::table('order_item')->where('order_id', $orderId)->delete();
    DB::table('order')->delete($orderId);
}
```

---

## Testing Nested Transactions

```php
public function testNestedTransaction(): void
{
    $orderId = null;

    D('Order')->startTrans();
    try {
        // Outer transaction
        $orderId = D('Order')->add([
            'order_no' => 'ORD001',
            'total_amount' => 100.00,
        ]);

        // Inner operation
        D('Order')->startTrans();
        try {
            D('OrderItem')->add([
                'order_id' => $orderId,
                'product_id' => 1,
                'quantity' => 1,
            ]);
            D('Order')->commit();  // Inner commit
        } catch (\Exception $e) {
            D('Order')->rollback();
            throw $e;
        }

        D('Order')->commit();  // Outer commit

        $this->assertDatabaseHas('order', ['id' => $orderId]);

    } catch (\Exception $e) {
        D('Order')->rollback();
        $this->fail($e->getMessage());
    } finally {
        if ($orderId !== null) {
            DB::table('order_item')->where('order_id', $orderId)->delete();
            DB::table('order')->where('id', $orderId)->delete();
        }
    }
}
```

---

## PHPUnit 10 Cleanup Pattern

In PHPUnit 10, the tearDown method must have void return type:

```php
<?php

declare(strict_types=1);

namespace Lara\Tests\Feature;

use PHPUnit\Framework\TestCase;
use Illuminate\Support\Facades\DB;

abstract class TransactionTestCase extends TestCase
{
    protected array $createdIds = [];

    protected function tearDown(): void
    {
        // Clean up all created records
        foreach ($this->createdIds as $table => $ids) {
            if (!empty($ids)) {
                DB::table($table)->whereIn('id', $ids)->delete();
            }
        }

        parent::tearDown();
    }

    protected function trackCreatedId(string $table, int $id): void
    {
        $this->createdIds[$table][] = $id;
    }
}
```

### Using the Cleanup Pattern

```php
class OrderTest extends TransactionTestCase
{
    public function testWithAutoCleanup(): void
    {
        $orderId = DB::table('order')->insertGetId([
            'order_no' => 'ORD001',
            'total_amount' => 100.00,
            'status' => DBCont::NORMAL_STATUS,
        ]);
        $this->trackCreatedId('order', $orderId);

        $itemId = DB::table('order_item')->insertGetId([
            'order_id' => $orderId,
            'product_id' => 1,
            'quantity' => 1,
        ]);
        $this->trackCreatedId('order_item', $itemId);

        // Test assertions...
        $this->assertDatabaseHas('order', ['id' => $orderId]);

        // Cleanup happens automatically in tearDown
    }
}
```

---

## Testing Transaction Deadlocks

```php
public function testDeadlockHandling(): void
{
    $this->expectException(\Exception::class);

    // Simulate deadlock scenario
    DB::transaction(function (): void {
        // Update order
        DB::table('order')->where('id', 1)->update(['status' => 2]);

        // This would cause a deadlock in concurrent scenario
        throw new \Exception('Deadlock detected');
    });
}
```

---

## PHPUnit 10 Exception Assertions

```php
use PHPUnit\Framework\Attributes\TestDox;

class TransactionExceptionTest extends TestCase
{
    #[TestDox('Transaction throws exception on invalid data')]
    public function testTransactionThrowsOnInvalidData(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessageMatches('/invalid.*data/i');

        D('Order')->startTrans();
        try {
            D('Order')->add([
                'order_no' => '',  // Invalid empty order_no
                'total_amount' => -100,  // Invalid negative amount
            ]);
            D('Order')->commit();
        } catch (\Exception $e) {
            D('Order')->rollback();
            throw $e;
        }
    }
}
```

---

## Database Assertions

PHPUnit 10 with Laravel provides database assertions:

```php
public function testDatabaseAssertions(): void
{
    $orderId = DB::table('order')->insertGetId([
        'order_no' => 'ORD001',
        'total_amount' => 100.00,
        'status' => DBCont::NORMAL_STATUS,
    ]);

    // Assert record exists
    $this->assertDatabaseHas('order', [
        'id' => $orderId,
        'order_no' => 'ORD001',
    ]);

    // Assert record does not exist
    $this->assertDatabaseMissing('order', [
        'order_no' => 'NONEXISTENT',
    ]);

    // Assert count
    $this->assertDatabaseCount('order', 1);

    // Cleanup
    DB::table('order')->delete($orderId);
}
```

---

## Best Practices

1. **Always rollback on failure** - Use try/catch/finally
2. **Clean up test data** - Don't leave records in database
3. **Test rollback scenarios** - Verify error handling
4. **Use database assertions** - assertDatabaseHas, assertDatabaseMissing
5. **Avoid shared state** - Each test should be independent
6. **Use void return type** - On tearDown() and setup methods
7. **Add strict_types** - At the top of all test files
8. **Track created IDs** - For reliable cleanup

---

## Related Rules

- [TDD First](test-tdd-first.md) - Test-driven development
- [Test Wall Mock](test-wall-mock.md) - Mocking external services
- [Testing Reference](../../references/testing.md) - Complete testing guide

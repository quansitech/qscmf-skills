---
title: Transaction Testing (v13)
impact: HIGH
impactDescription: Required for testing database operations
tags: test, transaction, v13
---

## Transaction Testing (v13)

Testing database transactions for data integrity in QSCMF v13.

### When to Use This Rule

- Testing operations that modify multiple tables
- Verifying rollback behavior
- Ensuring data consistency

---

## Basic Transaction Test

```php
public function testTransactionCommit(): void
{
    $orderData = [
        'order_no' => 'ORD' . time(),
        'total_amount' => 100.00,
        'status' => DBCont::NORMAL_STATUS,
    ];

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
        DB::table('order_item')->where('order_id', $orderId)->delete();
        DB::table('order')->delete($orderId);
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

    DB::transaction(function () use (&$orderId) {
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
        DB::table('order_item')->where('order_id', $orderId ?? 0)->delete();
        DB::table('order')->where('id', $orderId ?? 0)->delete();
    }
}
```

---

## Cleanup Pattern

```php
protected $createdIds = [];

protected function tearDown(): void
{
    // Clean up all created records
    foreach ($this->createdIds as $table => $ids) {
        DB::table($table)->whereIn('id', $ids)->delete();
    }

    parent::tearDown();
}

public function testWithAutoCleanup(): void
{
    $orderId = DB::table('order')->insertGetId([...]);
    $this->createdIds['order'][] = $orderId;

    $itemId = DB::table('order_item')->insertGetId([...]);
    $this->createdIds['order_item'][] = $itemId;

    // Test assertions...
    // Cleanup happens automatically in tearDown
}
```

---

## Best Practices

1. **Always rollback on failure** - Use try/catch/finally
2. **Clean up test data** - Don't leave records in database
3. **Test rollback scenarios** - Verify error handling
4. **Use database assertions** - assertDatabaseHas, assertDatabaseMissing
5. **Avoid shared state** - Each test should be independent

---

## Related Rules

- [TDD First](test-tdd-first.md) - Test-driven development
- [Test Wall Mock](test-wall-mock.md) - Mocking external services
- [Testing Reference](../../references/testing.md) - Complete testing guide

---
title: 事务测试规则
impact: HIGH
impactDescription: 确保数据一致性，避免脏数据
tags: test, transaction, both
---

## 事务测试规则

**影响级别：HIGH（确保数据一致性）**

测试数据库事务的正确性，保证 ACID 特性。

### 何时使用此规则

- 编写涉及多表操作的业务逻辑测试
- 测试事务回滚场景
- 验证并发操作的数据一致性

---

## 事务测试原则

### 1. 每个测试独立事务

```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;
use Illuminate\Support\Facades\DB;

class OrderTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        // 每个测试开始事务
        DB::beginTransaction();
    }

    protected function tearDown(): void
    {
        // 每个测试结束回滚
        DB::rollBack();
        parent::tearDown();
    }

    public function testCreateOrder(): void
    {
        // 测试代码在事务中执行
        // 测试结束自动回滚，不影响数据库
    }
}
```

### 2. 显式事务测试

测试事务边界内的业务逻辑：

```php
public function testOrderWithItemsTransaction(): void
{
    $this->runTp(function () {
        // 开始事务
        D()->startTrans();

        try {
            // 创建订单
            $orderId = D('Order')->add([
                'order_no' => 'ORD001',
                'total_amount' => 100.00,
                'status' => 0,
            ]);

            $this->assertGreaterThan(0, $orderId);

            // 创建订单项
            $itemId = D('OrderItem')->add([
                'order_id' => $orderId,
                'product_id' => 1,
                'quantity' => 2,
                'price' => 50.00,
            ]);

            $this->assertGreaterThan(0, $itemId);

            // 提交事务
            D()->commit();

            // 验证数据
            $order = D('Order')->find($orderId);
            $this->assertNotNull($order);
            $this->assertEquals('ORD001', $order['order_no']);

        } catch (\Exception $e) {
            D()->rollback();
            $this->fail('事务执行失败: ' . $e->getMessage());
        }
    });
}
```

---

## 事务回滚测试

### 回滚场景测试

```php
public function testOrderRollbackOnError(): void
{
    $initialCount = $this->runTp(fn() => D('Order')->count());

    $this->runTp(function () {
        D()->startTrans();

        try {
            // 创建订单
            $orderId = D('Order')->add([
                'order_no' => 'ORD002',
                'total_amount' => 100.00,
            ]);

            // 模拟错误：库存不足
            $stock = D('Product')->where(['id' => 1])->getField('stock');
            if ($stock < 100) {
                throw new \Exception('库存不足');
            }

            D()->commit();

        } catch (\Exception $e) {
            D()->rollback();
            // 重新抛出以便测试捕获
            throw $e;
        }
    });

    // 验证回滚：订单数量未增加
    $finalCount = $this->runTp(fn() => D('Order')->count());
    $this->assertEquals($initialCount, $finalCount);
}
```

### 部分失败测试

```php
public function testPartialFailureRollback(): void
{
    $this->runTp(function () {
        D()->startTrans();

        $results = [];

        try {
            // 操作 1：成功
            $results[] = D('Log')->add([
                'action' => 'test1',
                'created_at' => date('Y-m-d H:i:s'),
            ]);

            // 操作 2：成功
            $results[] = D('Log')->add([
                'action' => 'test2',
                'created_at' => date('Y-m-d H:i:s'),
            ]);

            // 操作 3：故意失败
            if (true) {  // 模拟失败条件
                throw new \Exception('操作3失败');
            }

            // 操作 4：不会执行
            $results[] = D('Log')->add([
                'action' => 'test4',
                'created_at' => date('Y-m-d H:i:s'),
            ]);

            D()->commit();

        } catch (\Exception $e) {
            D()->rollback();
        }

        // 验证：所有操作都未生效
        $logCount = D('Log')->where(['action' => ['in', ['test1', 'test2', 'test4']]])->count();
        $this->assertEquals(0, $logCount);
    });
}
```

---

## 并发事务测试

### 乐观锁测试

```php
public function testOptimisticLock(): void
{
    $this->runTp(function () {
        // 创建测试数据
        $id = D('Product')->add([
            'name' => 'Test Product',
            'stock' => 100,
            'version' => 1,  // 乐观锁版本号
        ]);

        // 模拟两个并发请求读取相同数据
        $product1 = D('Product')->find($id);
        $product2 = D('Product')->find($id);

        // 第一个请求更新成功
        $result1 = D('Product')->where([
            'id' => $id,
            'version' => $product1['version'],
        ])->save([
            'stock' => $product1['stock'] - 10,
            'version' => $product1['version'] + 1,
        ]);

        $this->assertTrue($result1 !== false);

        // 第二个请求更新失败（版本号不匹配）
        $result2 = D('Product')->where([
            'id' => $id,
            'version' => $product2['version'],  // 旧版本号
        ])->save([
            'stock' => $product2['stock'] - 20,
            'version' => $product2['version'] + 1,
        ]);

        $this->assertEquals(0, $result2);  // 影响行数为 0

        // 验证最终数据
        $final = D('Product')->find($id);
        $this->assertEquals(90, $final['stock']);
        $this->assertEquals(2, $final['version']);
    });
}
```

### 悲观锁测试

```php
public function testPessimisticLockWithRedis(): void
{
    $lockKey = 'product_stock_lock_1';

    $this->runTp(function () use ($lockKey) {
        // 获取分布式锁
        $lock = new \Qscmf\Lib\Redis\RedisLock($lockKey, 10);

        if (!$lock->acquire()) {
            $this->fail('无法获取锁');
        }

        try {
            // 读取库存
            $product = D('Product')->find(1);
            $this->assertNotNull($product);

            // 检查库存
            if ($product['stock'] < 10) {
                $this->fail('库存不足');
            }

            // 扣减库存
            D('Product')->where(['id' => 1])->setDec('stock', 10);

            // 验证
            $updated = D('Product')->find(1);
            $this->assertEquals($product['stock'] - 10, $updated['stock']);

        } finally {
            $lock->release();
        }
    });
}
```

---

## 嵌套事务测试

### Laravel 嵌套事务

```php
public function testNestedTransaction(): void
{
    // 外层事务
    DB::beginTransaction();

    try {
        // 操作 1
        DB::table('qs_log')->insert(['action' => 'outer']);

        // 内层事务（使用 savepoint）
        DB::beginTransaction();

        try {
            // 操作 2
            DB::table('qs_log')->insert(['action' => 'inner']);

            DB::commit();  // 释放 savepoint

        } catch (\Exception $e) {
            DB::rollBack(2);  // 回滚到 savepoint
        }

        DB::commit();  // 提交外层事务

    } catch (\Exception $e) {
        DB::rollBack();
        $this->fail('事务失败');
    }

    // 验证
    $logs = DB::table('qs_log')->where('action', 'in', ['outer', 'inner'])->get();
    $this->assertCount(2, $logs);
}
```

---

## 事务测试最佳实践

### 1. 使用 TestCase 基类提供的事务支持

```php
// lara/tests/TestCase.php
namespace Lara\Tests;

use Illuminate\Support\Facades\DB;

abstract class TestCase extends \Illuminate\Foundation\Testing\TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        DB::beginTransaction();
    }

    protected function tearDown(): void
    {
        DB::rollBack();
        parent::tearDown();
    }

    /**
     * 在 ThinkPHP 上下文中运行代码
     */
    protected function runTp(callable $callback)
    {
        return app()->make(\App\Services\TpRunner::class)->run($callback);
    }
}
```

### 2. 数据工厂与事务配合

```php
public function testWithFactory(): void
{
    // 工厂创建的数据在事务中
    $product = $this->createProduct(['stock' => 100]);

    // 测试逻辑
    $result = D('Product')->deductStock($product['id'], 10);

    $this->assertTrue($result);
    $this->assertEquals(90, D('Product')->getFieldById($product['id'], 'stock'));

    // tearDown 自动回滚，数据不会残留
}

private function createProduct(array $attrs = []): array
{
    $defaults = [
        'name' => 'Test Product',
        'stock' => 100,
        'status' => 1,
    ];

    $data = array_merge($defaults, $attrs);
    $id = D('Product')->add($data);

    return D('Product')->find($id);
}
```

### 3. 验证事务隔离级别

```php
public function testTransactionIsolation(): void
{
    // 在事务内创建数据
    DB::beginTransaction();

    DB::table('qs_product')->insert([
        'name' => 'Isolation Test',
        'stock' => 100,
    ]);

    // 事务未提交，新连接应看不到数据
    $countInTransaction = DB::table('qs_product')
        ->where('name', 'Isolation Test')
        ->count();

    $this->assertEquals(1, $countInTransaction);

    DB::rollBack();

    // 回滚后数据消失
    $countAfterRollback = DB::table('qs_product')
        ->where('name', 'Isolation Test')
        ->count();

    $this->assertEquals(0, $countAfterRollback);
}
```

---

## 事务测试检查清单

### 基本检查

- [ ] 测试使用 setUp/tearDown 自动事务
- [ ] 显式事务有 commit 和 rollback
- [ ] 异常情况正确回滚
- [ ] 测试后数据库状态干净

### 边界检查

- [ ] 空值/NULL 处理正确
- [ ] 外键约束违规回滚
- [ ] 唯一键冲突回滚
- [ ] 超时情况处理

### 并发检查

- [ ] 乐观锁版本号正确更新
- [ ] 悲观锁获取/释放正确
- [ ] 死锁检测和处理

---

## 相关文档

- [TDD 开发](test-tdd-first.md) - 测试驱动开发
- [Wall Mock](test-wall-mock.md) - Mock 外部依赖
- [Redis Lock](../pattern/pattern-redis-lock.md) - 分布式锁
- [开发规范](../../references/development-standards.md) - 编码规范

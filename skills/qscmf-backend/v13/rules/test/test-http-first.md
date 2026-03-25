---
title: HTTP First Testing (v13)
impact: HIGH
impactDescription: Improves test performance by ~500ms per test
tags: test, http, performance, v13
---

## HTTP First Testing (v13)

**CRITICAL**: HTTP 集成测试优先，runTp() 仅在无法使用 HTTP 时使用。

## Performance Comparison

| Method | Time | Usage |
|--------|------|-------|
| HTTP + Mock | ~50ms | ✅ Preferred |
| DB facade | ~10ms | ✅ For data setup/verify |
| runTp() (fork + pipe) | ~500ms | ⚠️ Last resort |

## Golden Rule

```
准备数据 → DB::table()
设置 Mock → app()->instance()
执行测试 → HTTP GET/POST
验证结果 → DB::table()
runTp()   → 仅用于 ThinkPHP 配置等无法用 HTTP 的场景
```

---

## HTTP Integration Test (Preferred)

### Pattern

```php
/** @test */
public function testUpdatesStatusWithMock(): void
{
    // 1. 准备数据 - DB facade (不用 runTp)
    $waybillId = DB::table('qs_jd_waybill')->insertGetId([
        'order_id' => 'JD' . time(),
        'order_status' => 0,
    ]);

    // 2. 设置 Mock - app()->instance() (不用 runTp)
    $mock = $this->createMock(\Common\Lib\Wall\JdClientWall::class);
    $mock->method('execute')->willReturn([
        'success' => true,
        'orderStatus' => 2,
    ]);
    app()->instance(\Common\Lib\Wall\JdClientWall::class, $mock);

    // 3. 执行 - HTTP GET (不用 runTp)
    $response = $this->get('/JDInfoRefresh/info');

    // 4. 验证结果 - DB facade (不用 runTp)
    $result = DB::table('qs_jd_waybill')->where('id', $waybillId)->first();
    $this->assertEquals(2, $result->order_status);
}
```

### Wall Class Mock Pattern

```php
/** @test */
public function testJdOrderSync(): void
{
    // 准备数据
    $orderId = 'JD' . time();
    DB::table('qs_jd_order')->insertGetId([
        'order_id' => $orderId,
        'status' => 0,
    ]);

    // Mock JdClientWall
    $mock = $this->createMock(\Common\Lib\Wall\JdClientWall::class);
    $mock->method('execute')->willReturn($this->mockJdResponse());
    app()->instance(\Common\Lib\Wall\JdClientWall::class, $mock);

    // 执行 HTTP 请求
    $response = $this->post('/api.php/JdOrder/sync', ['order_id' => $orderId]);

    // 验证
    $response->assertStatus(200)->assertJson(['status' => 1]);
    $this->assertDatabaseHas('qs_jd_order', ['order_id' => $orderId, 'status' => 1]);
}

private function mockJdResponse(): array
{
    return [
        'code' => 200,
        'orderInfo' => [
            'orderId' => $orderId,
            'orderState' => 1,
        ],
    ];
}
```

---

## CLI Testing Pattern

### CLI Entry Point

CLI 入口文件在 `app/` 目录，不是 `www/index.php`：

```
app/jdInfoRefresh  → JDInfoRefreshController
app/queue          → QueueController
app/batchExport    → BatchExportController
```

### Test Pattern

```php
/** @test */
public function testCliUpdatesStatus(): void
{
    // 1. 准备数据 - DB facade (不用 runTp)
    $waybillId = DB::table('qs_jd_waybill')->insertGetId([
        'order_id' => 'JD' . time(),
        'order_status' => 0,
    ]);

    // 2. 设置配置 - runTp (仅此处需要)
    $this->runTp(fn() => C('CANCEL_JD_WAYBILL', true));

    // 3. 执行 CLI
    $this->cli('app/jdInfoRefresh', 'info');

    // 4. 验证结果 - DB facade (不用 runTp)
    $result = DB::table('qs_jd_waybill')->where('id', $waybillId)->first();
    $this->assertEquals(1, $result->order_status);
}
```

### CLI with Mock

```php
/** @test */
public function testCliWithMockedExternalService(): void
{
    // 准备数据
    DB::table('qs_task')->insertGetId(['status' => 0]);

    // 设置 Mock (在 runTp 外面)
    $mock = $this->createMock(\Common\Lib\Wall\ExternalApi::class);
    $mock->method('call')->willReturn(['success' => true]);
    app()->instance(\Common\Lib\Wall\ExternalApi::class, $mock);

    // 设置配置
    $this->runTp(fn() => C('API_TIMEOUT', 30));

    // 执行 CLI
    $this->cli('app/queue', 'process');

    // 验证
    $this->assertDatabaseHas('qs_task', ['status' => 1]);
}
```

---

## When to Use runTp()

| Scenario | Use runTp? | Alternative |
|----------|------------|-------------|
| `DB::table()->insert()` | ❌ No | Laravel facade (fast) |
| `DB::table()->first()` | ❌ No | Laravel facade (fast) |
| HTTP GET/POST | ❌ No | Laravel HTTP tests (fast) |
| `app()->instance()` Mock | ❌ No | Laravel service container |
| `C('config_key', value)` | ✅ Yes | No alternative |
| `D('Model')->find()` | ⚠️ Only if HTTP not possible | Prefer HTTP test |
| ThinkPHP constants | ✅ Yes | No alternative |

---

## Common Mistakes

### ❌ Overusing runTp()

```php
// BAD - Everything in runTp (slow, ~500ms)
public function testBad(): void
{
    $result = $this->runTp(function () {
        DB::table('qs_product')->insert([...]);  // Not needed
        $response = $this->post('/api.php/Product/save', [...]);  // Not needed
        return DB::table('qs_product')->first();  // Not needed
    });
}
```

### ✅ Correct Approach

```php
// GOOD - Direct usage, ~50ms
public function testGood(): void
{
    // Setup - DB facade
    $id = DB::table('qs_product')->insertGetId([...]);

    // Execute - HTTP
    $response = $this->post('/api.php/Product/save', [...]);

    // Verify - DB facade
    $result = DB::table('qs_product')->where('id', $id)->first();
}
```

---

## Related Rules

- [runTp Wrapper](test-runtp-wrapper.md) - When runTp is necessary
- [Test TDD First](test-tdd-first.md) - Test-driven development
- [Testing Reference](../../references/testing.md) - Complete testing guide

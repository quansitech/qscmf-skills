---
title: runTp Wrapper (v13)
impact: CRITICAL
impactDescription: Tests using D() directly will fail due to ThinkPHP not being initialized
tags: test, runtp, thinkphp, v13
---

## runTp Wrapper (v13)

**CRITICAL**: In `lara/tests/`, never use `D()` function directly. Always wrap ThinkPHP logic with `runTp()`.

> **⚠️ IMPORTANT**: runTp() has ~500ms overhead per call. **HTTP tests are preferred**. See [HTTP First Testing](test-http-first.md) for the recommended testing pattern.

## Why This Matters

The `lara/` folder uses Laravel's testing infrastructure. ThinkPHP is not fully initialized in this context, so:

```php
// ❌ WRONG - Will fail with "Undefined constant EXT"
public function testModelMethod(): void
{
    $result = D('Product')->add(['name' => 'test']);
    $this->assertGreaterThan(0, $result);
}

// ✅ CORRECT - Works because runTp initializes ThinkPHP
public function testModelMethod(): void
{
    $result = $this->runTp(function () {
        return D('Product')->add(['name' => 'test']);
    });
    $this->assertGreaterThan(0, $result);
}
```

## The runTp Helper

### Definition (in TestCase)

```php
/**
 * 在 ThinkPHP 上下文中运行代码
 */
protected function runTp(callable $callback)
{
    // 初始化 ThinkPHP 环境
    $this->initThinkPHP();

    try {
        return $callback();
    } finally {
        // 清理 ThinkPHP 状态
    }
}
```

### When to Use runTp

| Scenario | Use runTp? | Alternative |
|----------|------------|-------------|
| `D('Model')->...` | ✅ Yes | - |
| `M('Table')->...` | ✅ Yes | - |
| `C('config_key')` | ✅ Yes | - |
| `U('action')` | ✅ Yes | - |
| `DB::table('...')` | ❌ No | Laravel facade, works directly |
| `$this->post('/api/...')` | ❌ No | HTTP request, works directly |
| Pure PHP logic | ❌ No | No ThinkPHP dependency |

## Common Patterns

### Model CRUD Operations

```php
public function testModelCreate(): void
{
    $id = $this->runTp(function () {
        return D('Product')->createAdd([
            'name' => 'Test Product',
            'status' => DBCont::NORMAL_STATUS,
        ]);
    });

    $this->assertGreaterThan(0, $id);
}
```

### Model Validation

```php
public function testModelValidation(): void
{
    $result = $this->runTp(function () {
        return D('Product')->createAdd([
            // Missing required field 'name'
            'status' => DBCont::NORMAL_STATUS,
        ]);
    });

    $this->assertFalse($result);

    $error = $this->runTp(fn() => D('Product')->getError());
    $this->assertStringContainsString('名称', $error);
}
```

### Query with ThinkPHP ORM

```php
public function testModelQuery(): void
{
    // Create test data first
    $id = $this->runTp(function () {
        return D('Product')->createAdd([
            'name' => 'Query Test',
            'status' => DBCont::NORMAL_STATUS,
        ]);
    });

    // Query using ThinkPHP ORM
    $product = $this->runTp(fn() => D('Product')->find($id));

    $this->assertNotNull($product);
    $this->assertEquals('Query Test', $product['name']);
}
```

### Multiple Operations

```php
public function testModelUpdate(): void
{
    // Create
    $id = $this->runTp(function () {
        return D('Product')->createAdd([
            'name' => 'Original',
            'status' => DBCont::NORMAL_STATUS,
        ]);
    });

    // Update
    $result = $this->runTp(function () use ($id) {
        return D('Product')->where(['id' => $id])->save([
            'name' => 'Updated',
        ]);
    });

    $this->assertNotFalse($result);

    // Verify
    $product = $this->runTp(fn() => D('Product')->find($id));
    $this->assertEquals('Updated', $product['name']);
}
```

## Mixed Approach (Best Practice)

For comprehensive testing, combine Laravel DB facade with runTp:

```php
public function testCompleteFlow(): void
{
    // Use Laravel DB for setup (faster, no ThinkPHP overhead)
    $id = DB::table('qs_product')->insertGetId([
        'name' => 'Test Product',
        'status' => 1,
        'create_date' => now(),
    ]);

    // Use runTp for ThinkPHP Model logic
    $result = $this->runTp(function () use ($id) {
        return D('Product')->createSave([
            'id' => $id,
            'name' => 'Updated via Model',
        ]);
    });

    $this->assertNotFalse($result);

    // Use Laravel DB for verification
    $this->assertDatabaseHas('qs_product', [
        'id' => $id,
        'name' => 'Updated via Model',
    ]);
}
```

## Error Messages

If you see these errors, you're missing runTp:

| Error | Cause |
|-------|-------|
| `Undefined constant "EXT"` | ThinkPHP not initialized |
| `Undefined constant "APP_PATH"` | ThinkPHP not initialized |
| `Class 'D' not found` | ThinkPHP not initialized |
| `Call to a member function where() on null` | D() returned null |

## Related Rules

- [Test TDD First](test-tdd-first.md) - Test-driven development
- [Test Transaction](test-transaction.md) - Database transaction testing
- [Testing Reference](../../references/testing.md) - Complete testing guide

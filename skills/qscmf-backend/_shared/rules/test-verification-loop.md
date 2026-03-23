---
title: Test Verification Loop
impact: CRITICAL
impactDescription: Tests without verification are useless - AI often claims success without running
tags: test, verification, loop, tdd
---

## Test Verification Loop (CRITICAL)

> **铁律**：写测试后必须运行验证，否则等于没写。AI 经常声称测试通过，但实际从未运行。

---

## 必须执行的步骤

### 1. 写完测试后，必须运行

```bash
# 定义命令（关闭 xdebug 加速）
PHPUNIT="php -d display_errors=on -d xdebug.mode=off -d xdebug.start_with_request=0 vendor/bin/phpunit"

# 运行单个测试文件
$PHPUNIT lara/tests/Feature/XxxTest.php

# 运行单个测试方法
$PHPUNIT --filter "testMethodName" lara/tests/Feature/XxxTest.php
```

### 2. 必须看到明确的成功输出

**成功的标志**：
```
OK (1 test, 3 assertions)
```
或
```
Tests: 1, Assertions: 3, Time: 0.05s, Memory: 12.00 MB
```

### 3. 失败时必须修复

**失败的标志**：
```
FAILURES!
Tests: 1, Assertions: 1, Failures: 1.
```

**处理流程**：
1. 读取错误信息
2. 修复代码或测试
3. 重新运行测试
4. 确认看到 `OK`

---

## 禁止行为

| 禁止 | 原因 |
|------|------|
| ❌ 只写测试不运行 | 等于没写 |
| ❌ 假设测试通过 | AI 经常误判 |
| ❌ 看到错误就跳过 | 必须修复 |
| ❌ 用宽泛断言作为唯一验证 | 容易误判成功 |

---

## 正确的断言模式

### 精确断言（推荐）

```php
// ✅ JSON 响应 - 解析后精确断言
$json = json_decode($response, true);
$this->assertEquals(1, $json['status']);
$this->assertArrayHasKey('id', $json['data']);
$this->assertEquals('Expected Name', $json['data']['name']);

// ✅ 数据库验证
$this->assertDatabaseHas('qs_product', [
    'id' => $productId,
    'status' => DBCont::NORMAL_STATUS,
]);

// ✅ 精确匹配
$this->assertEquals($expected, $actual);

// ✅ 类型断言
$this->assertIsInt($id);
$this->assertIsArray($result);
```

### 宽泛断言（谨慎使用）

```php
// ⚠️ 可以用，但不能作为唯一断言
$this->assertTrue(Str::contains($response, '成功'));

// ❌ 危险 - 任何包含"成功"的响应都会通过
// 例如："操作失败成功回滚" 也会匹配
```

### 组合断言（最佳实践）

```php
public function testCreateProduct(): void
{
    $response = $this->post('/api.php/Product/save', [
        'product_name' => 'Test Product',
        'price' => 99.99,
    ]);

    // 1. 先检查响应格式
    $json = json_decode($response, true);
    $this->assertNotNull($json, 'Response should be valid JSON');
    $this->assertEquals(1, $json['status'], 'Status should be 1 (success)');

    // 2. 再检查返回数据
    $this->assertArrayHasKey('id', $json['data']);
    $productId = $json['data']['id'];
    $this->assertGreaterThan(0, $productId);

    // 3. 最后验证数据库
    $this->assertDatabaseHas('qs_product', [
        'id' => $productId,
        'product_name' => 'Test Product',
    ]);
}
```

---

## PHPUnit 输出解读

### 成功输出

```
PHPUnit 9.6.0 by Sebastian Bergmann and contributors.

.                                                                   1 / 1 (100%)

Time: 00:00.050, Memory: 12.00 MB

OK (1 test, 3 assertions)
```

**关键标志**：`OK (X tests, Y assertions)`

### 失败输出

```
PHPUnit 9.6.0 by Sebastian Bergmann and contributors.

F                                                                   1 / 1 (100%)

Time: 00:00.050, Memory: 12.00 MB

There was 1 failure:

1) Lara\Tests\Feature\ProductTest::testCreateProduct
Failed asserting that 0 matches expected 1.

/var/www/project/lara/tests/Feature/ProductTest.php:25

FAILURES!
Tests: 1, Assertions: 1, Failures: 1.
```

**关键标志**：`FAILURES!` 或 `ERRORS!`

### 错误输出（语法错误等）

```
PHPUnit 9.6.0 by Sebastian Bergmann and contributors.

E                                                                   1 / 1 (100%)

There was 1 error:

1) Lara\Tests\Feature\ProductTest::testCreateProduct
Error: Class 'App\Service\NonExistentClass' not found
```

**关键标志**：`There was 1 error:` 或 `There were X errors:`

---

## 验证清单

在声称"测试通过"之前，确认：

- [ ] 实际运行了 `vendor/bin/phpunit` 命令
- [ ] 看到了 `OK` 或 `Tests: X, Assertions: Y` 输出
- [ ] 没有看到 `FAILURES!` 或 `ERRORS!`
- [ ] 断言是精确的，不是宽泛的字符串匹配
- [ ] 如果有数据库操作，验证了数据状态

---

## 相关文档

- [Testing Common Commands](../references/testing-common.md) - 测试命令参考
- [v13 TDD First](../../v13/rules/test/test-tdd-first.md) - v13 TDD 工作流
- [v14 TDD First](../../v14/rules/test/test-tdd-first.md) - v14 TDD 工作流

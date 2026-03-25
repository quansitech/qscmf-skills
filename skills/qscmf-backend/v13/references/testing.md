# Testing Reference

> QSCMF v13 PHPUnit 测试完整指南

## 版本特性

| 特性 | v13 |
|------|-----|
| PHP 版本 | >= 8.1 |
| PHPUnit | ^9.3.0 |
| Laravel | ^8.0 |


> **⚠️ CRITICAL**: 在 `lara/tests/` 中，**禁止直接使用 `D()` 函数**。必须使用 `runTp()` 包装 ThinkPHP 逻辑。详见 [runTp Wrapper](../rules/test/test-runtp-wrapper.md)。
## 测试环境配置

### 配置文件

**phpunit.xml**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<phpunit xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:noNamespaceSchemaLocation="vendor/phpunit/phpunit/phpunit.xsd"
         bootstrap="lara/tests/bootstrap.php"
         colors="true">
    <testsuites>
        <testsuite name="Feature">
            <directory>lara/tests/Feature</directory>
        </testsuite>
        <testsuite name="Unit">
            <directory>lara/tests/Unit</directory>
        </testsuite>
    </testsuites>
    <coverage>
        <include>
            <directory suffix=".php">app/</directory>
        </include>
    </coverage>
</phpunit>
```

## 测试基类

### TestCase 基类

```php
<?php
namespace Lara\Tests;

use Illuminate\Foundation\Testing\TestCase as BaseTestCase;
use Illuminate\Support\Facades\DB;
use Illuminate\Foundation\Testing\DatabaseTransactions;

abstract class TestCase extends BaseTestCase
{
    use CreatesApplication;
    use DatabaseTransactions;

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

    /**
     * 初始化 ThinkPHP 环境
     */
    private function initThinkPHP(): void
    {
        // 设置 ThinkPHP 常量和路径
        if (!defined('APP_PATH')) {
            define('APP_PATH', dirname(__DIR__, 3) . '/app/');
        }
    }

    /**
     * 创建测试数据
     */
    protected function createTestRecord(string $model, array $data): array
    {
        return $this->runTp(function () use ($model, $data) {
            $id = D($model)->add($data);
            return D($model)->find($id);
        });
    }

    /**
     * 断言 JSON 响应
     */
    protected function assertJsonResponse($response, int $status = 1): void
    {
        $response->assertStatus(200)
            ->assertJson(['status' => $status]);
    }
}
```

## API 测试

### RESTful API 测试

```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;

class ProductApiTest extends TestCase
{
    /**
     * 测试获取列表
     */
    public function testGetList(): void
    {
        $response = $this->get('/api.php/Product/gets');

        $response->assertStatus(200)
            ->assertJson(['status' => 1])
            ->assertJsonStructure([
                'status',
                'msg',
                'data' => [
                    'list',
                    'total',
                ]
            ]);
    }

    /**
     * 测试创建
     */
    public function testCreate(): void
    {
        $response = $this->post('/api.php/Product/add', [
            'product_name' => 'Test Product',
            'price' => 99.99,
            'status' => 1,
        ]);

        $response->assertStatus(200)
            ->assertJson([
                'status' => 1,
            ]);
    }

    /**
     * 测试创建验证失败
     */
    public function testCreateValidationFail(): void
    {
        $response = $this->post('/api.php/Product/add', [
            // 缺少必填字段 product_name
            'price' => 99.99,
        ]);

        $response->assertStatus(200)
            ->assertJson([
                'status' => 0,
            ]);
    }

    /**
     * 测试更新
     */
    public function testUpdate(): void
    {
        // 创建测试数据
        $product = $this->createTestRecord('Product', [
            'product_name' => 'Original Name',
            'price' => 50.00,
            'status' => 1,
        ]);

        $response = $this->post('/api.php/Product/edit', [
            'id' => $product['id'],
            'product_name' => 'Updated Name',
            'price' => 99.99,
        ]);

        $response->assertStatus(200)
            ->assertJson(['status' => 1]);
    }

    /**
     * 测试删除
     */
    public function testDelete(): void
    {
        $product = $this->createTestRecord('Product', [
            'product_name' => 'To Delete',
            'price' => 10.00,
            'status' => 1,
        ]);

        $response = $this->post('/api.php/Product/delete', [
            'id' => $product['id'],
        ]);

        $response->assertStatus(200)
            ->assertJson(['status' => 1]);

        // 验证已删除
        $this->runTp(function () use ($product) {
            $deleted = D('Product')->find($product['id']);
            $this->assertNull($deleted);
        });
    }
}
```

## Model 测试

### GyListModel 测试

```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;

class ProductModelTest extends TestCase
{
    /**
     * 测试添加
     */
    public function testAdd(): void
    {
        $result = $this->runTp(function () {
            return D('Product')->add([
                'product_name' => 'Test Product',
                'price' => 99.99,
                'status' => 1,
            ]);
        });

        $this->assertIsInt($result);
        $this->assertGreaterThan(0, $result);
    }

    /**
     * 测试验证规则
     */
    public function testValidation(): void
    {
        $result = $this->runTp(function () {
            // 缺少必填字段
            return D('Product')->add([
                'price' => 99.99,
            ]);
        });

        $this->assertFalse($result);

        // 检查错误信息
        $error = $this->runTp(fn() => D('Product')->getError());
        $this->assertNotEmpty($error);
    }

    /**
     * 测试更新
     */
    public function testUpdate(): void
    {
        $product = $this->createTestRecord('Product', [
            'product_name' => 'Original',
            'price' => 50.00,
            'status' => 1,
        ]);

        $result = $this->runTp(function () use ($product) {
            return D('Product')->where(['id' => $product['id']])->save([
                'product_name' => 'Updated',
                'price' => 99.99,
            ]);
        });

        $this->assertTrue($result !== false);

        // 验证更新结果
        $updated = $this->runTp(fn() => D('Product')->find($product['id']));
        $this->assertEquals('Updated', $updated['product_name']);
        $this->assertEquals(99.99, $updated['price']);
    }
}
```

## Mock 测试

### Mock 外部服务

```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;
use Common\Lib\Wall\ExternalApiService;

class ExternalServiceTest extends TestCase
{
    /**
     * Mock 外部 API
     */
    public function testWithMockedApi(): void
    {
        // 创建 Mock
        $mock = $this->createMock(ExternalApiService::class);

        // 设置期望
        $mock->method('fetchData')
            ->with($this->equalTo(['id' => 1]))
            ->willReturn([
                'success' => true,
                'data' => ['id' => 1, 'name' => 'Mock Data']
            ]);

        // 注入到容器
        app()->instance(ExternalApiService::class, $mock);

        // 执行测试
        $result = $this->runTp(function () {
            $service = new ExternalApiService();
            return $service->fetchData(['id' => 1]);
        });

        $this->assertTrue($result['success']);
        $this->assertEquals('Mock Data', $result['data']['name']);
    }

    /**
     * Mock HTTP 请求
     */
    public function testWithMockedHttp(): void
    {
        Http::fake([
            'external-api.com/*' => Http::response([
                'status' => 'ok',
                'data' => ['result' => 'success']
            ], 200),
        ]);

        $response = Http::get('https://external-api.com/test');

        $this->assertEquals(200, $response->status());
        $this->assertEquals('ok', $response->json('status'));
    }
}
```

### Wall Class Mock

```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;
use Common\Lib\Wall\PaymentGateway;

class PaymentTest extends TestCase
{
    public function testPaymentWithWallMock(): void
    {
        // 使用 Wall Class Mock 模式
        $mockGateway = new class implements PaymentGateway {
            public function charge(array $data): array
            {
                return [
                    'success' => true,
                    'transaction_id' => 'MOCK_TXN_' . time(),
                ];
            }
        };

        // 注入 Mock
        app()->instance(PaymentGateway::class, $mockGateway);

        // 测试支付逻辑
        $orderService = app()->make(\App\Services\OrderService::class);
        $result = $orderService->processPayment([
            'order_id' => 1,
            'amount' => 100.00,
        ]);

        $this->assertTrue($result['success']);
    }
}
```

## 数据提供器

### 使用 DataProvider

```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;

class ValidationTest extends TestCase
{
    /**
     * @dataProvider validationDataProvider
     */
    public function testValidation(array $data, bool $expectedSuccess, ?string $expectedError = null): void
    {
        $result = $this->runTp(function () use ($data) {
            return D('Product')->add($data);
        });

        if ($expectedSuccess) {
            $this->assertGreaterThan(0, $result);
        } else {
            $this->assertFalse($result);
            if ($expectedError) {
                $error = D('Product')->getError();
                $this->assertStringContainsString($expectedError, $error);
            }
        }
    }

    public function validationDataProvider(): array
    {
        return [
            // 有效数据
            'valid data' => [
                ['product_name' => 'Test', 'price' => 100, 'status' => 1],
                true,
            ],
            // 缺少名称
            'missing name' => [
                ['price' => 100, 'status' => 1],
                false,
                '产品名称',
            ],
            // 价格无效
            'invalid price' => [
                ['product_name' => 'Test', 'price' => -10, 'status' => 1],
                false,
                '价格',
            ],
        ];
    }
}
```

## CLI 测试

### CLI 入口点

CLI 入口文件在 `app/` 目录，不是 `www/index.php`：

```
app/jdInfoRefresh  → JDInfoRefreshController
app/queue          → QueueController
app/batchExport    → BatchExportController
```

### CLI 测试模式

```php
/** @test */
public function testCliUpdatesStatus(): void
{
    // 1. 准备数据 - DB facade
    $waybillId = DB::table('qs_jd_waybill')->insertGetId([
        'order_id' => 'JD' . time(),
        'order_status' => 0,
    ]);

    // 2. 设置配置 - runTp (仅此处需要)
    $this->runTp(fn() => C('CANCEL_JD_WAYBILL', true));

    // 3. 执行 CLI
    $this->cli('app/jdInfoRefresh', 'info');

    // 4. 验证结果 - DB facade
    $result = DB::table('qs_jd_waybill')->where('id', $waybillId)->first();
    $this->assertEquals(1, $result->order_status);
}
```

### HTTP 集成测试（推荐）

> **优先使用 HTTP 测试** - 性能更好（~50ms vs ~500ms）

```php
/** @test */
public function testHttpUpdatesStatusWithMock(): void
{
    // 1. 准备数据 - DB facade (不用 runTp)
    $waybillId = DB::table('qs_jd_waybill')->insertGetId([
        'order_id' => 'JD' . time(),
        'order_status' => 0,
    ]);

    // 2. 设置 Mock - app()->instance() (不用 runTp)
    $mock = $this->createMock(\Common\Lib\Wall\JdClientWall::class);
    $mock->method('execute')->willReturn(['success' => true, 'orderStatus' => 2]);
    app()->instance(\Common\Lib\Wall\JdClientWall::class, $mock);

    // 3. 执行 - HTTP GET (不用 runTp)
    $response = $this->get('/JDInfoRefresh/info');

    // 4. 验证结果 - DB facade (不用 runTp)
    $result = DB::table('qs_jd_waybill')->where('id', $waybillId)->first();
    $this->assertEquals(2, $result->order_status);
}
```

> 详见: [HTTP First Testing](../rules/test/test-http-first.md)

## 测试命令

> **通用测试命令**: 详见 [_shared/references/testing-common.md](_shared/references/testing-common.md)

### 基础命令（推荐）

```bash
# 定义基础命令别名
PHPUNIT="php -d display_errors=on -d xdebug.mode=off -d xdebug.start_with_request=0 vendor/bin/phpunit"

# 运行所有测试
$PHPUNIT

# 运行单个测试类
$PHPUNIT lara/tests/Feature/ProductTest.php

# 运行单个测试方法
$PHPUNIT --filter "testMethodName" lara/tests/Feature/ProductTest.php

# 详细输出
$PHPUNIT -v
```

## 测试最佳实践

### 1. 命名规范

**格式**: `test` + `camelCase`

```php
// ✅ 正确 - test + camelCase
public function testCreateOrderWithValidData(): void {}
public function testCreateOrderFailsWhenStockIsInsufficient(): void {}
public function testYearFilter(): void {}
public function testCompleteTimeBoundary(): void {}
public function testYearAndCompleteTimeCombined(): void {}

// ❌ 错误 - snake_case
public function test_create_order(): void {}
public function test_year_filter(): void {}

// ❌ 错误 - 无 test 前缀
public function createOrder(): void {}
public function yearFilter(): void {}
```

### 测试命名模式

| 模式 | 示例 | 说明 |
|------|------|------|
| `test{Action}` | `testCreateOrder()` | 基础动作测试 |
| `test{Action}{Result}` | `testCreateOrderReturnsId()` | 动作+结果 |
| `test{Condition}{Expected}` | `testEmptySortingCannotFinish()` | 条件+期望 |
| `test{Field}{Comparison}` | `testDetailCreateDateEqualsSortingCreateDate()` | 字段比较 |
| `test{Filter}` | `testYearFilter()` | 单个过滤器 |
| `test{Filter}And{Filter}` | `testYearAndStatusFilter()` | 多条件组合 |

### 2. 单一职责

```php
// 好：每个测试只验证一个行为
public function testCreate(): void { /* 只测试创建 */ }
public function testUpdate(): void { /* 只测试更新 */ }
public function testDelete(): void { /* 只测试删除 */ }

// 不好：一个测试验证多个行为
public function testCrud(): void {
    // 创建
    // 更新
    // 删除
}
```

### 3. 数据隔离

```php
protected function setUp(): void
{
    parent::setUp();
    // 使用事务确保数据隔离
    DB::beginTransaction();
}

protected function tearDown(): void
{
    DB::rollBack();
    parent::tearDown();
}
```

### 4. 避免硬编码

```php
// 好：使用常量或配置
$this->assertEquals(DBCont::NORMAL_STATUS, $product['status']);

// 不好：硬编码
$this->assertEquals(1, $product['status']);
```

## 相关文档

- [Development Standards](development-standards.md) - 开发规范
- [Model Guide](model-guide.md) - 模型开发指南
- [API Controllers](api-controllers.md) - API 开发指南

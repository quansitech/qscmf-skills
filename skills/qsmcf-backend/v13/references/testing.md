# Testing Reference

> QSCMF v13 PHPUnit 测试完整指南

## 版本特性

| 特性 | v13 |
|------|-----|
| PHP 版本 | >= 8.1 |
| PHPUnit | ^9.3.0 |
| Laravel | ^8.0 |

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

## 测试命令

### 常用命令

```bash
# 运行所有测试
vendor/bin/phpunit

# 运行特定文件
vendor/bin/phpunit lara/tests/Feature/ProductTest.php

# 运行特定方法
vendor/bin/phpunit --filter testCreate

# 运行特定测试套件
vendor/bin/phpunit --testsuite Feature

# 生成代码覆盖率报告
vendor/bin/phpunit --coverage-html coverage

# 并行测试
vendor/bin/paratest

# 只运行快速测试
vendor/bin/phpunit --exclude-group slow

# 详细输出
vendor/bin/phpunit -v
```

## 测试最佳实践

### 1. 命名规范

```php
// 好的命名
public function testCreateOrderWithValidData(): void {}
public function testCreateOrderFailsWhenStockIsInsufficient(): void {}

// 不好的命名
public function testOrder(): void {}
public function test1(): void {}
```

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

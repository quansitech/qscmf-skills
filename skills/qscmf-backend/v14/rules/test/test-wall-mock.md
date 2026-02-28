---
title: Wall Mock Pattern (v14)
impact: HIGH
impactDescription: Required for testing external API calls
tags: test, mock, wall, v14, phpunit10
---

# Wall Class Mock 测试模式 (v14)

> PHPUnit 10 环境下的外部服务 Mock 测试指南

## When to Use This Rule

- 测试调用外部 API 的代码
- 隔离测试与外部依赖
- 模拟 API 响应场景（成功、失败、超时）

---

## 概述

Wall Class 模式用于在测试中 Mock 外部服务（如支付网关、短信服务、第三方 API），使测试不依赖外部环境。

---

## PHPUnit 10 Mocking 变化

PHPUnit 10 移除了一些 PHPUnit 9 的方法：

| 移除的方法 | 替代方案 |
|-----------|---------|
| `withConsecutive()` | `willReturnCallback()` + 回调验证 |
| `returnCallback()` | `willReturnCallback()` |

**推荐使用**：
- 简单顺序返回：`willReturnOnConsecutiveCalls()`
- 复杂场景：`willReturnCallback()`

---

## Wall Class 模式

### 基本结构

Wall 类封装外部服务调用：

```php
<?php

declare(strict_types=1);

namespace Common\Lib\Wall;

class PaymentWall
{
    public function createOrder(array $data): array
    {
        $client = new \GuzzleHttp\Client();
        $response = $client->post('https://api.payment.com/orders', [
            'json' => $data
        ]);

        return json_decode($response->getBody(), true);
    }

    public function queryOrder(string $orderId): array
    {
        $client = new \GuzzleHttp\Client();
        $response = $client->get("https://api.payment.com/orders/{$orderId}");

        return json_decode($response->getBody(), true);
    }
}
```

### NoLogClient Mock 实现

用于测试环境的完整 Mock 实现：

```php
<?php

declare(strict_types=1);

namespace Common\Lib\BusinessWall;

/**
 * 无日志客户端 - 用于测试环境
 */
class NoLogClient
{
    protected array $config;

    public function __construct(array $config = [])
    {
        $this->config = $config;
    }

    public function send(string $endpoint, array $data = []): array
    {
        return [
            'success' => true,
            'data' => $this->getMockData($endpoint),
            'message' => 'Mock response',
        ];
    }

    protected function getMockData(string $endpoint): array
    {
        $mockData = [
            '/api/payment/create' => [
                'order_id' => 'MOCK_ORDER_' . time(),
                'pay_url' => 'https://mock-payment.example.com/pay/mock',
            ],
            '/api/sms/send' => [
                'message_id' => 'MOCK_MSG_' . time(),
                'status' => 'sent',
            ],
        ];

        return $mockData[$endpoint] ?? [];
    }
}
```

---

## 接口与工厂

### 接口定义

```php
<?php

declare(strict_types=1);

namespace Common\Lib\BusinessWall;

interface WallClientInterface
{
    public function send(string $endpoint, array $data = []): array;
    public function getStatus(): string;
}
```

### 工厂模式

```php
<?php

declare(strict_types=1);

namespace Common\Lib\BusinessWall;

class WallClientFactory
{
    public static function create(): WallClientInterface
    {
        $clientClass = C('BUSINESS_WALL_CLIENT', NoLogClient::class);

        return new $clientClass([
            'api_key' => env('BUSINESS_API_KEY'),
            'api_url' => env('BUSINESS_API_URL'),
        ]);
    }
}
```

---

## 配置切换

### 环境配置

```php
// config.php

// 生产环境 - 使用真实服务
'BUSINESS_WALL_CLIENT' => \Common\Lib\BusinessWall\RealClient::class,

// 测试环境 - 使用 Mock
'BUSINESS_WALL_CLIENT' => \Common\Lib\BusinessWall\NoLogClient::class,
```

### .env 配置

```bash
# .env.testing
BUSINESS_WALL_CLIENT=Common\Lib\BusinessWall\NoLogClient
```

---

## 在业务代码中使用

```php
<?php

declare(strict_types=1);

namespace Common\Lib;

use Common\Lib\BusinessWall\WallClientFactory;

class PaymentService
{
    protected $client;

    public function __construct()
    {
        $this->client = WallClientFactory::create();
    }

    public function createOrder(array $orderData): array
    {
        $response = $this->client->send('/api/payment/create', $orderData);

        if (!$response['success']) {
            throw new \Exception($response['message']);
        }

        return $response['data'];
    }
}
```

---

## 测试用例

### 方式一：PHPUnit Mock

在 Model 中提供 setter 方法支持依赖注入：

```php
<?php

declare(strict_types=1);

namespace Common\Model;

use Common\Lib\Wall\PaymentWall;
use Gy_Library\GyListModel;

class OrderModel extends GyListModel
{
    protected PaymentWall $paymentWall;

    public function __construct()
    {
        parent::__construct();
        $this->paymentWall = new PaymentWall();
    }

    public function setPaymentWall(PaymentWall $wall): void
    {
        $this->paymentWall = $wall;
    }

    public function createPayment(int $orderId): array
    {
        $order = $this->find($orderId);

        return $this->paymentWall->createOrder([
            'order_no' => $order['order_no'],
            'amount' => $order['total_amount'],
        ]);
    }
}
```

测试代码：

```php
<?php

declare(strict_types=1);

namespace Tests\Feature;

use PHPUnit\Framework\TestCase;
use Common\Lib\Wall\PaymentWall;

class OrderTest extends TestCase
{
    public function testCreatePaymentWithMock(): void
    {
        $mockWall = $this->createMock(PaymentWall::class);

        $mockWall->expects($this->once())
            ->method('createOrder')
            ->with($this->callback(function(array $data): bool {
                return $data['order_no'] === 'ORD001';
            }))
            ->willReturn([
                'status' => 'success',
                'payment_url' => 'https://pay.example.com/xxx'
            ]);

        $orderModel = D('Order');
        $orderModel->setPaymentWall($mockWall);

        $result = $orderModel->createPayment(1);

        $this->assertEquals('success', $result['status']);
        $this->assertArrayHasKey('payment_url', $result);
    }
}
```

### 方式二：配置驱动 Mock

```php
<?php

declare(strict_types=1);

namespace Tests\Feature;

use Lara\Tests\TestCase;
use Common\Lib\BusinessWall\NoLogClient;

class PaymentTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        C('BUSINESS_WALL_CLIENT', NoLogClient::class);
    }

    public function testCreatePayment(): void
    {
        $response = $this->post('/api/payment/create', [
            'amount' => 100,
            'order_no' => 'TEST_ORDER_001',
        ]);

        $response->assertStatus(200)
            ->assertJson(['status' => 1])
            ->assertJsonStructure([
                'status',
                'data' => [
                    'order_id',
                    'pay_url',
                ],
            ]);
    }
}
```

### 方式三：自定义 Mock 类

```php
<?php

declare(strict_types=1);

namespace Tests\Mocks;

class MockPaymentWall
{
    private array $responses = [];
    private int $callCount = 0;

    public function setResponse(string $method, array $response): void
    {
        $this->responses[$method] = $response;
    }

    public function setSequentialResponses(string $method, array $responses): void
    {
        $this->responses[$method] = $responses;
    }

    public function createOrder(array $data): array
    {
        $response = $this->responses['createOrder'] ?? ['status' => 'mock_success'];

        if (isset($response[0])) {
            return $response[$this->callCount++ % count($response)];
        }

        return $response;
    }

    public function queryOrder(string $orderId): array
    {
        return $this->responses['queryOrder'] ?? ['status' => 'paid'];
    }

    public function reset(): void
    {
        $this->responses = [];
        $this->callCount = 0;
    }
}
```

使用自定义 Mock：

```php
public function testWithCustomMock(): void
{
    $mock = new \Lara\Tests\Mocks\MockPaymentWall();
    $mock->setResponse('createOrder', [
        'status' => 'success',
        'payment_url' => 'https://mock.pay/xxx'
    ]);

    $orderModel = D('Order');
    $orderModel->setPaymentWall($mock);

    $result = $orderModel->createPayment(1);
    $this->assertEquals('success', $result['status']);

    $mock->reset();
}
```

---

## PHPUnit 10 顺序返回

### 简单顺序返回

```php
public function testMultipleApiCalls(): void
{
    $mockWall = $this->createMock(PaymentWall::class);

    $mockWall->method('queryOrder')
        ->willReturnOnConsecutiveCalls(
            ['status' => 'pending'],
            ['status' => 'paid'],
            ['status' => 'completed']
        );

    $orderModel = D('Order');
    $orderModel->setPaymentWall($mockWall);

    $this->assertEquals('pending', $orderModel->checkPaymentStatus(1)['status']);
    $this->assertEquals('paid', $orderModel->checkPaymentStatus(1)['status']);
    $this->assertEquals('completed', $orderModel->checkPaymentStatus(1)['status']);
}
```

### 复杂场景（替代 withConsecutive）

```php
public function testConsecutiveCallsWithValidation(): void
{
    $mockWall = $this->createMock(PaymentWall::class);

    $callCount = 0;
    $expectedIds = ['ORD001', 'ORD002'];
    $responses = [
        ['status' => 'pending'],
        ['status' => 'paid']
    ];

    $mockWall->expects($this->exactly(2))
        ->method('queryOrder')
        ->with($this->callback(function(string $orderId) use (&$callCount, $expectedIds): bool {
            return $orderId === $expectedIds[$callCount++];
        }))
        ->willReturnCallback(function() use (&$callCount, $responses): array {
            return $responses[$callCount - 1];
        });

    // 测试逻辑...
}
```

---

## 模拟错误场景

```php
public function testPaymentFailure(): void
{
    $mockWall = $this->createMock(PaymentWall::class);

    $mockWall->method('createOrder')
        ->willThrowException(new \Exception('Payment service unavailable'));

    $orderModel = D('Order');
    $orderModel->setPaymentWall($mockWall);

    $this->expectException(\Exception::class);
    $this->expectExceptionMessage('Payment service unavailable');

    $orderModel->createPayment(1);
}
```

---

## PHPUnit 10 Attributes

```php
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\Attributes\Group;
use PHPUnit\Framework\Attributes\TestDox;

#[Group('mock')]
class PaymentMockTest extends TestCase
{
    #[Test]
    #[TestDox('Payment wall returns success on valid order')]
    public function paymentReturnsSuccessOnValidOrder(): void
    {
        $mockWall = $this->createMock(PaymentWall::class);
        $mockWall->method('createOrder')
            ->willReturn(['status' => 'success']);

        // 测试逻辑...
    }
}
```

---

## 测试覆盖率

| 场景 | 覆盖方式 |
|------|---------|
| 正常响应 | Mock 返回成功数据 |
| 异常响应 | Mock 返回失败状态 |
| 超时场景 | Mock 抛出 TimeoutException |
| 边界值 | Mock 返回边界数据（空数组、最大值等） |

---

## 最佳实践

1. **使用 Wall 模式**：所有外部服务调用都应封装在 Wall 类中
2. **提供 setter 方法**：支持依赖注入，便于测试时替换
3. **配置驱动**：通过配置切换真实/Mock 客户端
4. **工厂模式**：统一创建客户端实例
5. **接口定义**：确保 Mock 与真实实现一致
6. **测试覆盖**：Mock 应覆盖所有业务场景（成功、失败、边界）
7. **文档同步**：Mock 返回值应与真实 API 文档一致
8. **重置状态**：自定义 Mock 在 tearDown() 中重置

---

## Related Rules

- [TDD First](test-tdd-first.md) - 测试驱动开发
- [Test Transaction](test-transaction.md) - 事务测试
- [Pattern Wall Class](../pattern/pattern-wall-class.md) - Wall 类模式

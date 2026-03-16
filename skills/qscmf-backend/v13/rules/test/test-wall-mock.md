---
title: Wall Mock Pattern (v13)
impact: HIGH
impactDescription: Required for testing external API calls
tags: test, mock, wall, v13
---

## Wall Mock Pattern (v13)

Mocking external services using the Wall class pattern for testing.

### When to Use This Rule

- Testing code that calls external APIs
- Isolating tests from external dependencies
- Simulating API responses

---

## Wall Class Pattern

The Wall class wraps external service calls for easy mocking:

```php
// app/Common/Lib/Wall/PaymentWall.php

namespace Common\Lib\Wall;

class PaymentWall
{
    public function createOrder(array $data): array
    {
        // Real API call
        $client = new \GuzzleHttp\Client();
        $response = $client->post('https://api.payment.com/orders', [
            'json' => $data
        ]);

        return json_decode($response->getBody(), true);
    }

    public function queryOrder(string $orderId): array
    {
        // Real API call
        $client = new \GuzzleHttp\Client();
        $response = $client->get("https://api.payment.com/orders/{$orderId}");

        return json_decode($response->getBody(), true);
    }
}
```

---

## Using Wall in Code

```php
// app/Common/Model/OrderModel.php

class OrderModel extends GyListModel
{
    protected $paymentWall;

    public function __construct()
    {
        parent::__construct();
        $this->paymentWall = new \Common\Lib\Wall\PaymentWall();
    }

    // For dependency injection in tests
    public function setPaymentWall($wall): void
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

---

## Mocking in Tests

### Using PHPUnit Mocks

```php
// lara/tests/Feature/OrderTest.php

public function testCreatePaymentWithMock(): void
{
    // Create mock
    $mockWall = $this->createMock(\Common\Lib\Wall\PaymentWall::class);

    // Configure mock behavior
    $mockWall->expects($this->once())
        ->method('createOrder')
        ->with($this->callback(function($data) {
            return $data['order_no'] === 'ORD001';
        }))
        ->willReturn([
            'status' => 'success',
            'payment_url' => 'https://pay.example.com/xxx'
        ]);

    // Inject mock
    $orderModel = D('Order');
    $orderModel->setPaymentWall($mockWall);

    // Test
    $result = $orderModel->createPayment(1);

    $this->assertEquals('success', $result['status']);
    $this->assertArrayHasKey('payment_url', $result);
}
```

### Using Custom Mock Class

```php
// lara/tests/Mocks/MockPaymentWall.php

namespace Lara\Tests\Mocks;

class MockPaymentWall
{
    private $responses = [];

    public function setResponse(string $method, array $response): void
    {
        $this->responses[$method] = $response;
    }

    public function createOrder(array $data): array
    {
        return $this->responses['createOrder'] ?? ['status' => 'mock_success'];
    }

    public function queryOrder(string $orderId): array
    {
        return $this->responses['queryOrder'] ?? ['status' => 'paid'];
    }
}

// In test
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
}
```

---

## Simulating Errors

```php
public function testPaymentFailure(): void
{
    $mockWall = $this->createMock(\Common\Lib\Wall\PaymentWall::class);

    // Simulate API failure
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

## Best Practices

1. **Always use Wall pattern** for external services
2. **Provide setter method** for dependency injection
3. **Test both success and failure** scenarios
4. **Document mock behavior** in test comments
5. **Reset mocks between tests** in tearDown()

---

---

## 容器注入模式

业务类通过容器获取 Wall，测试时替换为 mock。

### Wall 类

```php
class GuzzleWall
{
    protected \GuzzleHttp\Client $client;

    public function __construct(\GuzzleHttp\Client $client)
    {
        $this->client = $client;
    }

    public function get(string $uri): array
    {
        return json_decode($this->client->get($uri)->getBody(), true);
    }
}
```

### 业务代码

```php
class ExternalService
{
    protected GuzzleWall $api_client;

    public function __construct()
    {
        $client = new \GuzzleHttp\Client(['base_uri' => 'https://api.example.com']);
        $this->api_client = app()->makeWith(GuzzleWall::class, ['client' => $client]);
    }

    public function fetch(): array
    {
        return $this->api_client->get('/data');
    }
}
```

### 测试代码

```php
public function testFetch(): void
{
    $mock = $this->createMock(GuzzleWall::class);
    $mock->method('get')->willReturn(['id' => 1]);

    app()->instance(GuzzleWall::class, $mock);

    $service = new ExternalService();
    $result = $service->fetch();

    $this->assertEquals(['id' => 1], $result);
}
```

---

## 构造函数注入模式（零业务代码改动）

> 适用于：代理第三方 SDK，Mock 粒度在最终请求层

### 核心思想

```
┌──────────────────────────────────────────────────────────────┐
│  业务代码                                                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ $sdk->config = ...                                      │ │
│  │ $sdk->buildParams($data)  // ← 参数构建逻辑，需测试覆盖   │ │
│  │ $sdk->validate($params)   // ← 验证逻辑，需测试覆盖      │ │
│  │ $sdk->execute($request)   // ← 最终 HTTP 请求，Mock 点  │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

### Wall 类（属性代理模式）

```php
// Wall 类：代理真实 SDK，转发所有属性和方法调用

class SdkClientWall
{
    protected $realClient;  // 真实的第三方 SDK 实例

    public function __construct()
    {
        $this->realClient = new \Vendor\Sdk\Client();
    }

    // 代理属性写入
    public function __set($name, $value)
    {
        $this->realClient->$name = $value;
    }

    // 代理属性读取
    public function __get($name)
    {
        return $this->realClient->$name;
    }

    // 最终请求方法（Mock 点）
    public function execute($request, $token = null)
    {
        return $this->realClient->execute($request, $token);
    }
}
```

### 业务代码改动（仅构造函数）

```php
// 伪代码：业务服务类

class ExternalService
{
    public $client;  // 保持原属性名不变

    public function __construct()
    {
        // 改动点：仅此一行
        // BEFORE: $this->client = new \Vendor\Sdk\Client();
        // AFTER:  $this->client = app()->make(SdkClientWall::class);

        $this->client = app()->make(SdkClientWall::class);

        // 以下代码完全不变
        $this->client->apiKey = config('api.key');
        $this->client->endpoint = config('api.url');
    }

    public function doSomething($data)
    {
        // 所有调用方式完全不变
        $this->client->someProperty = 'value';
        return $this->client->execute($request);
    }
}
```

### 测试代码（容器注入 Mock）

```php
// 伪代码：测试用例

public function testBusinessLogic(): void
{
    // 1. 创建 Mock
    $mock = $this->createMock(SdkClientWall::class);
    $mock->method('execute')
        ->willReturn(['status' => 'success', 'id' => 'MOCK_001']);

    // 2. 注入容器
    app()->instance(SdkClientWall::class, $mock);

    // 3. 执行测试
    // 参数构建、验证等上游逻辑全部被测试覆盖
    $result = $service->doSomething($data);

    $this->assertEquals('success', $result['status']);
}
```

### 模式优势

| 特性 | 说明 |
|------|------|
| **零业务改动** | 仅修改构造函数 1 行，所有方法调用不变 |
| **精准 Mock** | Mock 在 `execute()` 层，上游逻辑全被覆盖 |
| **容器原生** | `app()->make()` / `app()->instance()` |
| **属性代理** | `__get`/`__set` 确保属性访问透明 |

### 适用场景

- 第三方 SDK（支付、物流、短信、云服务等）
- 需要 Mock HTTP 层但保留业务逻辑测试
- 追求最小化代码改动

---

## Related Rules

- [TDD First](test-tdd-first.md) - Test-driven development
- [Test Transaction](test-transaction.md) - Transaction testing
- [Pattern Wall Class](../pattern/pattern-wall-class.md) - Wall class pattern

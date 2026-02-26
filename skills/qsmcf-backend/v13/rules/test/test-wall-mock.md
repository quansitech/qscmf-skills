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

## Related Rules

- [TDD First](test-tdd-first.md) - Test-driven development
- [Test Transaction](test-transaction.md) - Transaction testing
- [Pattern Wall Class](../pattern/pattern-wall-class.md) - Wall class pattern

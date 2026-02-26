---
title: Wall Mock Pattern (v14)
impact: HIGH
impactDescription: Required for testing external API calls
tags: test, mock, wall, v14, phpunit10
---

## Wall Mock Pattern (v14)

Mocking external services using the Wall class pattern for testing with PHPUnit 10.

### When to Use This Rule

- Testing code that calls external APIs
- Isolating tests from external dependencies
- Simulating API responses

---

## PHPUnit 10 Mocking Changes

Key differences from PHPUnit 9:

- **`withConsecutive()` removed** - Use `willReturnCallback()` instead
- **`returnCallback()` syntax** - Simplified callback handling
- **Strict type expectations** - Use `willReturnOnConsecutiveCalls()`
- **Mock builder improvements** - Better method stub configuration

---

## Wall Class Pattern

The Wall class wraps external service calls for easy mocking:

```php
// app/Common/Lib/Wall/PaymentWall.php

<?php

declare(strict_types=1);

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

    // For dependency injection in tests
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

---

## Mocking in Tests (PHPUnit 10)

### Using PHPUnit Mocks

```php
// lara/tests/Feature/OrderTest.php

<?php

declare(strict_types=1);

namespace Lara\Tests\Feature;

use PHPUnit\Framework\TestCase;
use Common\Lib\Wall\PaymentWall;

class OrderTest extends TestCase
{
    public function testCreatePaymentWithMock(): void
    {
        // Create mock
        $mockWall = $this->createMock(PaymentWall::class);

        // Configure mock behavior (PHPUnit 10 style)
        $mockWall->expects($this->once())
            ->method('createOrder')
            ->with($this->callback(function(array $data): bool {
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
}
```

### Replacing withConsecutive() (PHPUnit 10)

PHPUnit 10 removed `withConsecutive()`. Use `willReturnCallback()` instead:

```php
// PHPUnit 9 (deprecated)
$mock->expects($this->exactly(2))
    ->method('queryOrder')
    ->withConsecutive(
        ['ORD001'],
        ['ORD002']
    )
    ->willReturnOnConsecutiveCalls(
        ['status' => 'pending'],
        ['status' => 'paid']
    );

// PHPUnit 10 (correct)
$callCount = 0;
$mock->expects($this->exactly(2))
    ->method('queryOrder')
    ->with($this->callback(function(string $orderId) use (&$callCount): bool {
        $expectedIds = ['ORD001', 'ORD002'];
        return $orderId === $expectedIds[$callCount++];
    }))
    ->willReturnCallback(function() use (&$callCount): array {
        $responses = [
            ['status' => 'pending'],
            ['status' => 'paid']
        ];
        return $responses[$callCount - 1];
    });
```

### Simplified Multiple Returns

```php
public function testMultipleApiCalls(): void
{
    $mockWall = $this->createMock(PaymentWall::class);

    // Use willReturnOnConsecutiveCalls for simple sequential returns
    $mockWall->method('queryOrder')
        ->willReturnOnConsecutiveCalls(
            ['status' => 'pending'],
            ['status' => 'paid'],
            ['status' => 'completed']
        );

    $orderModel = D('Order');
    $orderModel->setPaymentWall($mockWall);

    // First call
    $result1 = $orderModel->checkPaymentStatus(1);
    $this->assertEquals('pending', $result1['status']);

    // Second call
    $result2 = $orderModel->checkPaymentStatus(1);
    $this->assertEquals('paid', $result2['status']);

    // Third call
    $result3 = $orderModel->checkPaymentStatus(1);
    $this->assertEquals('completed', $result3['status']);
}
```

---

## Using Custom Mock Class

```php
// lara/tests/Mocks/MockPaymentWall.php

<?php

declare(strict_types=1);

namespace Lara\Tests\Mocks;

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

        if (is_array($response) && isset($response[0])) {
            // Sequential responses
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

### Using Custom Mock in Tests

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

## Simulating Errors

```php
public function testPaymentFailure(): void
{
    $mockWall = $this->createMock(PaymentWall::class);

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

## PHPUnit 10 Attributes for Mock Tests

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

        // Test implementation
    }
}
```

---

## Best Practices

1. **Always use Wall pattern** for external services
2. **Provide setter method** for dependency injection with type hints
3. **Test both success and failure** scenarios
4. **Document mock behavior** in test comments
5. **Reset mocks between tests** in tearDown()
6. **Use willReturnCallback()** instead of removed withConsecutive()
7. **Add strict_types declaration** to all mock classes

---

## Related Rules

- [TDD First](test-tdd-first.md) - Test-driven development
- [Test Transaction](test-transaction.md) - Transaction testing
- [Pattern Wall Class](../pattern/pattern-wall-class.md) - Wall class pattern

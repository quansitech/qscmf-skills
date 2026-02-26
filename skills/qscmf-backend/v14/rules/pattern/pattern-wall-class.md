---
title: Wall Class Pattern (v14)
impact: HIGH
impactDescription: Required for external API integration
tags: pattern, wall, api, v14
---

## Wall Class Pattern (v14)

Wrap external service calls for testability and maintainability in QSCMF v14.

### When to Use This Rule

- Calling external APIs
- Integrating third-party services
- Creating testable service wrappers

---

## Basic Wall Class

```php
// app/Common/Lib/Wall/PaymentWall.php

namespace Common\Lib\Wall;

class PaymentWall
{
    protected $apiUrl = 'https://api.payment.com';
    protected $apiKey;
    protected $timeout = 30;

    public function __construct()
    {
        $this->apiKey = C('PAYMENT_API_KEY');
    }

    /**
     * Create payment order
     */
    public function createOrder(array $data): array
    {
        $client = new \GuzzleHttp\Client([
            'timeout' => $this->timeout
        ]);

        try {
            $response = $client->post($this->apiUrl . '/orders', [
                'headers' => [
                    'Authorization' => 'Bearer ' . $this->apiKey,
                    'Content-Type' => 'application/json'
                ],
                'json' => $data
            ]);

            return json_decode($response->getBody(), true);
        } catch (\Exception $e) {
            return [
                'status' => 'error',
                'message' => $e->getMessage()
            ];
        }
    }

    /**
     * Query order status
     */
    public function queryOrder(string $orderId): array
    {
        $client = new \GuzzleHttp\Client([
            'timeout' => $this->timeout
        ]);

        try {
            $response = $client->get($this->apiUrl . '/orders/' . $orderId, [
                'headers' => [
                    'Authorization' => 'Bearer ' . $this->apiKey
                ]
            ]);

            return json_decode($response->getBody(), true);
        } catch (\Exception $e) {
            return [
                'status' => 'error',
                'message' => $e->getMessage()
            ];
        }
    }

    /**
     * Close order
     */
    public function closeOrder(string $orderId): bool
    {
        $client = new \GuzzleHttp\Client([
            'timeout' => $this->timeout
        ]);

        try {
            $response = $client->post($this->apiUrl . '/orders/' . $orderId . '/close', [
                'headers' => [
                    'Authorization' => 'Bearer ' . $this->apiKey
                ]
            ]);

            $result = json_decode($response->getBody(), true);
            return $result['status'] === 'success';
        } catch (\Exception $e) {
            return false;
        }
    }
}
```

---

## Using Wall in Model

```php
// app/Common/Model/OrderModel.class.php

class OrderModel extends GyListModel
{
    protected $paymentWall;

    public function setPaymentWall($wall)
    {
        $this->paymentWall = $wall;
    }

    public function getPaymentWall()
    {
        if (!$this->paymentWall) {
            $this->paymentWall = new \Common\Lib\Wall\PaymentWall();
        }
        return $this->paymentWall;
    }

    public function createPayment(int $orderId): array
    {
        $order = $this->find($orderId);
        if (!$order) {
            return ['status' => 'error', 'message' => '订单不存在'];
        }

        $wall = $this->getPaymentWall();

        $result = $wall->createOrder([
            'order_no' => $order['order_no'],
            'amount' => $order['total_amount'],
            'notify_url' => U('Api/Notify/payment', [], true, true)
        ]);

        if ($result['status'] === 'success') {
            // Update order with payment info
            $this->where(['id' => $orderId])->save([
                'payment_no' => $result['payment_no'],
                'payment_url' => $result['payment_url']
            ]);
        }

        return $result;
    }
}
```

---

## SMS Wall Example

```php
// app/Common/Lib/Wall/SmsWall.php

namespace Common\Lib\Wall;

class SmsWall
{
    protected $apiUrl;
    protected $apiKey;
    protected $apiSecret;

    public function __construct()
    {
        $this->apiUrl = C('SMS_API_URL');
        $this->apiKey = C('SMS_API_KEY');
        $this->apiSecret = C('SMS_API_SECRET');
    }

    /**
     * Send SMS
     */
    public function send(string $mobile, string $content): array
    {
        $client = new \GuzzleHttp\Client();

        try {
            $response = $client->post($this->apiUrl . '/send', [
                'form_params' => [
                    'api_key' => $this->apiKey,
                    'api_secret' => $this->apiSecret,
                    'mobile' => $mobile,
                    'content' => $content
                ]
            ]);

            return json_decode($response->getBody(), true);
        } catch (\Exception $e) {
            return [
                'status' => 'error',
                'message' => $e->getMessage()
            ];
        }
    }

    /**
     * Send verification code
     */
    public function sendVerifyCode(string $mobile, string $code): array
    {
        $content = sprintf('您的验证码是：%s，5分钟内有效。', $code);
        return $this->send($mobile, $content);
    }
}
```

---

## Benefits

1. **Testability** - Easy to mock in tests
2. **Centralization** - API logic in one place
3. **Error handling** - Consistent error responses
4. **Configuration** - Centralized API settings
5. **Logging** - Easy to add logging/debugging

---

## Related Rules

- [Test Wall Mock](../test/test-wall-mock.md) - Mocking Wall classes
- [Pattern Queue Job](pattern-queue-job.md) - Async processing
- [API Controllers Reference](../../references/api-controllers.md) - API guide

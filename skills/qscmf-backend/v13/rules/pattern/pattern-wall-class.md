---
title: Wall Class Pattern (v13)
impact: HIGH
impactDescription: Required for external API integration
tags: pattern, wall, api, v13
---

## Wall Class Pattern (v13)

Wrap external service calls for testability and maintainability in QSCMF v13.

### When to Use This Rule

- Calling external APIs
- Integrating third-party services
- Creating testable service wrappers

---

## Basic Wall Class

```php
// Wall 类文件 (如 PaymentWall.php)

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
// Model 类文件 (如 OrderModel.class.php)

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
// Wall 类文件 (如 SmsWall.php)

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

## SDK Proxy Pattern（零改动注入）

> 适用于：代理第三方 SDK，Mock 粒度在最终请求层

### 核心思想

当业务代码使用第三方 SDK 时，通过 **属性代理** 封装 SDK，仅修改构造函数注入方式，实现：
- 业务代码 **零改动**
- Mock 粒度在 `execute()` 层（HTTP 请求前最后一步）
- 上游参数构建、验证逻辑 **全被测试覆盖**

### Wall 类结构（伪代码）

```php
// 伪代码：SDK 代理 Wall

namespace Common\Lib\Wall;

/**
 * 代理第三方 SDK，支持容器注入 Mock
 */
class SdkClientWall
{
    protected $realClient;  // 真实 SDK 实例

    public function __construct()
    {
        $this->realClient = new \Vendor\Sdk\Client();
    }

    // 代理属性设置（透明传递）
    public function __set($name, $value)
    {
        $this->realClient->$name = $value;
    }

    // 代理属性获取（透明传递）
    public function __get($name)
    {
        return $this->realClient->$name;
    }

    // 执行请求（Mock 点）
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
    public $client;  // 保持原属性名

    public function __construct()
    {
        // BEFORE: $this->client = new \Vendor\Sdk\Client();
        // AFTER:  仅此一行改动
        $this->client = app()->make(SdkClientWall::class);

        // 以下完全不变
        $this->client->apiKey = config('api.key');
    }

    // 所有方法调用完全不变
    public function doSomething($data)
    {
        $this->client->someProperty = 'value';
        return $this->client->execute($request);
    }
}
```

### 模式对比

| 模式 | Mock 粒度 | 业务改动 | 上游逻辑覆盖 |
|------|----------|---------|-------------|
| **Setter 注入** | 方法层 | 需添加 setter | 部分 |
| **SDK Proxy** | execute() 层 | 仅构造函数 1 行 | 完整 |

### 适用场景

- 第三方 SDK（支付、物流、短信、云服务等）
- 需要 Mock HTTP 层但保留业务逻辑测试
- 追求最小化代码改动

---

## Benefits

1. **Testability** - Easy to mock in tests
2. **Centralization** - API logic in one place
3. **Error handling** - Consistent error responses
4. **Configuration** - Centralized API settings
5. **Logging** - Easy to add logging/debugging
6. **Zero Change Injection** - SDK Proxy pattern enables minimal code change

---

## Related Rules

- [Test Wall Mock](../test/test-wall-mock.md) - Mocking Wall classes
- [Pattern Queue Job](pattern-queue-job.md) - Async processing
- [API Controllers Reference](../../references/api-controllers.md) - API guide

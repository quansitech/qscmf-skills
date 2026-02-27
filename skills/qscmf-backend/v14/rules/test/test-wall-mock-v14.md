# Wall Class Mock 测试模式 (v14)

> 外部服务 Mock 测试指南

## 概述

Wall Class 模式用于在测试中 Mock 外部服务（如支付网关、短信服务、第三方 API），使测试不依赖外部环境。

## 实际项目中的 Wall Class

### NoLogClient 示例

```php
// app/Common/Lib/BusinessWall/NoLogClient.class.php

namespace Common\Lib\BusinessWall;

/**
 * 无日志客户端 - 用于测试环境
 *
 * 不记录日志，返回模拟响应
 */
class NoLogClient
{
    protected $config;

    public function __construct(array $config = [])
    {
        $this->config = $config;
    }

    /**
     * 发送请求（模拟）
     */
    public function send(string $endpoint, array $data = []): array
    {
        // 返回模拟响应
        return [
            'success' => true,
            'data' => $this->getMockData($endpoint),
            'message' => 'Mock response',
        ];
    }

    /**
     * 获取模拟数据
     */
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

## 配置切换

### 环境配置

```php
// app/Common/Conf/config.php

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

## 测试用例示例

### 支付服务测试

```php
<?php
// lara/tests/Feature/PaymentTest.php

namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;
use Common\Lib\BusinessWall\NoLogClient;

class PaymentTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();

        // 强制使用 Mock 客户端
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

### 短信服务测试

```php
<?php
// lara/tests/Feature/SmsTest.php

namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;
use Common\Lib\BusinessWall\NoLogClient;

class SmsTest extends TestCase
{
    public function testSendSms(): void
    {
        // 在测试中直接使用 Mock
        $client = new NoLogClient();

        $result = $client->send('/api/sms/send', [
            'mobile' => '13800138000',
            'content' => '测试短信',
        ]);

        $this->assertTrue($result['success']);
        $this->assertArrayHasKey('message_id', $result['data']);
    }
}
```

## Wall Class 工厂模式

```php
<?php
// app/Common/Lib/BusinessWall/WallClientFactory.class.php

namespace Common\Lib\BusinessWall;

class WallClientFactory
{
    /**
     * 创建客户端实例
     */
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

## 接口定义

```php
<?php
// app/Common/Lib/BusinessWall/WallClientInterface.php

namespace Common\Lib\BusinessWall;

interface WallClientInterface
{
    /**
     * 发送请求
     */
    public function send(string $endpoint, array $data = []): array;

    /**
     * 获取客户端状态
     */
    public function getStatus(): string;
}
```

## 在业务代码中使用

```php
<?php
// app/Common/Lib/PaymentService.class.php

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

## 测试覆盖率

使用 Wall Class Mock 可以实现：

| 场景 | 覆盖情况 |
|------|---------|
| 正常响应 | ✅ Mock 返回成功 |
| 异常响应 | ✅ Mock 返回失败 |
| 超时场景 | ✅ Mock 模拟超时 |
| 边界值 | ✅ Mock 返回边界数据 |

## 最佳实践

1. **接口隔离**: 定义清晰的 WallClientInterface
2. **配置驱动**: 通过配置切换真实/Mock 客户端
3. **工厂模式**: 使用工厂创建客户端实例
4. **测试覆盖**: Mock 应覆盖所有业务场景
5. **文档同步**: Mock 返回值应与真实 API 文档一致

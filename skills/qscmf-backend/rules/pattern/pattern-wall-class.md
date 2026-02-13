# Wall Class Pattern (External API Integration)

## Purpose

Isolate external API calls behind a "Wall" class for:
- Clean error handling
- Easy mocking in tests
- Retry logic
- Rate limiting

## Architecture

```
Controller
    ↓
  Wall Class (facade)
    ↓
  External API (HTTP client)
```

## Wall Class Structure

```php
namespace Common\Wall;
use Gy_Library\GyLib;

/**
 * External Service Wall
 * Facade for all external API calls
 */
class ExternalServiceWall
{
    protected $baseUrl;
    protected $apiKey;
    protected $timeout = 30;
    protected $maxRetries = 3;

    public function __construct()
    {
        $this->baseUrl = C('EXTERNAL_SERVICE_URL');
        $this->apiKey = C('EXTERNAL_SERVICE_API_KEY');
    }

    /**
     * Fetch data from external API
     */
    public function fetchData(string $id): ?array
    {
        $url = $this->baseUrl . '/api/data/' . $id;

        for ($attempt = 1; $attempt <= $this->maxRetries; $attempt++) {
            try {
                $response = $this->httpGet($url, [
                    'Authorization' => 'Bearer ' . $this->apiKey
                ]);

                if ($response['status'] == 200) {
                    return $response['data'];
                }

                if ($response['status'] == 404) {
                    return null;
                }

                // Retry on server errors
                if ($response['status'] >= 500 && $attempt < $this->maxRetries) {
                    sleep(2 ** $attempt); // Exponential backoff
                    continue;
                }

                $this->logError('fetchData', $response);
                return null;

            } catch (\Exception $e) {
                if ($attempt == $this->maxRetries) {
                    $this->logError('fetchData', ['error' => $e->getMessage()]);
                    return null;
                }
                sleep(2 ** $attempt);
            }
        }

        return null;
    }

    /**
     * Send data to external API
     */
    public function sendData(array $data): bool
    {
        $url = $this->baseUrl . '/api/data';

        try {
            $response = $this->httpPost($url, $data, [
                'Authorization' => 'Bearer ' . $this->apiKey,
                'Content-Type' => 'application/json'
            ]);

            return $response['status'] == 200 || $response['status'] == 201;

        } catch (\Exception $e) {
            $this->logError('sendData', ['error' => $e->getMessage()]);
            return false;
        }
    }

    /**
     * HTTP GET request
     */
    protected function httpGet(string $url, array $headers = []): array
    {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $this->buildHeaders($headers));

        $response = curl_exec($ch);
        $statusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        return [
            'status' => $statusCode,
            'data' => json_decode($response, true)
        ];
    }

    /**
     * HTTP POST request
     */
    protected function httpPost(string $url, array $data, array $headers = []): array
    {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $this->buildHeaders($headers));

        $response = curl_exec($ch);
        $statusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        return [
            'status' => $statusCode,
            'data' => json_decode($response, true)
        ];
    }

    /**
     * Build headers array
     */
    protected function buildHeaders(array $headers): array
    {
        $built = [];
        foreach ($headers as $key => $value) {
            $built[] = "$key: $value";
        }
        return $built;
    }

    /**
     * Log error
     */
    protected function logError(string $action, array $context): void
    {
        \Think\Log::record(
            "ExternalServiceWall::{$action} failed: " . json_encode($context),
            'error'
        );
    }
}
```

## Use in Controller

```php
namespace Admin\Controller;
use Admin\Controller\QsListController;
use Common\Wall\ExternalServiceWall;

class ProductController extends QsListController
{
    /**
     * Sync product with external service
     */
    public function syncWithExternal()
    {
        $id = I('get.id', 0, 'intval');
        $product = D('Product')->find($id);

        if (!$product) {
            $this->error('产品不存在');
        }

        $wall = new ExternalServiceWall();
        $externalData = $wall->fetchData($product['external_id']);

        if (!$externalData) {
            $this->error('同步失败，无法获取外部数据');
        }

        // Update local data
        D('Product')->where(['id' => $id])->save([
            'name' => $externalData['name'],
            'price' => $externalData['price'],
            'synced_at' => time()
        ]);

        $this->success('同步成功');
    }
}
```

## Mock in Tests

```php
namespace Tests\Feature;
use Tests\TestCase;
use Common\Wall\ExternalServiceWall;

class ProductTest extends TestCase
{
    public function testSyncWithExternal()
    {
        // Mock the wall class
        $mockWall = $this->createMock(ExternalServiceWall::class);
        $mockWall->method('fetchData')
            ->willReturn([
                'name' => 'External Product',
                'price' => 100.00
            ]);

        // Inject mock
        $this->app->instance(ExternalServiceWall::class, $mockWall);

        // Test sync logic
        $controller = new \Admin\Controller\ProductController();
        $result = $controller->syncWithExternal();

        $this->assertTrue($result);
    }
}
```

→ [Testing Guide](references/testing.md)
→ [API Controllers Guide](references/api-controllers.md)

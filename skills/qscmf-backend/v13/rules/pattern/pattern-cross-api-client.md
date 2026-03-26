---
title: CrossApi Client Pattern (v13)
impact: HIGH
impactDescription: Standard pattern for cross-system API calls between QSCMF projects
tags: pattern, cross-api, http, guzzle, factory, v13
---

## CrossApi Client Pattern (v13)

Standard pattern for making cross-system API calls from one QSCMF project to another.

### When to Use This Rule

- Calling another QSCMF system's API (e.g., usercenter → reading_2)
- Replacing direct GuzzleHttp usage with structured client
- Need consistent Authorization header and response parsing

---

## Architecture Overview

```
Caller System                    Target System
┌─────────────────┐              ┌─────────────────────────────┐
│ CrossApiClient  │──HTTP──────▶│ QscmfCrossApi\RestController │
│ Factory         │              │ (framework standard)         │
└─────────────────┘              └─────────────────────────────┘

Request:  Authorization header + JSON body
Response: { status: 1|0, info: "message", data: {} }
```

---

## File Structure

```
app/Common/Lib/CrossApi/
├── CrossApiException.php         # Exception class
├── CrossApiClient.php            # Abstract base class
├── CrossApiClientFactory.php     # Factory
└── Client/
    └── PlatformClient.php        # Platform-specific client
```

---

## 1. Exception Class

```php
<?php
namespace Common\Lib\CrossApi;

/**
 * Cross-system API exception
 */
class CrossApiException extends \Exception
{
    protected ?int $httpStatusCode;
    protected ?array $responseData;

    public function __construct(
        string $message = "",
        int $httpStatusCode = null,
        array $responseData = null,
        int $code = 0,
        \Throwable $previous = null
    ) {
        parent::__construct($message, $code, $previous);
        $this->httpStatusCode = $httpStatusCode;
        $this->responseData = $responseData;
    }

    public function getHttpStatusCode(): ?int
    {
        return $this->httpStatusCode;
    }

    public function getResponseData(): ?array
    {
        return $this->responseData;
    }
}
```

---

## 2. Abstract Base Client

```php
<?php
namespace Common\Lib\CrossApi;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;

/**
 * Cross-system API client abstract base class
 */
abstract class CrossApiClient
{
    protected string $baseUri;
    protected string $authorization;
    protected int $timeout = 10;
    protected Client $httpClient;

    public function __construct()
    {
        $this->httpClient = new Client([
            'timeout' => $this->timeout,
        ]);
    }

    /**
     * GET request
     */
    public function get(string $urlOrPath, array $params = []): array
    {
        $url = $this->resolveUrl($urlOrPath);
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }
        return $this->request('GET', $url);
    }

    /**
     * POST request
     */
    public function post(string $urlOrPath, array $data = []): array
    {
        return $this->request('POST', $this->resolveUrl($urlOrPath), $data);
    }

    /**
     * PUT request
     */
    public function put(string $urlOrPath, array $data = []): array
    {
        return $this->request('PUT', $this->resolveUrl($urlOrPath), $data);
    }

    /**
     * DELETE request
     */
    public function delete(string $urlOrPath): array
    {
        return $this->request('DELETE', $this->resolveUrl($urlOrPath));
    }

    /**
     * Smart URL resolution
     * - Full URL (http/https): use as-is
     * - Relative path: prepend baseUri
     */
    protected function resolveUrl(string $urlOrPath): string
    {
        if (str_starts_with($urlOrPath, 'http')) {
            return $urlOrPath;
        }
        return rtrim($this->baseUri, '/') . '/' . ltrim($urlOrPath, '/');
    }

    /**
     * Core request method
     */
    protected function request(string $method, string $url, array $data = []): array
    {
        try {
            $options = [
                'headers' => [
                    'Authorization' => $this->authorization,
                    'Content-Type' => 'application/json',
                    'Accept' => 'application/json',
                ],
            ];

            if (!empty($data) && in_array($method, ['POST', 'PUT', 'PATCH'])) {
                $options['json'] = $data;
            }

            $response = $this->httpClient->request($method, $url, $options);

            return $this->parseResponse(
                $response->getStatusCode(),
                $response->getBody()->getContents()
            );
        } catch (RequestException $e) {
            $response = $e->getResponse();
            $statusCode = $response ? $response->getStatusCode() : 0;
            $body = $response ? $response->getBody()->getContents() : '';

            throw new CrossApiException(
                "HTTP request failed: {$e->getMessage()}",
                $statusCode,
                json_decode($body, true) ?: [],
                0,
                $e
            );
        }
    }

    /**
     * Parse QSCMF standard response: {status, info, data}
     */
    protected function parseResponse(int $statusCode, string $body): array
    {
        $data = json_decode($body, true);

        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new CrossApiException(
                "Invalid JSON response: " . json_last_error_msg(),
                $statusCode,
                ['raw' => $body]
            );
        }

        // Check business status
        if (isset($data['status']) && $data['status'] != 1) {
            throw new CrossApiException(
                $data['info'] ?? 'Unknown error',
                $statusCode,
                $data
            );
        }

        return $data;
    }
}
```

---

## 3. Platform-Specific Client

```php
<?php
namespace Common\Lib\CrossApi\Client;

use Common\Lib\CrossApi\CrossApiClient;

class PlatformClient extends CrossApiClient
{
    protected string $baseUri;
    protected string $authorization;

    public function __construct()
    {
        $this->baseUri = env('PLATFORM_API_URL', '');
        $this->authorization = env('PLATFORM_API_TOKEN', '');

        if (empty($this->baseUri)) {
            throw new \InvalidArgumentException('PLATFORM_API_URL not configured');
        }

        if (empty($this->authorization)) {
            throw new \InvalidArgumentException('PLATFORM_API_TOKEN not configured');
        }
    }
}
```

---

## 4. Factory Class

```php
<?php
namespace Common\Lib\CrossApi;

use Common\Lib\CrossApi\Client\PlatformClient;
use InvalidArgumentException;

class CrossApiClientFactory
{
    /**
     * Platform to client class mapping
     */
    protected static array $mapping = [
        'platform_a' => PlatformClient::class,
        // 'platform_b' => PlatformBClient::class,  // Future extension
    ];

    /**
     * Create client instance by platform identifier
     */
    public static function create(string $platform): CrossApiClient
    {
        if (!isset(self::$mapping[$platform])) {
            throw new InvalidArgumentException("Unknown platform: {$platform}");
        }

        $clientClass = self::$mapping[$platform];
        return new $clientClass();
    }

    /**
     * Register new platform client
     */
    public static function register(string $platform, string $clientClass): void
    {
        self::$mapping[$platform] = $clientClass;
    }

    /**
     * Get all registered platforms
     */
    public static function getRegisteredPlatforms(): array
    {
        return array_keys(self::$mapping);
    }
}
```

---

## 5. Usage in Business Logic

```php
<?php
namespace Common\Lib\Service;

use Common\Lib\CrossApi\CrossApiClientFactory;
use Common\Lib\CrossApi\CrossApiException;

class NotificationService
{
    /**
     * Send callback to external system
     */
    protected function sendCallback(string $platform, string $url, array $data): bool
    {
        try {
            $client = CrossApiClientFactory::create($platform);
            $client->post($url, $data);

            \Think\Log::write("Callback success: platform={$platform}, url={$url}");

            return true;
        } catch (CrossApiException $e) {
            \Think\Log::write("Callback failed: platform={$platform}, url={$url}, error: " . $e->getMessage());
            return false;
        } catch (\InvalidArgumentException $e) {
            \Think\Log::write("Platform not configured: platform={$platform}, error: " . $e->getMessage());
            return false;
        } catch (\Exception $e) {
            \Think\Log::write("Callback error: platform={$platform}, url={$url}, error: " . $e->getMessage());
            return false;
        }
    }
}
```

---

## Environment Configuration

Add to `.env.example`:

```env
# Platform A API
PLATFORM_A_API_URL=https://platform-a.example.com
PLATFORM_A_API_TOKEN=your-token-here

# Platform B API
PLATFORM_B_API_URL=https://platform-b.example.com
PLATFORM_B_API_TOKEN=your-token-here
```

---

## Benefits

1. **Consistency** - All cross-system calls use the same pattern
2. **Testability** - Easy to mock clients in tests
3. **Extensibility** - Add new platforms by creating new client classes
4. **Error Handling** - Unified exception handling with context
5. **Maintainability** - Configuration centralized in `.env`

---

## Related Rules

- [API Response Format](../api/api-response-format.md) - Standard `{status, info, data}` format
- [API Documentation](../api/api-documentation.md) - OpenAPI documentation for APIs
- [Pattern Abstract Base](pattern-abstract-base.md) - Abstract base pattern for controllers/models

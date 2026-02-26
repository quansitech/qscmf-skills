---
title: API Authentication JWT (v14)
impact: HIGH
impactDescription: Required for protected API endpoints
tags: api, auth, jwt, v14, php82
---

## API Authentication JWT (v14)

JWT authentication for QSCMF v14 API endpoints with PHP 8.2+ modern patterns.

### When to Use This Rule

- Securing API endpoints
- Implementing user authentication
- Managing API access tokens
- Building stateless authentication systems

---

## JWT Configuration

Configuration in `lara/config/jwt.php`:

```php
<?php

return [
    'secret' => env('JWT_SECRET'),
    'algorithm' => env('JWT_ALGORITHM', 'HS256'),
    'ttl' => (int)env('JWT_TTL', 3600),           // 1 hour
    'refresh_ttl' => (int)env('JWT_REFRESH_TTL', 604800), // 7 days
    'issuer' => env('APP_URL', 'http://localhost'),
];
```

Environment variables in `.env`:

```env
JWT_SECRET=your-very-secure-secret-key-here
JWT_ALGORITHM=HS256
JWT_TTL=3600
JWT_REFRESH_TTL=604800
```

---

## Token Generation

### Login Endpoint

```php
<?php
namespace Api\Controller;

use Firebase\JWT\JWT;
use Firebase\JWT\Key;

class AuthController extends RestController
{
    protected $noAuthorization = ['login', 'register', 'refresh'];

    public function login_post(): void
    {
        $username = I('post.username');
        $password = I('post.password');

        if (empty($username) || empty($password)) {
            $this->response([
                'status' => false,
                'msg' => '用户名和密码不能为空',
            ], 422);
            return;
        }

        $user = D('User')->where(['username' => $username])->find();

        if (!$user || !password_verify($password, $user['password'])) {
            $this->response([
                'status' => false,
                'msg' => '用户名或密码错误',
            ], 401);
            return;
        }

        if ($user['status'] !== DBCont::NORMAL_STATUS) {
            $this->response([
                'status' => false,
                'msg' => '账号已被禁用',
            ], 403);
            return;
        }

        $token = $this->generateToken($user);
        $refreshToken = $this->generateRefreshToken($user);

        $this->response([
            'status' => true,
            'data' => [
                'token' => $token,
                'refresh_token' => $refreshToken,
                'expires_in' => config('jwt.ttl'),
                'token_type' => 'Bearer',
            ],
            'user' => [
                'id' => (int)$user['id'],
                'username' => $user['username'],
                'nickname' => $user['nickname'],
                'avatar' => $user['avatar'] ?? null,
            ],
        ]);
    }

    private function generateToken(array $user): string
    {
        $payload = [
            'iss' => config('jwt.issuer'),
            'iat' => time(),
            'exp' => time() + config('jwt.ttl'),
            'uid' => (int)$user['id'],
            'type' => 'access',
        ];

        return JWT::encode($payload, config('jwt.secret'), config('jwt.algorithm'));
    }

    private function generateRefreshToken(array $user): string
    {
        $payload = [
            'iss' => config('jwt.issuer'),
            'iat' => time(),
            'exp' => time() + config('jwt.refresh_ttl'),
            'uid' => (int)$user['id'],
            'type' => 'refresh',
        ];

        return JWT::encode($payload, config('jwt.secret'), config('jwt.algorithm'));
    }
}
```

---

## Token Verification

### Middleware Pattern

```php
<?php
namespace Api\Middleware;

use Firebase\JWT\JWT;
use Firebase\JWT\Key;
use Closure;

class JwtMiddleware
{
    public function handle(object $request, Closure $next): mixed
    {
        $token = $this->extractToken();

        if (!$token) {
            return response()->json([
                'status' => false,
                'msg' => 'Token 未提供',
            ], 401);
        }

        try {
            $decoded = JWT::decode($token, new Key(config('jwt.secret'), config('jwt.algorithm')));

            if ($decoded->type !== 'access') {
                return response()->json([
                    'status' => false,
                    'msg' => '无效的 Token 类型',
                ], 401);
            }

            // Store user in request
            $request->userId = $decoded->uid;

        } catch (\Firebase\JWT\ExpiredException $e) {
            return response()->json([
                'status' => false,
                'msg' => 'Token 已过期',
                'error_code' => 'TOKEN_EXPIRED',
            ], 401);
        } catch (\Firebase\JWT\SignatureInvalidException $e) {
            return response()->json([
                'status' => false,
                'msg' => 'Token 签名无效',
            ], 401);
        } catch (\Exception $e) {
            return response()->json([
                'status' => false,
                'msg' => 'Token 无效',
            ], 401);
        }

        return $next($request);
    }

    private function extractToken(): ?string
    {
        $authorization = I('server.HTTP_AUTHORIZATION');

        if (!$authorization || !str_starts_with($authorization, 'Bearer ')) {
            return null;
        }

        return substr($authorization, 7);
    }
}
```

### Controller Integration

```php
<?php
namespace Api\Controller;

class RestController extends BaseController
{
    protected ?array $currentUser = null;
    protected array $noAuthorization = [];

    public function __construct()
    {
        parent::__construct();

        $action = strtolower(ACTION_NAME);

        if (!in_array($action, $this->noAuthorization, true)) {
            $this->authenticate();
        }
    }

    protected function authenticate(): void
    {
        $token = $this->extractToken();

        if (!$token) {
            $this->response([
                'status' => false,
                'msg' => '请先登录',
            ], 401);
            exit;
        }

        try {
            $decoded = \Firebase\JWT\JWT::decode(
                $token,
                new \Firebase\JWT\Key(config('jwt.secret'), config('jwt.algorithm'))
            );

            $this->currentUser = D('User')->find($decoded->uid);

            if (!$this->currentUser || $this->currentUser['status'] !== DBCont::NORMAL_STATUS) {
                $this->response([
                    'status' => false,
                    'msg' => '用户不存在或已被禁用',
                ], 401);
                exit;
            }

        } catch (\Exception $e) {
            $this->response([
                'status' => false,
                'msg' => 'Token 无效或已过期',
                'error_code' => 'TOKEN_INVALID',
            ], 401);
            exit;
        }
    }

    protected function extractToken(): ?string
    {
        $authorization = I('server.HTTP_AUTHORIZATION');

        if (!$authorization || !str_starts_with($authorization, 'Bearer ')) {
            return null;
        }

        return substr($authorization, 7);
    }

    protected function getCurrentUser(): ?array
    {
        return $this->currentUser;
    }

    protected function getCurrentUserId(): ?int
    {
        return $this->currentUser['id'] ?? null;
    }
}
```

---

## Token Refresh

```php
<?php
namespace Api\Controller;

class AuthController extends RestController
{
    protected $noAuthorization = ['login', 'register', 'refresh'];

    public function refresh_post(): void
    {
        $refreshToken = I('post.refresh_token');

        if (empty($refreshToken)) {
            $this->response([
                'status' => false,
                'msg' => 'Refresh token 未提供',
            ], 422);
            return;
        }

        try {
            $decoded = \Firebase\JWT\JWT::decode(
                $refreshToken,
                new \Firebase\JWT\Key(config('jwt.secret'), config('jwt.algorithm'))
            );

            if ($decoded->type !== 'refresh') {
                $this->response([
                    'status' => false,
                    'msg' => '无效的 Token 类型',
                ], 401);
                return;
            }

            $user = D('User')->find($decoded->uid);

            if (!$user || $user['status'] !== DBCont::NORMAL_STATUS) {
                $this->response([
                    'status' => false,
                    'msg' => '用户不存在或已被禁用',
                ], 401);
                return;
            }

            $newToken = $this->generateToken($user);

            $this->response([
                'status' => true,
                'data' => [
                    'token' => $newToken,
                    'expires_in' => config('jwt.ttl'),
                    'token_type' => 'Bearer',
                ],
            ]);

        } catch (\Firebase\JWT\ExpiredException $e) {
            $this->response([
                'status' => false,
                'msg' => 'Refresh token 已过期，请重新登录',
                'error_code' => 'REFRESH_TOKEN_EXPIRED',
            ], 401);
        } catch (\Exception $e) {
            $this->response([
                'status' => false,
                'msg' => 'Refresh token 无效',
            ], 401);
        }
    }
}
```

---

## Logout

```php
public function logout_post(): void
{
    // In v14, JWT is stateless so we just return success
    // For token blacklisting, use Redis

    $token = $this->extractToken();

    if ($token) {
        // Optional: Add token to blacklist
        $this->blacklistToken($token);
    }

    $this->response([
        'status' => true,
        'msg' => '登出成功',
    ]);
}

private function blacklistToken(string $token): void
{
    try {
        $decoded = \Firebase\JWT\JWT::decode(
            $token,
            new \Firebase\JWT\Key(config('jwt.secret'), config('jwt.algorithm'))
        );

        $ttl = $decoded->exp - time();

        if ($ttl > 0) {
            Redis::setex("jwt:blacklist:{$token}", $ttl, '1');
        }
    } catch (\Exception $e) {
        // Ignore errors during blacklisting
    }
}
```

---

## Authorization Patterns

### Public Endpoints

```php
class ProductController extends RestController
{
    // No authentication required for these actions
    protected $noAuthorization = ['gets', 'detail', 'search', 'categories'];
}
```

### Protected Endpoints

```php
class OrderController extends RestController
{
    // Only 'track' is public, all others require authentication
    protected $noAuthorization = ['track'];

    public function save_post(): void
    {
        $userId = $this->getCurrentUserId();

        // User is authenticated
        $orderData = I('post.');
        $orderData['user_id'] = $userId;

        $orderId = D('Order')->createAdd($orderData);

        $this->response([
            'status' => true,
            'data' => ['id' => $orderId],
            'msg' => '订单创建成功',
        ], 201);
    }
}
```

### Role-based Access

```php
class AdminController extends RestController
{
    protected $noAuthorization = [];

    public function dashboard_get(): void
    {
        $user = $this->getCurrentUser();

        if ($user['role_id'] !== ROLE_ADMIN) {
            $this->response([
                'status' => false,
                'msg' => '无权限访问',
            ], 403);
            return;
        }

        $stats = $this->getDashboardStats();

        $this->response([
            'status' => true,
            'data' => $stats,
        ]);
    }
}
```

### Resource Ownership

```php
public function detail_get(int $id): void
{
    $order = D('Order')->find($id);

    if (!$order) {
        $this->response([
            'status' => false,
            'msg' => '订单不存在',
        ], 404);
        return;
    }

    $userId = $this->getCurrentUserId();

    // Only allow access to own orders (unless admin)
    if ($order['user_id'] !== $userId && !$this->isAdmin()) {
        $this->response([
            'status' => false,
            'msg' => '无权限访问此订单',
        ], 403);
        return;
    }

    $this->response([
        'status' => true,
        'data' => $order,
    ]);
}

private function isAdmin(): bool
{
    $user = $this->getCurrentUser();
    return $user['role_id'] === ROLE_ADMIN;
}
```

---

## Client Usage

### Request with Token

```javascript
// Include token in Authorization header
const token = localStorage.getItem('token');

fetch('/api.php/Product/save', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name: 'Product Name' }),
});
```

### Token Refresh Handling

```javascript
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('token');

    const response = await fetch(url, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${token}`,
        },
    });

    if (response.status === 401) {
        const data = await response.json();

        if (data.error_code === 'TOKEN_EXPIRED') {
            // Try to refresh token
            const refreshed = await refreshToken();

            if (refreshed) {
                // Retry original request
                return fetchWithAuth(url, options);
            } else {
                // Redirect to login
                window.location.href = '/login';
            }
        }
    }

    return response;
}

async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');

    const response = await fetch('/api.php/Auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.data.token);
        return true;
    }

    return false;
}
```

---

## Best Practices

1. **Use HTTPS** - Always transmit tokens over secure connections
2. **Short access token TTL** - Set access token to 1 hour or less
3. **Refresh tokens** - Implement refresh mechanism for long sessions
4. **Token blacklisting** - Use Redis for logout/token revocation
5. **Secure storage** - Store tokens securely on client (httpOnly cookies preferred)
6. **Rate limiting** - Implement rate limiting on auth endpoints
7. **Input validation** - Always validate login credentials
8. **Logging** - Log authentication failures for security monitoring

---

## PHP 8.2+ Features

Use modern PHP features in v14:

```php
// Typed properties
protected ?array $currentUser = null;

// Match expressions
private function getAuthErrorCode(\Exception $e): string
{
    return match (true) {
        $e instanceof \Firebase\JWT\ExpiredException => 'TOKEN_EXPIRED',
        $e instanceof \Firebase\JWT\SignatureInvalidException => 'INVALID_SIGNATURE',
        default => 'TOKEN_INVALID',
    };
}

// Nullsafe operator
$userId = $this->currentUser?['id'];

// str_starts_with helper
if (str_starts_with($authorization, 'Bearer ')) {
    // ...
}
```

---

## Related Rules

- [API Response Format](api-response-format.md) - Standard response format
- [API Pagination](api-pagination-cursor.md) - Pagination strategies
- [API Controllers Reference](../../references/api-controllers.md) - Complete guide

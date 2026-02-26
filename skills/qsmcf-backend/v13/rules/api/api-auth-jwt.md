---
title: API Authentication JWT (v13)
impact: HIGH
impactDescription: Required for protected API endpoints
tags: api, auth, jwt, v13
---

## API Authentication JWT (v13)

JWT authentication for QSCMF v13 API endpoints.

### When to Use This Rule

- Securing API endpoints
- Implementing user authentication
- Managing API access tokens

---

## RestController Authentication

QSCMF RestController has built-in authentication:

```php
use Qscmf\Api\RestController;

class ProductController extends RestController
{
    // Endpoints that don't require authentication
    protected $noAuthorization = ['gets', 'detail', 'options'];

    // Endpoints requiring authentication
    // save, update, delete require auth by default
}
```

---

## JWT Configuration

Configuration in `lara/config/jwt.php`:

```php
return [
    'secret' => env('JWT_SECRET', 'your-secret-key'),
    'ttl' => 60 * 24,  // 24 hours
    'refresh_ttl' => 60 * 24 * 7,  // 7 days
];
```

---

## Token Generation

### Login Endpoint

```php
public function login(): Response
{
    $username = I('post.username');
    $password = I('post.password');

    if (empty($username) || empty($password)) {
        return new Response('用户名和密码不能为空', 0);
    }

    $user = D('User')->where(['username' => $username])->find();

    if (!$user || !password_verify($password, $user['password'])) {
        return new Response('用户名或密码错误', 0);
    }

    if ($user['status'] != DBCont::NORMAL_STATUS) {
        return new Response('账号已被禁用', 0);
    }

    // Generate JWT token
    $token = $this->generateToken($user);

    return new Response('登录成功', 1, [
        'token' => $token,
        'user' => [
            'id' => $user['id'],
            'username' => $user['username'],
            'nickname' => $user['nickname']
        ]
    ]);
}
```

---

## Token Verification

The framework automatically verifies tokens for protected endpoints.

### Manual Verification

```php
public function customAction(): Response
{
    // Get current user from token
    $user = $this->getCurrentUser();

    if (!$user) {
        return new Response('未授权', 0);
    }

    // Proceed with user context
    return new Response('成功', 1, ['user_id' => $user['id']]);
}
```

---

## Token Refresh

```php
public function refreshToken(): Response
{
    try {
        $new_token = $this->refreshJwtToken();
        return new Response('成功', 1, ['token' => $new_token]);
    } catch (\Exception $e) {
        return new Response('刷新失败', 0);
    }
}
```

---

## Authorization Patterns

### Public Endpoints

```php
// No authentication required
protected $noAuthorization = ['gets', 'detail', 'login', 'register'];
```

### Protected Endpoints

```php
// All methods require authentication except those in $noAuthorization
class OrderController extends RestController
{
    protected $noAuthorization = ['tracks'];  // Only tracks is public

    // gets, save, update, delete require auth
}
```

### Role-based Access

```php
public function adminOnly(): Response
{
    $user = $this->getCurrentUser();

    if ($user['role_id'] != ROLE_ADMIN) {
        return new Response('无权限', 0);
    }

    // Admin logic
    return new Response('成功', 1);
}
```

---

## Client Usage

### Request with Token

```javascript
// Include token in header
fetch('/api.php/Product/save', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

### Token Storage

```javascript
// Store token after login
localStorage.setItem('token', response.data.token);

// Get token for requests
const token = localStorage.getItem('token');
```

---

## Best Practices

1. **Use HTTPS** - Always transmit tokens over secure connections
2. **Short expiration** - Set reasonable token TTL
3. **Refresh tokens** - Implement refresh mechanism for long sessions
4. **Logout handling** - Clear token on client logout

---

## Related Rules

- [API Response Format](api-response-format.md) - Standard response format
- [API Pagination](api-pagination-cursor.md) - Pagination strategies
- [API Controllers Reference](../../references/api-controllers.md) - Complete guide

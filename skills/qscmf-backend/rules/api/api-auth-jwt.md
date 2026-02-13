# API Authentication (JWT)

## Enable JWT Authentication

In your RestController:

```php
namespace Api\Controller;
use Qscmf\Api\RestController;

class {{MODEL}}Controller extends RestController
{
    protected $modelName = '{{MODEL_NAME}}';

    // Endpoints that don't require authentication
    protected $noAuthorization = ['login', 'register', 'gets', 'detail'];

    // Enable JWT
    protected $useAuth = true;
}
```

## Login Endpoint

```php
/**
 * User login
 *
 * POST /api.php/User/login
 * Body: username, password
 */
public function login(): Response
{
    $username = I('post.username');
    $password = I('post.password');

    if (!$username || !$password) {
        return new Response('参数错误', 0);
    }

    $user = D('User')->where([
        'username' => $username
    ])->find();

    if (!$user) {
        return new Response('用户不存在', 0);
    }

    if ($user['password'] !== md5($password . $user['salt'])) {
        return new Response('密码错误', 0);
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

/**
 * Generate JWT token
 */
protected function generateToken(array $user): string
{
    $payload = [
        'iss' => 'qscmf',           // Issuer
        'iat' => time(),             // Issued at
        'exp' => time() + 7200,      // Expire in 2 hours
        'uid' => $user['id']
    ];

    // Use firebase/php-jwt or custom implementation
    return \Firebase\JWT\JWT::encode(
        $payload,
        C('JWT_SECRET'),
        'HS256'
    );
}
```

## Get Current User

```php
/**
 * Get current authenticated user
 */
protected function getCurrentUser(): ?array
{
    $token = $this->getBearerToken();

    if (!$token) {
        return null;
    }

    try {
        $decoded = \Firebase\JWT\JWT::decode(
            $token,
            new \Firebase\JWT\Key(C('JWT_SECRET'), 'HS256')
        );

        return D('User')->find($decoded->uid);
    } catch (\Exception $e) {
        return null;
    }
}

protected function getBearerToken(): ?string
{
    $headers = getallheaders();
    $auth = $headers['Authorization'] ?? '';

    if (preg_match('/Bearer\s+(.*)$/i', $auth, $matches)) {
        return $matches[1];
    }

    return null;
}
```

## Refresh Token

```php
/**
 * Refresh token
 *
 * POST /api.php/User/refresh
 * Header: Authorization: Bearer {token}
 */
public function refresh(): Response
{
    $user = $this->getCurrentUser();

    if (!$user) {
        return new Response('认证失败', 0);
    }

    $newToken = $this->generateToken($user);

    return new Response('刷新成功', 1, [
        'token' => $newToken
    ]);
}
```

→ [API Controllers Guide](references/api-controllers.md)

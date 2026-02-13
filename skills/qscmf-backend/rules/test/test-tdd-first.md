---
title: TDD First - Write Tests Before Implementation
impact: HIGH
impactDescription: Ensures code quality and prevents bugs
tags: test, tdd, phpunit, both
---

## TDD First - Write Tests Before Implementation

**Impact: HIGH (Critical for code quality)**

Always write failing tests before writing implementation code.

**Incorrect (先写代码，后写测试):**
```php
// 1. 先写实现
class UserModel {
    public function getUserByEmail(string $email) {
        return $this->where(['email' => $email])->find();
    }
}

// 2. 后写测试（可能遗漏边界情况）
public function testGetUserByEmail() {
    $user = D('User')->getUserByEmail('test@example.com');
    $this->assertNotEmpty($user);
}
```

**Correct (先写测试，驱动开发):**
```php
// 1. 先写测试（包含边界情况）
public function testGetUserByEmail_Success(): void {
    $email = 'test@example.com';

    D('User')->add(['email' => $email, 'nick_name' => 'Test']);

    $user = D('User')->getUserByEmail($email);

    $this->assertNotEmpty($user);
    $this->assertEquals($email, $user['email']);
}

public function testGetUserByEmail_NotFound(): void {
    $user = D('User')->getUserByEmail('notfound@example.com');

    $this->assertEmpty($user);
}

// 2. 运行测试（确认失败）
// vendor/bin/phpunit tests/Feature/UserTest.php
// Output: FAIL

// 3. 实现代码使测试通过
class UserModel extends GyListModel {
    public function getUserByEmail(string $email): ?array
    {
        return $this->where(['email' => $email])->find();
    }
}

// 4. 再次运行测试（确认通过）
```

**Red-Green-Refactor Cycle:**
```
1. RED: Write failing test
2. GREEN: Write minimum code to pass
3. REFACTOR: Improve code while tests pass
```

**Test File Location:**
```
lara/tests/Feature/{Module}Test.php
```

**Test Template:**
```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;

class ProductTest extends TestCase
{
    public function testCreateProduct(): void
    {
        $data = ['name' => 'Test Product', 'price' => 99.99];

        $id = D('Product')->add($data);

        $this->assertTrue($id > 0);
        $this->assertEquals($data['name'], D('Product')->getField('name', $id));
    }
}
```

**See Also:**
- [Wall Class Mocking](../test/test-wall-mock.md)
- [Test Transaction](../test/test-transaction.md)
- [PHPUnit Guide](../../references/testing.md)

**Iron Law (from superpowers:test-driven-development):**
```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
RED-GREEN-REFACTOR CYCLE
```

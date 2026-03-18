# Testing

> PHPUnit testing guide for QSCMF v14.

## 通用测试命令

> **重要**: 关闭 xdebug 以加速测试。详见 [Testing Common Commands](_shared/references/testing-common.md)

```bash
# 定义基础命令
PHPUNIT="php -d display_errors=on -d xdebug.mode=off -d xdebug.start_with_request=0 vendor/bin/phpunit"

# 运行测试
$PHPUNIT                                    # 全部测试
$PHPUNIT lara/tests/Feature/ProductTest.php # 单个测试类
$PHPUNIT --filter "testMethodName"          # 单个测试方法
```

## Test Structure

```php
<?php
namespace Tests\Feature;

use Tests\TestCase;
use Gy_Library\DBCont;

class ProductTest extends TestCase
{
    public function test_index_returns_list(): void
    {
        $response = $this->get('/api/product');

        $response->assertStatus(200)
            ->assertJsonStructure(['status', 'data']);
    }
}
```

## Assertions

```php
$response->assertStatus(200);
$response->assertJson(['status' => true]);
$response->assertJsonStructure(['data' => ['id', 'name']]);
$this->assertDatabaseHas('product', ['id' => 1]);
```

---

## Related Documentation
- [Testing Common Commands](_shared/references/testing-common.md) - 通用测试命令
- [TDD First](../rules/test/test-tdd-first.md)
- [Wall Mock](../rules/test/test-wall-mock.md)

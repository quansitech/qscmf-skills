# Development Standards Reference

> QSCMF 开发规范与测试指南

## PHP 8.2 Coding Standards

### Type Declarations

```php
// ✅ 方法声明类型
public function getUserById(int $id): ?array
{
    return $this->where(['id' => $id])->find();
}

// ✅ 参数类型
public function save(array $data, bool $isNew = false): bool
{
    // ...
}

// ❌ 避免混合类型返回
public function getData()  // 避免：可能返回 array 或 false
{
    return $this->find() ?: [];
}
```

### Strict Comparisons

```php
// ✅ 严格比较
if ($status === DBCont::NORMAL_STATUS) { }
if ($result !== false) { }

// ❌ 避免松散比较
if ($status == 1) { }
if ($result) { }
```

### Modern PHP Features

```php
// ✅ 箭头函数
$ids = array_map(fn($item) => (int)$item['id'], $list);
$names = array_map(fn($item) => $item['name'], $list);

// ✅ Match 表达式
$type = match($field) {
    'content' => 'ueditor',
    'status' => 'select',
    'cover' => 'image',
    default => 'text'
};

// ✅ Null 合并运算符
$name = $data['name'] ?? 'Default';
$user = $user ?? null;

// ✅ 命名参数
DB::table('demo')->insert([
    'name' => 'Test',
    'status' => 1,
]);
```

### Naming Conventions

```php
// 类名：PascalCase
class ProductController {}

// 方法名：camelCase
public function getUserList() {}

// 常量：UPPER_SNAKE_CASE
const MAX_COUNT = 100;

// 变量：camelCase
$userList = [];
$userId = 1;

// 数据库字段：snake_case
// user_id, create_time, is_enabled
```

## React/TypeScript Standards

### Component Structure

```tsx
interface Props {
  title: string;
  onSave: (data: FormData) => void;
}

export function ProductForm({ title, onSave }: Props) {
  const [form] = Form.useForm();

  const handleSubmit = async (values: FormData) => {
    try {
      await onSave(values);
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    }
  };

  return (
    <Form form={form} onFinish={handleSubmit}>
      {/* ... */}
    </Form>
  );
}
```

### Type Definitions

```typescript
// 接口类型
interface Product {
  id: number;
  title: string;
  status: 0 | 1;
  createdAt: string;
}

// 枚举类型
enum Status {
  Disabled = 0,
  Enabled = 1,
}

// 泛型
interface ApiResponse<T> {
  status: number;
  message: string;
  data: T;
}
```

## Caching & Locking

### Redis Cache

```php
use Qscmf\Lib\Cache\QscmfCache;

// 简单缓存
$cache = new QscmfCache('key', 3600);
$data = $cache->remember(function() {
    return expensiveOperation();
});

// 标签缓存
$cache = new QscmfCache('key', 3600, 'demo_tag');
$cache->clear();  // 清除所有 demo_tag 标签的缓存

// 永久缓存
$cache = new QscmfCache('key', 0);
```

### Redis Lock

```php
use Qscmf\Lib\Redis\RedisLock;

$lock = new RedisLock('lock_key', 10);

if (!$lock->acquire()) {
    $this->error('操作进行中');
}

try {
    // 执行业务逻辑
    process();
} finally {
    $lock->release();
}
```

### Cache Invalidation

```php
// 保存后清除相关缓存
public function save()
{
    $result = parent::save();

    if ($result->status) {
        // 清除列表缓存
        QscmfCache::clearByTag('demo_list');

        // 清除特定缓存
        $cache = new QscmfCache('demo_' . $this->save_id);
        $cache->clear();
    }

    return $result;
}
```

## Unit Testing Guide

### PHPUnit Test Structure

```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;

class DemoTest extends TestCase
{
    public function testGetList(): void
    {
        $response = $this->get('/api.php/Demo/gets');

        $response->assertStatus(200)
            ->assertJson(['status' => 1])
            ->assertJsonStructure([
                'data' => ['list', 'total']
            ]);
    }
}
```

### Testing with Mocks

```php
use App\Services\ApiService;

public function testWithMock(): void
{
    // 创建 Mock
    $mock = $this->createMock(ApiService::class);

    // 设置期望
    $mock->method('fetch')
        ->willReturn(['success' => true]);

    // 注入到容器
    app()->instance(ApiService::class, $mock);

    // 执行测试
    $result = D('Demo')->syncWithExternal();
    $this->assertTrue($result);
}
```

### Testing with ThinkPHP Context

```php
public function testTpModel(): void
{
    $result = $this->runTp(function() {
        return D('Demo')->find(1);
    });

    $this->assertIsArray($result);
}
```

## Mock Third-Party APIs

### Wall Class Pattern

```php
<?php
namespace Common\Lib\Wall;
use Common\Lib\Wall\Gateway\IGateway;

/**
 * Wall class for external API isolation
 */
class ExternalApi implements IGateway
{
    public function fetch($params)
    {
        // 生产环境：调用真实 API
        if (config('app.env') === 'production') {
            return RealApiClient::call($params);
        }

        // 测试环境：返回模拟数据
        return [
            'success' => true,
            'data' => []
        ];
    }
}
```

### Using Wall in Code

```php
use Common\Lib\Wall\ExternalApi;

class DemoModel extends GyListModel
{
    public function syncWithExternal()
    {
        $api = new ExternalApi();
        $result = $api->fetch(['id' => $this->id]);

        if ($result['success']) {
            // 处理数据
            return true;
        }

        return false;
    }
}
```

### Testing Wall Class

```php
public function testExternalApi()
{
    $mock = $this->createMock(ExternalApi::class);
    $mock->method('fetch')->willReturn([
        'success' => true,
        'data' => ['id' => 1, 'name' => 'Test']
    ]);

    app()->instance(ExternalApi::class, $mock);

    $result = D('Demo')->syncWithExternal();
    $this->assertTrue($result);
}
```

## Code Review Checklist

### Functionality
- [ ] 功能符合需求
- [ ] 边界条件处理
- [ ] 错误处理完善
- [ ] 日志记录充分

### Performance
- [ ] 避免N+1查询
- [ ] 使用索引字段查询
- [ ] 大数据分页处理
- [ ] 合理使用缓存

### Security
- [ ] 输入验证
- [ ] SQL注入防护
- [ ] XSS防护
- [ ] 权限检查

### Code Quality
- [ ] 遵循PSR标准
- [ ] 类型声明完整
- [ ] 命名清晰
- [ ] 注释充分

### Testing
- [ ] 单元测试覆盖
- [ ] Mock外部依赖
- [ ] 边界测试
- [ ] 集成测试

---

**相关文档**：
- [Admin Controllers](admin-controllers.md)
- [CRUD Patterns](crud-patterns.md)

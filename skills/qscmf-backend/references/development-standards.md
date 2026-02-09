# Development Standards Reference

> QSCMF 开发规范与测试指南

## 概述

本文档定义 QSCMF 项目的开发规范，包括 PHP 8.2 代码标准、React/TypeScript 前端规范、测试最佳实践等。

## PHP 8.2 编码规范

### 类型声明

```php
// ✅ 方法返回类型声明
public function getUserById(int $id): ?array
{
    return $this->where(['id' => $id])->find();
}

// ✅ 参数类型声明
public function saveData(array $data, bool $isNew = false): bool
{
    // 实现逻辑
}

// ✅ 可空类型
public function getCategory(?int $id): ?array
{
    return $id ? $this->find($id) : null;
}

// ❌ 避免混合类型返回
public function getData()  // 避免：可能返回 array 或 false
{
    return $this->find() ?: [];
}
```

### 严格比较

```php
// ✅ 使用严格比较
if ($status === DBCont::NORMAL_STATUS) { }
if ($result !== false) { }

// ✅ 使用类型转换后比较
$statusCode = (int)$response['code'];
if ($statusCode === 200) { }

// ❌ 避免松散比较
if ($status == 1) { }
if ($result) { }
```

### 现代 PHP 特性

```php
// ✅ 箭头函数（数组回调）
$ids = array_map(fn($item) => (int)$item['id'], $list);
$names = array_map(fn($item) => $item['name'], $list);

// ✅ Match 表达式（替代 switch）
$fieldType = match($field) {
    'content' => 'ueditor',
    'status' => 'select',
    'cover' => 'image',
    'images' => 'images',
    default => 'text'
};

// ✅ Null 合并运算符
$name = $data['name'] ?? 'Default';
$user = $userData['user'] ?? null;

// ✅ Null 合并赋值
$config['timeout'] ??= 30;

// ✅ 命名参数（提高可读性）
DB::table('demo')->insert([
    'name' => 'Test',
    'status' => 1,
]);

// ✅ 构造器属性提升
class UserService
{
    public function __construct(
        private UserRepository $repo,
        private Logger $logger
    ) {}
}
```

### 命名规范

```php
// 类名：PascalCase
class ProductController {}
class UserModel {}

// 方法名：camelCase
public function getUserList() {}
public function saveData() {}

// 常量：UPPER_SNAKE_CASE
const MAX_COUNT = 100;
const DEFAULT_TIMEOUT = 30;

// 变量：snake_case
$user_list = [];
$user_id = 1;

// 数据库字段：snake_case
// user_id, create_time, is_enabled
```

## React/TypeScript 规范

### 组件结构

```tsx
interface Props {
  title: string;
  onSave: (data: FormData) => void;
  onCancel?: () => void;
}

export function DataForm({ title, onSave, onCancel }: Props) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: FormData) => {
    try {
      setLoading(true);
      await onSave(values);
      message.success('保存成功');
    } catch (error) {
      message.error('保存失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Form form={form} onFinish={handleSubmit}>
      <Form.Item name="title" label="标题" rules={[{ required: true }]}>
        <Input placeholder="请输入标题" />
      </Form.Item>
      {/* 其他表单字段 */}
    </Form>
  );
}
```

### 类型定义

```typescript
// 接口类型
interface BaseEntity {
  id: number;
  createTime: string;
  updateTime: string;
}

interface Article extends BaseEntity {
  title: string;
  content: string;
  status: 0 | 1;
  categoryId: number;
}

// 枚举类型
enum Status {
  Disabled = 0,
  Enabled = 1,
  Pending = 2,
}

// 泛型接口
interface ApiResponse<T = any> {
  status: number;
  message: string;
  data: T;
}

// 使用泛型
interface ListResponse {
  list: T[];
  total: number;
}

type ArticleListResponse = ApiResponse<ListResponse<Article>>;
```

## 缓存与锁

### Redis 缓存

```php
use Qscmf\Lib\Cache\QscmfCache;

// 简单缓存（带过期时间）
$cache = new QscmfCache('data_list_key', 3600);
$data = $cache->remember(function() {
    return expensiveDatabaseQuery();
});

// 标签缓存（批量清除）
$cache = new QscmfCache('item_123', 3600, 'items_tag');
$cache->remember(function() {
    return getItemData(123);
});

// 清除所有 items_tag 标签的缓存
QscmfCache::clearByTag('items_tag');

// 永久缓存（不过期）
$cache = new QscmfCache('config_data', 0);
$config = $cache->remember(function() {
    return getSystemConfig();
});
```

### Redis 分布式锁

```php
use Qscmf\Lib\Redis\RedisLock;

// 获取锁（10秒超时）
$lock = new RedisLock('process_lock_key', 10);

if (!$lock->acquire()) {
    $this->error('操作进行中，请稍候');
}

try {
    // 执行需要互斥的业务逻辑
    processCriticalOperation();
} finally {
    // 确保锁被释放
    $lock->release();
}
```

### 缓存失效策略

```php
// 保存/更新后清除相关缓存
public function save($data)
{
    $result = parent::save($data);

    if ($result->status) {
        $id = $result->data['id'];

        // 清除列表缓存
        QscmfCache::clearByTag('data_list');

        // 清除详情缓存
        $cache = new QscmfCache('data_detail_' . $id);
        $cache->clear();

        // 清除相关统计缓存
        QscmfCache::clearByTag('data_statistics');
    }

    return $result;
}
```

## 单元测试指南

### PHPUnit 测试结构

```php
<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;

class DataApiTest extends TestCase
{
    public function testGetList(): void
    {
        $response = $this->get('/api.php/Data/gets');

        $response->assertStatus(200)
            ->assertJson(['status' => 1])
            ->assertJsonStructure([
                'data' => ['list', 'total']
            ]);
    }

    public function testCreateItem(): void
    {
        $response = $this->post('/api.php/Data/add', [
            'title' => 'Test Item',
            'status' => 1,
        ]);

        $response->assertStatus(200)
            ->assertJson([
                'status' => 1,
                'message' => '添加成功'
            ]);
    }
}
```

### 使用 Mock 对象

```php
use App\Services\ExternalApiService;

public function testWithMockService(): void
{
    // 创建 Mock 对象
    $mock = $this->createMock(ExternalApiService::class);

    // 设置方法期望
    $mock->method('fetchData')
        ->willReturn(['success' => true, 'data' => ['id' => 1]]);

    // 注入到服务容器
    app()->instance(ExternalApiService::class, $mock);

    // 执行测试
    $result = D('Data')->syncWithExternal();
    $this->assertTrue($result);
}
```

### 测试 ThinkPHP 上下文

```php
public function testTpModelOperation(): void
{
    $result = $this->runTp(function() {
        return D('Data')->find(1);
    });

    $this->assertIsArray($result);
    $this->assertArrayHasKey('id', $result);
}

public function testTpModelCreate(): void
{
    $result = $this->runTp(function() {
        $id = D('Data')->add([
            'title' => 'Test',
            'status' => 1,
        ]);
        return D('Data')->find($id);
    });

    $this->assertIsArray($result);
    $this->assertEquals('Test', $result['title']);
}
```

## 外部 API Mock

### Wall Class 模式

使用 Wall Class 隔离外部 API 依赖，便于测试和维护：

```php
<?php
namespace Common\Lib\Wall;
use Common\Lib\Wall\Gateway\IGateway;

/**
 * 外部 API 隔离类
 */
class ExternalApiService implements IGateway
{
    public function fetchData($params)
    {
        // 生产环境：调用真实 API
        if (config('app.env') === 'production') {
            return RealApiClient::call($params);
        }

        // 测试环境：返回模拟数据
        return [
            'success' => true,
            'data' => ['id' => 1, 'name' => 'Mock Data']
        ];
    }
}
```

### 在代码中使用 Wall

```php
use Common\Lib\Wall\ExternalApiService;

class DataModel extends GyListModel
{
    public function syncWithExternal()
    {
        $api = new ExternalApiService();
        $result = $api->fetchData(['id' => $this->id]);

        if ($result['success']) {
            $this->save($result['data']);
            return true;
        }

        return false;
    }
}
```

### 测试 Wall Class

```php
public function testExternalApiIntegration()
{
    $mock = $this->createMock(ExternalApiService::class);
    $mock->method('fetchData')->willReturn([
        'success' => true,
        'data' => ['id' => 1, 'name' => 'Test']
    ]);

    app()->instance(ExternalApiService::class, $mock);

    $result = D('Data')->syncWithExternal();
    $this->assertTrue($result);
}
```

## 代码审查清单

### 功能性
- [ ] 功能符合需求文档
- [ ] 边界条件处理（空值、极限值）
- [ ] 错误处理完善（异常捕获、错误提示）
- [ ] 日志记录充分（关键操作、错误日志）

### 性能
- [ ] 避免 N+1 查询问题
- [ ] 使用索引字段进行查询
- [ ] 大数据量分页处理
- [ ] 合理使用缓存（热点数据）
- [ ] 避免在循环中执行数据库查询

### 安全性
- [ ] 输入验证（类型、长度、格式）
- [ ] SQL 注入防护（使用参数绑定）
- [ ] XSS 防护（输出转义）
- [ ] CSRF 防护（表单令牌）
- [ ] 权限检查（操作权限、数据权限）
- [ ] 敏感数据加密（密码、密钥）

### 代码质量
- [ ] 遵循 PSR 标准（PSR-4, PSR-12）
- [ ] 类型声明完整（参数、返回值）
- [ ] 命名清晰有意义
- [ ] 注释充分（复杂逻辑、公共方法）
- [ ] 代码复用（避免重复）
- [ ] 方法长度适中（< 50 行）

### 测试
- [ ] 单元测试覆盖核心逻辑
- [ ] Mock 外部依赖（API、服务）
- [ ] 边界值测试
- [ ] 集成测试覆盖关键流程

## 最佳实践总结

### 1. 始终使用类型声明

```php
// 好
public function getUserById(int $id): ?array { }

// 避免
public function getUserById($id) { }
```

### 2. 使用常量替代魔法数字

```php
// 好
if ($status === DBCont::NORMAL_STATUS) { }

// 避免
if ($status === 1) { }
```

### 3. 优先使用框架方法

```php
// 好
$result = $this->response('success', 1, $data);

// 避免
echo json_encode(['status' => 1, 'msg' => 'success', 'data' => $data]);
```

### 4. 数据库操作使用事务

```php
D()->startTrans();
try {
    D('Table')->add($data);
    D('Log')->add($log);
    D()->commit();
} catch (\Exception $e) {
    D()->rollback();
    throw $e;
}
```

### 5. 外部调用添加超时和重试

```php
try {
    $response = HttpClient::get($url, [
        'timeout' => 5,
        'retry' => 3,
    ]);
} catch (\Exception $e) {
    Log::error('API调用失败', ['url' => $url, 'error' => $e->getMessage()]);
}
```

## 相关文档

- [Admin Controllers](admin-controllers.md) - 后台控制器开发
- [Abstract Base Patterns](abstract-base-patterns.md) - 抽象基类模式
- [Models & Migrations](models-migrations.md) - 模型与迁移
- [Migration Metadata](migration-metadata.md) - 迁移元数据

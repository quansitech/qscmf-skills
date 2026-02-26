# Development Standards Reference

> QSCMF v13 开发规范与测试指南

## 版本特性

| 特性 | v13 |
|------|-----|
| PHP 版本 | >= 8.1 |
| PHPUnit | ^9.3.0 |
| jQuery | 3.7 |

## PHP 8.1+ 编码规范

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
    'cover' => 'picture',
    'images' => 'pictures',
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

## jQuery 3.7 兼容性

### 已删除的方法

升级到 jQuery 3.7 后，以下方法已被移除：

| 已移除方法 | 替代方案 |
|-----------|---------|
| `.andSelf()` | `.addBack()` |
| `.size()` | `.length` |
| `.bind()` | `.on()` |
| `.delegate()` | `.on()` |
| `.live()` | `.on()` |
| `.die()` | `.off()` |
| `.unbind()` | `.off()` |
| `.undelegate()` | `.off()` |
| `.selector` | 无直接替代 |
| `.context` | 无直接替代 |

### AJAX 方法变更

```javascript
// ❌ 已移除
$.get().success()
$.get().error()
$.get().complete()
$.post().success()
$.post().error()
$.post().complete()

// ✅ 使用替代
$.get().done()
$.get().fail()
$.get().always()
$.post().done()
$.post().fail()
$.post().always()
```

### 常见迁移示例

```javascript
// ❌ 旧代码
$('.elements').size()

// ✅ 新代码
$('.elements').length

// ❌ 旧代码
$('.element').bind('click', handler)

// ✅ 新代码
$('.element').on('click', handler)

// ❌ 旧代码
$('.parent').delegate('.child', 'click', handler)

// ✅ 新代码
$('.parent').on('click', '.child', handler)
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
public function add()
{
    if (IS_POST) {
        $result = D($this->modelName)->add(I('post.'));

        if ($result) {
            $id = $result;

            // 清除列表缓存
            QscmfCache::clearByTag('data_list');

            // 清除详情缓存
            $cache = new QscmfCache('data_detail_' . $id);
            $cache->clear();
        }
    }
}
```

## 错误处理

### 标准错误响应

```php
// 在控制器中
public function add()
{
    try {
        if (IS_POST) {
            $result = D($this->modelName)->add(I('post.'));

            if (!$result) {
                $this->error(D($this->modelName)->getError());
            }

            $this->success('添加成功', U('index'));
        }
    } catch (\Exception $e) {
        // 记录日志
        sysLogs('操作失败: ' . $e->getMessage());

        // 返回错误
        $this->error('系统错误，请稍后重试');
    }
}
```

### 事务错误处理

```php
public function complexSave()
{
    $model = D('TableName');
    $model->startTrans();

    try {
        // 业务逻辑
        $id = $model->add($data);
        D('Related')->add(['foreign_id' => $id]);

        $model->commit();
        return $this->success('保存成功');

    } catch (\Exception $e) {
        $model->rollback();

        // 记录详细错误
        sysLogs('保存失败: ' . $e->getMessage(), 'error');

        return $this->error('保存失败');
    }
}
```

## 日志记录

```php
// 信息日志
sysLogs('操作描述, id:' . $id);

// 带上下文的日志
sysLogs(sprintf(
    '用户 %s 操作了记录 %s，结果: %s',
    session('admin_id'),
    $id,
    $result ? '成功' : '失败'
));

// 错误日志
sysLogs('错误详情: ' . $error_message, 'error');

// 调试日志
sysLogs('调试信息: ' . json_encode($debug_data), 'debug');
```

## 安全性

### 输入验证

```php
// ✅ 使用 I() 函数获取输入
$id = I('get.id', 0, 'intval');
$name = I('post.name', '', 'trim,htmlspecialchars');
$status = I('post.status', 0, 'intval');

// ✅ 使用参数绑定
$result = D('TableName')->where(['id' => $id])->find();

// ❌ 避免直接拼接 SQL
$sql = "SELECT * FROM table WHERE id = $id";  // 危险
```

### XSS 防护

```php
// 输出转义
echo htmlspecialchars($data['title'], ENT_QUOTES, 'UTF-8');

// 在模板中使用
{$data.title|htmlspecialchars}
```

### CSRF 防护

QSCMF 框架内置 CSRF 防护，表单会自动添加令牌。

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
- [ ] 权限检查（操作权限、数据权限）
- [ ] 敏感数据加密（密码、密钥）

### 代码质量
- [ ] 遵循 PSR 标准（PSR-4）
- [ ] 类型声明完整（参数、返回值）
- [ ] 命名清晰有意义
- [ ] 注释充分（复杂逻辑、公共方法）
- [ ] 代码复用（避免重复）
- [ ] 方法长度适中（< 50 行）

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
$builder = new FormBuilder();
$builder->setPostUrl(U('add'))->build();

// 避免
echo '<form action="' . U('add') . '">';
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
- [Testing](testing.md) - PHPUnit 9 测试指南
- [CRUD Patterns](crud-patterns.md) - CRUD 开发模式
- [Model Guide](model-guide.md) - 模型开发指南

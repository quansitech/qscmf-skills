# runTp() 进程隔离测试机制

> 在 Laravel 测试环境中执行 ThinkPHP 代码

## 概述

`runTp()` 是 QSCMF 测试框架的核心机制，允许在 Laravel/PHPUnit 测试环境中执行 ThinkPHP 业务代码。

**位置**: `vendor/tiderjian/think-core/src/Testing/InteractsWithTpConsole.php`

## 为什么需要 runTp()

QSCMF 采用 ThinkPHP + Laravel 混合架构：
- **业务代码** 运行在 ThinkPHP 环境
- **测试框架** 使用 Laravel 的 PHPUnit

`runTp()` 通过**进程隔离**解决两个框架环境不兼容的问题。

## 基本用法

```php
use Testing\InteractsWithTpConsole;

class MyTest extends TestCase
{
    use InteractsWithTpConsole;

    public function testThinkPhpCode()
    {
        $result = $this->runTp(function () {
            // 这里的代码在 ThinkPHP 环境中执行
            return D('User')->find(1);
        });

        // 在 Laravel 环境中断言
        $this->assertEquals(1, $result['id']);
    }
}
```

## 实现原理

```
┌─────────────────────────────────────────────────────────────┐
│                    Laravel/PHPUnit 进程                      │
│                                                             │
│   $this->runTp(function() {                                 │
│       return D('User')->find(1);                            │
│   });                                                       │
│       │                                                     │
│       ▼                                                     │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ pcntl_fork() 创建子进程                              │   │
│   └─────────────────────┬───────────────────────────────┘   │
│                         │                                   │
├─────────────────────────┼───────────────────────────────────┤
│                         ▼                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              ThinkPHP 子进程                         │   │
│   │                                                     │   │
│   │  define('IS_CGI', 1);                               │   │
│   │  define('IS_CLI', false);                           │   │
│   │  加载 tp.php 初始化 ThinkPHP                        │   │
│   │  执行闭包函数                                       │   │
│   │  序列化返回结果                                     │   │
│   │  通过管道写回父进程                                 │   │
│   └─────────────────────────────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              父进程接收结果                          │   │
│   │  从管道读取数据                                     │   │
│   │  反序列化返回给调用者                               │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 关键实现细节

### 1. 进程隔离

```php
$pid = pcntl_fork();
if ($pid === 0) {
    // 子进程 - 模拟 Web 环境
    define('IS_CGI', 1);
    define('IS_CLI', false);
    // 加载 ThinkPHP
    require __DIR__ . '/../../../tp.php';
    // 执行闭包并序列化结果
    $result = $callback();
    echo "__QSCMF_TESTING_SERIALIZE_START__";
    echo serialize($result);
    echo "__QSCMF_TESTING_SERIALIZE_END__";
    exit(0);
}
// 父进程等待并获取结果
pcntl_wait($status);
```

### 2. 环境模拟

```php
// 子进程中设置的关键常量
define('IS_CGI', 1);       // 模拟 CGI 模式
define('IS_CLI', false);   // 非 CLI 模式

// 路由设置
$_SERVER['argv'] = ['/Qscmf/Testing/index'];
```

### 3. 数据交换

```php
// 通过管道通信
$pipe = '/tmp/test.pipe';
posix_mkfifo($pipe, 0666);

// 使用 Opis\Closure 序列化闭包
use Opis\Closure\SerializableClosure;
$serialized = serialize(new SerializableClosure($callback));
```

## 使用示例

### 示例1: 模型查询

```php
public function testModelQuery()
{
    $result = $this->runTp(function () {
        return D('ResourceContent')
            ->where(['status' => DBCont::NORMAL_STATUS])
            ->limit(10)
            ->select();
    });

    $this->assertCount(10, $result);
}
```

### 示例2: 控制器调用

```php
public function testController()
{
    $result = $this->runTp(function () {
        $controller = new \Home\Controller\KnowledgeStoreSyncController();
        return $controller->syncResource();
    });

    $this->assertTrue($result['success']);
}
```

### 示例3: 创建测试数据

```php
public function testWithTestData()
{
    $contentId = $this->runTp(function () {
        return D('ResourceContent')->createAdd([
            'title' => '测试内容',
            'status' => DBCont::NORMAL_STATUS,
        ]);
    });

    $this->assertGreaterThan(0, $contentId);

    // 后续测试使用这个 ID
    return $contentId;
}
```

### 示例4: 事务测试

```php
public function testTransaction()
{
    $result = $this->runTp(function () {
        M()->startTrans();
        try {
            D('User')->createAdd(['name' => 'test']);
            D('Profile')->createAdd(['user_id' => M()->getLastInsID()]);
            M()->commit();
            return true;
        } catch (\Exception $e) {
            M()->rollback();
            return false;
        }
    });

    $this->assertTrue($result);
}
```

## 限制与注意事项

### 1. 每个测试方法只能调用一次

```php
// ❌ 错误 - 会导致 IS_CGI 常量冲突
public function testMultiple()
{
    $result1 = $this->runTp(fn() => D('User')->find(1));
    $result2 = $this->runTp(fn() => D('User')->find(2)); // 报错！
}

// ✅ 正确 - 合并到一个 runTp 调用中
public function testMultiple()
{
    [$result1, $result2] = $this->runTp(function () {
        return [
            D('User')->find(1),
            D('User')->find(2),
        ];
    });
}
```

### 2. PHPUnit 断言不能在 runTp 内使用

```php
// ❌ 错误 - 断言在子进程中，不会影响测试结果
$this->runTp(function () {
    $user = D('User')->find(1);
    $this->assertNotNull($user); // 无效！
});

// ✅ 正确 - 在 runTp 外断言
$user = $this->runTp(fn() => D('User')->find(1));
$this->assertNotNull($user);
```

### 3. Mock 对象无法跨进程

```php
// ❌ 错误 - Mock 对象无法序列化传递
$mock = $this->createMock(SomeService::class);
$this->runTp(function () use ($mock) {
    // $mock 无法在子进程中使用
});

// ✅ 正确 - 在 runTp 内部创建 Mock
$this->runTp(function () {
    // 使用项目自带的 Wall Class Mock 机制
    $mock = new NoLogClient();
    app()->instance(Client::class, $mock);
});
```

### 4. 返回数据大小限制

```php
// ❌ 可能失败 - 返回数据过大
$result = $this->runTp(function () {
    return D('BigTable')->select(); // 百万条记录
});

// ✅ 正确 - 限制返回数据量
$result = $this->runTp(function () {
    return D('BigTable')->limit(1000)->select();
});
```

## 最佳实践

1. **最小化 runTp 内部逻辑** - 只放必要的 ThinkPHP 代码
2. **返回简单数据** - 数组、标量值，避免返回复杂对象
3. **错误处理** - 在 runTp 内捕获异常并返回错误信息
4. **数据清理** - 测试后清理创建的数据

```php
public function testWithCleanup()
{
    $id = $this->runTp(function () {
        return D('Test')->createAdd(['name' => 'test']);
    });

    try {
        // 测试逻辑
        $this->assertGreaterThan(0, $id);
    } finally {
        // 清理数据
        $this->runTp(function () use ($id) {
            D('Test')->delete($id);
        });
    }
}
```

---
title: CLI 控制器测试 (v14)
version: v14
impact: HIGH
when: "测试命令行控制器、批处理任务时使用"
---

# CLI 控制器测试 (v14)

测试命令行控制器和批处理任务的策略。

## 测试策略

### 1. 使用 runTp() 执行 CLI 命令

```php
use Testing\InteractsWithTpConsole;

class BatchJobTest extends TestCase
{
    use InteractsWithTpConsole;

    public function test_batch_process()
    {
        $result = $this->runTp(function () {
            // 执行 CLI 控制器
            return D('Product')->batchProcess();
        });

        $this->assertTrue($result['success']);
    }
}
```

### 2. 模拟 CLI 环境

```php
public function test_cli_mode_protection()
{
    // 非CLI模式应该被拒绝
    $response = $this->get('/home/batch/run');

    $response->assertStatus(403);
}
```

## 相关文件

- [test-runtp.md](test-runtp.md) - runTp() 进程隔离测试
- [../pattern/pattern-cli-controller.md](../pattern/pattern-cli-controller.md) - CLI 控制器模式

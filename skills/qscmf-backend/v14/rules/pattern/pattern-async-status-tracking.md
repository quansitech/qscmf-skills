---
title: Async Status Tracking Pattern (v14)
impact: MEDIUM
impactDescription: Pattern for tracking long-running async tasks
tags: pattern, async, status, trait, v14
---

## 异步任务状态追踪模式

追踪长时间运行任务的执行状态，支持状态流转、批量查询、错误记录。

### 适用场景

- 外部系统同步（知识库、搜索索引）
- AI 内容处理（生成、分析）
- 批量导入导出
- 任何需要异步处理的任务

---

## 核心模式

### 本质

```
任务触发 → 状态记录 → 异步执行 → 状态更新 → 结果查询
```

### 状态机

```
PENDING(0) → PROCESSING(1) → SUCCESS(2)
                  │
                  └──→ FAILED(3) ──→ 重试或取消
```

---

## Trait 实现

```php
<?php
namespace App\Lib\Pattern;

trait AsyncStatusTrackingTrait
{
    /**
     * 创建任务记录
     * @param string $type 任务类型
     * @param int $relateId 关联ID
     * @return int 任务记录ID
     */
    protected function createTaskRecord(string $type, int $relateId): int
    {
        return D('AsyncTask')->add([
            'type' => $type,
            'relate_id' => $relateId,
            'status' => self::STATUS_PENDING,
            'create_time' => time(),
        ]);
    }

    /**
     * 批量获取任务状态
     * @param string $type 任务类型
     * @param array $ids 关联ID列表
     * @return array [relate_id => status]
     */
    protected function getBatchTaskStatus(string $type, array $ids): array
    {
        return D('AsyncTask')->where([
            'type' => $type,
            'relate_id' => ['IN', $ids],
        ])->getField('relate_id,status', true);
    }

    /**
     * 更新任务状态
     */
    protected function updateTaskStatus(int $taskId, int $status, ?string $error = null, $extraData = null): bool
    {
        $data = [
            'id' => $taskId,
            'status' => $status,
            'update_time' => time(),
        ];

        if ($error !== null) {
            $data['error_message'] = $error;
        }

        if ($extraData !== null) {
            $data['extra_data'] = is_string($extraData) ? $extraData : json_encode($extraData);
        }

        return D('AsyncTask')->save($data) !== false;
    }

    /**
     * 检查是否正在处理中
     */
    protected function isProcessing(string $type, int $relateId): bool
    {
        return D('AsyncTask')->where([
            'type' => $type,
            'relate_id' => $relateId,
            'status' => self::STATUS_PROCESSING,
        ])->count() > 0;
    }
}
```

---

## 控制器集成

```php
<?php
namespace Admin\Controller;

use App\Lib\Pattern\AsyncStatusTrackingTrait;
use Qscmf\Core\QsListController;

abstract class ContentController extends QsListController
{
    use AsyncStatusTrackingTrait;

    // 定义状态常量
    const STATUS_PENDING = 0;
    const STATUS_PROCESSING = 1;
    const STATUS_SUCCESS = 2;
    const STATUS_FAILED = 3;

    public function save()
    {
        $model = D($this->modelName);
        $data = I('post.');

        $result = $model->createAdd($data);

        if ($result !== false) {
            // 创建异步任务记录
            $taskId = $this->createTaskRecord($this->getTaskType(), $result);

            // 分发异步任务
            $this->dispatchAsyncTask($taskId, $result);

            $this->success('保存成功，后台处理中');
        }

        $this->error($model->getError());
    }

    public function index()
    {
        // ... 获取数据列表 ...

        // 批量获取任务状态
        $ids = array_column($data_list, 'id');
        $taskStatus = $this->getBatchTaskStatus($this->getTaskType(), $ids);

        // 附加状态到数据
        foreach ($data_list as &$item) {
            $item['task_status'] = $taskStatus[$item['id']] ?? -1;
        }

        // ... 渲染表格 ...
    }

    /**
     * 子类实现：获取任务类型标识
     */
    abstract protected function getTaskType(): string;

    /**
     * 子类实现：分发异步任务
     */
    abstract protected function dispatchAsyncTask(int $taskId, int $relateId): void;
}
```

---

## UI 集成

### 状态列显示

```php
$container->select('task_status', '处理状态')
    ->setValueEnum([
        -1 => '未处理',
        0 => '待处理',
        1 => '处理中',
        2 => '已完成',
        3 => '处理失败',
    ])
    ->setBadge([
        -1 => 'default',
        0 => 'warning',
        1 => 'processing',
        2 => 'success',
        3 => 'error',
    ]);
```

### 条件操作按钮

```php
// 仅在非处理中时显示
$container->button('处理')
    ->setShowCondition('task_status', 'neq', 1)
    ->request('post', U('process'), ['id' => '__id__']);

// 仅在失败时显示
$container->button('查看错误')
    ->setShowCondition('task_status', 'eq', 3)
    ->modal($this->buildErrorModal());
```

---

## 异步任务处理

```php
<?php
namespace Common\Job;

class AsyncTaskJob
{
    protected $taskId;

    public function __construct($taskId)
    {
        $this->taskId = $taskId;
    }

    public function handle()
    {
        $task = D('AsyncTask')->find($this->taskId);

        if (!$task || $task['status'] != 0) {
            return;  // 状态不对，跳过
        }

        // 更新为处理中
        D('AsyncTask')->save([
            'id' => $this->taskId,
            'status' => 1,
        ]);

        try {
            // 执行具体业务逻辑
            $result = $this->process($task);

            // 成功
            D('AsyncTask')->save([
                'id' => $this->taskId,
                'status' => 2,
                'extra_data' => json_encode($result),
                'update_time' => time(),
            ]);
        } catch (\Exception $e) {
            // 失败
            D('AsyncTask')->save([
                'id' => $this->taskId,
                'status' => 3,
                'error_message' => $e->getMessage(),
                'update_time' => time(),
            ]);
        }
    }

    /**
     * 子类实现具体处理逻辑
     */
    protected function process(array $task)
    {
        // 由具体任务实现
    }
}
```

---

## 数据库表结构

```sql
CREATE TABLE `async_task` (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
    `type` varchar(50) NOT NULL COMMENT '任务类型',
    `relate_id` int(11) unsigned NOT NULL COMMENT '关联ID',
    `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '0待处理/1处理中/2成功/3失败',
    `extra_data` text COMMENT '额外数据(JSON)',
    `error_message` text COMMENT '错误信息',
    `create_time` int(11) unsigned DEFAULT NULL,
    `update_time` int(11) unsigned DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_type_relate` (`type`, `relate_id`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 扩展用法

### 带重试机制

```php
const MAX_RETRY = 3;

protected function handleFailure($task, $error)
{
    $retryCount = $task['retry_count'] ?? 0;

    if ($retryCount < self::MAX_RETRY) {
        // 重新加入队列
        D('AsyncTask')->save([
            'id' => $task['id'],
            'status' => 0,  // 回到待处理
            'retry_count' => $retryCount + 1,
        ]);
        $this->requeue($task['id']);
    } else {
        // 标记为最终失败
        D('AsyncTask')->save([
            'id' => $task['id'],
            'status' => 3,
            'error_message' => $error,
        ]);
    }
}
```

### 带进度追踪

```php
// 扩展状态
const STATUS_PROCESSING = 1;
const STATUS_PARTIAL_SUCCESS = 4;  // 部分成功

// 表结构增加
`progress` int(3) DEFAULT 0 COMMENT '进度百分比',
`success_count` int(11) DEFAULT 0,
`fail_count` int(11) DEFAULT 0,
```

---

## 相关模式

- [Queue Job Pattern](pattern-queue-job.md) - 异步任务实现
- [Redis Lock Pattern](pattern-redis-lock.md) - 防止并发处理

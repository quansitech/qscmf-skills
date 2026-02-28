# 知识库同步架构

> 异步双表架构同步内容到外部知识库

## 概述

知识库同步系统采用**双表架构**实现异步同步，将本地内容同步到外部向量数据库（如 Qdrant）。

## 架构设计

### 双表结构

```
qs_kstore_sync (状态表)              qs_kstore_process (历史表)
┌─────────────────────┐             ┌─────────────────────────┐
│ id                  │             │ id                      │
│ type                │◄────────────│ type                    │
│ relate_id           │             │ relate_id               │
│ latest_process_id ──┼────────────►│ task_id (外部API)       │
│ process_status      │             │ process_status          │
│ retry_count         │             │ sync_data (JSON)        │
│ last_sync_time      │             │ error_message           │
│ is_delete           │             │ create_date             │
└─────────────────────┘             └─────────────────────────┘
```

**状态表用途**: 记录每个内容的最新同步状态
**历史表用途**: 记录每次同步的详细信息，支持重试和追溯

### 状态流转

```
PROCESSING(0) → SUCCESS(1) / FAILED(2) / CANCELLED(3)
       │
       └── 失败后可重试 (retry_count < 3)
```

## 核心类

### KnowledgeStoreHelper

**位置**: KnowledgeStore 目录 (如 `KnowledgeStoreHelper.class.php`)

```php
class KnowledgeStoreHelper
{
    // 提交同步任务
    public static function submitSyncTask($type, $relate_id): bool;

    // 初始化同步记录
    public static function initializeSyncRecords($type, $relate_id): array;

    // 关联外部任务ID
    public static function associateTaskId($process_id, $task_id): bool;

    // 刷新同步状态
    public static function refreshSyncStatus($sync_id, $process_id, $status, $data = null): bool;

    // 获取待处理任务
    public static function getPendingSyncTasks($limit = 50): array;

    // 获取可重试任务
    public static function getRetryableTasks($limit = 50): array;
}
```

### KnowledgeStoreSync

**位置**: KnowledgeStore 目录 (如 `KnowledgeStoreSync.class.php`)

```php
class KnowledgeStoreSync
{
    // 创建同步任务
    public function createSyncTask(array $data): ?string;

    // 获取任务状态
    public function getTaskStatus(string $task_id): ?array;

    // 删除任务
    public function deleteTask(string $task_id): bool;

    // 批量查询任务状态
    public function listTasks(array $task_ids): array;
}
```

### KnowledgeStorePollJob

**位置**: Job 目录 (如 `KnowledgeStorePollJob.class.php`)

```php
class KnowledgeStorePollJob
{
    // 执行轮询
    public function perform(): void;

    // 批量轮询任务状态
    public function batchPollTasks(array $tasks): void;
}
```

## 使用方式

### 内容保存时触发同步

```php
// 在控制器中
public function save()
{
    $data = I('post.');
    $result = D('ResourceContent')->createSave($data);

    if ($result !== false) {
        // 触发知识库同步
        KnowledgeStoreHelper::submitSyncTask('ResourceContent', $result);
    }

    $this->success('保存成功');
}
```

### 查询同步状态

```php
// 获取内容的同步状态
$status = KnowledgeStoreHelper::getSyncStatus('ResourceContent', $content_id);

// 状态值
// 0 = PROCESSING (处理中)
// 1 = SUCCESS (成功)
// 2 = FAILED (失败)
// 3 = CANCELLED (已取消)
```

## Cron 配置

```bash
# crontab.txt
*/5 * * * * php www/index.php Home/KnowledgeStoreSync/runPoll
```

**轮询逻辑**:
1. 每5分钟执行一次
2. 查询 50 个 `PROCESSING` 状态的记录
3. 批量调用外部 API 获取任务状态
4. 更新本地状态表

## 重试机制

```php
// 最大重试次数
const MAX_RETRY_COUNT = 3;

// 获取可重试任务
$retryable = KnowledgeStoreHelper::getRetryableTasks(50);

foreach ($retryable as $task) {
    // 重新提交同步任务
    KnowledgeStoreHelper::submitSyncTask($task['type'], $task['relate_id']);
}
```

## 环境配置

```bash
# .env
KNOWLEDGE_STORE_API_URL=https://api.example.com/kstore
KNOWLEDGE_STORE_API_KEY=your_api_key
```

## 错误处理

```php
try {
    $result = KnowledgeStoreHelper::submitSyncTask($type, $id);
    if (!$result) {
        Log::error("知识库同步失败: type={$type}, id={$id}");
    }
} catch (\Exception $e) {
    // 记录错误但不影响主流程
    Log::error("知识库同步异常: " . $e->getMessage());
}
```

## 监控与日志

```php
// 日志文件位置
storage/logs/knowledge_store_sync.log

// 关键日志
- 同步任务提交
- 外部API调用结果
- 状态更新
- 重试记录
- 错误信息
```

## 最佳实践

1. **异步优先**: 不要在用户请求中同步调用外部 API
2. **失败隔离**: 同步失败不应影响内容保存
3. **重试策略**: 使用指数退避避免频繁重试
4. **监控告警**: 对 FAILED 状态设置告警
5. **数据追溯**: 保留历史表便于问题排查

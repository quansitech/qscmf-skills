# CLI 控制器模式

> 后台任务与批处理的命令行执行模式

## 概述

QSCMF 支持通过命令行执行控制器方法，用于定时任务、批处理作业等场景。

## 基类

### CliModeHelperController

**位置**: `app/Home/Controller/CliModeHelperController.class.php`

```php
<?php
namespace Home\Controller;

use Think\Controller;

class CliModeHelperController extends Controller
{
    protected $logFileName = '';

    public function __construct()
    {
        parent::__construct();

        // CLI 模式保护
        if (!IS_CLI) {
            die('This action must be run in CLI mode');
        }

        // 设置日志文件
        if ($this->logFileName) {
            $this->setLogFileName($this->logFileName);
        }
    }

    protected function writeErrorLog($message)
    {
        $logFile = $this->getLogFileFullName();
        $logDir = dirname($logFile);
        if (!is_dir($logDir)) {
            mkdir($logDir, 0755, true);
        }
        file_put_contents($logFile, date('Y-m-d H:i:s') . ' - ' . $message . "\n", FILE_APPEND);
    }

    protected function getLogFileFullName()
    {
        return LARA_STORAGE_PATH . '/logs/' . $this->logFileName . '.log';
    }

    protected function setLogFileName($name)
    {
        $this->logFileName = $name;
    }
}
```

## 使用示例

### 创建 CLI 控制器

```php
<?php
namespace Home\Controller;

use Home\Controller\CliModeHelperController;

class KnowledgeStoreSyncController extends CliModeHelperController
{
    protected $logFileName = 'knowledge_store_sync';

    /**
     * 轮询同步任务状态
     *
     * 执行: php www/index.php Home/KnowledgeStoreSync/runPoll
     */
    public function runPoll()
    {
        $this->writeErrorLog('开始轮询同步任务');

        try {
            $job = new \Common\Job\KnowledgeStorePollJob();
            $job->perform();
            $this->writeErrorLog('轮询完成');
        } catch (\Exception $e) {
            $this->writeErrorLog('轮询失败: ' . $e->getMessage());
        }
    }

    /**
     * 同步单个资源
     *
     * 执行: php www/index.php Home/KnowledgeStoreSync/syncResource/123
     */
    public function syncResource($id = null)
    {
        if (!$id) {
            $this->writeErrorLog('缺少资源ID');
            return;
        }

        $result = \Common\Lib\KnowledgeStore\KnowledgeStoreHelper::submitSyncTask(
            'ResourceContent',
            $id
        );

        $this->writeErrorLog("同步资源 {$id}: " . ($result ? '成功' : '失败'));
    }
}
```

### 批量处理控制器

```php
<?php
namespace Home\Controller;

use Home\Controller\CliModeHelperController;

class AiTagSyncController extends CliModeHelperController
{
    protected $logFileName = 'ai_tag_sync';

    /**
     * 生成 AI 标签
     *
     * 执行: php www/index.php Home/AiTagSync/runGenerate
     */
    public function runGenerate()
    {
        $pendingTasks = D('AiTagRecord')->where([
            'status' => DBCont::AI_TAG_STATUS_PENDING
        ])->limit(50)->select();

        $this->writeErrorLog('待处理任务: ' . count($pendingTasks));

        foreach ($pendingTasks as $task) {
            try {
                $job = new \Common\Job\AiTagGenerateJob();
                $job->args = ['id' => $task['id']];
                $job->perform();
            } catch (\Exception $e) {
                $this->writeErrorLog("任务 {$task['id']} 失败: " . $e->getMessage());
            }
        }
    }
}
```

## 执行方式

### 基本命令格式

```bash
php www/index.php <Module>/<Controller>/<Action>/<Arg1>/<Arg2>
```

### 示例

```bash
# 无参数
php www/index.php Home/KnowledgeStoreSync/runPoll

# 带参数
php www/index.php Home/KnowledgeStoreSync/syncResource/123

# 多参数
php www/index.php Home/BatchProcess/import/all/force

# 使用 docker-compose
docker-compose run --rm php-fpm8.2 php /var/www/zt-action/www/index.php Home/KnowledgeStoreSync/runPoll
```

## Cron 配置

```bash
# crontab.txt

# 知识库同步轮询 (每5分钟)
*/5 * * * * docker-compose run --rm php-fpm8.2 php /var/www/zt-action/www/index.php Home/KnowledgeStoreSync/runPoll

# AI 标签生成 (每分钟)
* * * * * docker-compose run --rm php-fpm8.2 php /var/www/zt-action/www/index.php Home/AiTagSync/runGenerate

# 数据清理 (每天凌晨2点)
0 2 * * * docker-compose run --rm php-fpm8.2 php /var/www/zt-action/www/index.php Home/DataClean/run
```

## 参数获取

### 通过路由参数

```php
public function syncResource($id = null, $force = false)
{
    // php www/index.php Home/KnowledgeStoreSync/syncResource/123/1
    echo "ID: {$id}, Force: {$force}";
}
```

### 通过 argv

```php
public function import()
{
    // php www/index.php Home/Import/run type=all limit=100
    $argv = $_SERVER['argv'];

    // 解析命名参数
    $params = [];
    foreach (array_slice($argv, 2) as $arg) {
        if (strpos($arg, '=') !== false) {
            list($key, $value) = explode('=', $arg, 2);
            $params[$key] = $value;
        }
    }

    $type = $params['type'] ?? 'all';
    $limit = (int)($params['limit'] ?? 1000);
}
```

## 日志管理

### 日志文件位置

```
lara/storage/logs/
├── knowledge_store_sync.log
├── ai_tag_sync.log
├── data_clean.log
└── ...
```

### 日志轮转

```php
protected function getLogFileFullName()
{
    // 按日期分割日志
    $date = date('Y-m-d');
    return LARA_STORAGE_PATH . '/logs/' . $this->logFileName . '_' . $date . '.log';
}
```

## 最佳实践

1. **CLI 保护**: 始终检查 `IS_CLI` 常量
2. **日志记录**: 记录关键操作和错误
3. **异常处理**: 捕获异常并记录，避免进程崩溃
4. **内存管理**: 批量处理时注意内存使用
5. **锁机制**: 避免同一任务并发执行

```php
public function runBatch()
{
    // 使用 Redis 锁防止并发
    $lock = new \Qscmf\Utils\Libs\RedisLock();
    if (!$lock->lock('batch_task', 3600)) {
        $this->writeErrorLog('任务正在执行，跳过');
        return;
    }

    try {
        // 批量处理逻辑
        $this->processBatch();
    } finally {
        $lock->unlock('batch_task');
    }
}
```

---
title: 通用代码模式 (v14)
version: v14
impact: MEDIUM
when: "应用抽象基类、Redis 锁、队列任务等通用模式时使用"
---

# Common Code Patterns

> This file documents reusable patterns: Abstract Base Class, Redis Lock for concurrency, and Queue Job pattern.

---

## Abstract Base Class Pattern

For multiple similar modules with shared logic, use abstract base classes to reduce code duplication.

### Pattern Structure

```php
<?php
// Common/Model/CategoryModel.class.php
namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;

abstract class CategoryModel extends GyListModel
{
    // Abstract methods for specific configuration
    protected abstract function getTableName(): string;
    protected abstract function getModuleTitle(): string;

    // Shared methods
    public function getTree(): array
    {
        return $this->where(['status' => DBCont::NORMAL_STATUS])
            ->order('sort asc')
            ->select();
    }

    public function getOptions(): array
    {
        $list = $this->getTree();
        return array_column($list, 'name', 'id');
    }
}

// Common/Model/ProductCateModel.class.php
class ProductCateModel extends CategoryModel
{
    protected function getTableName(): string
    {
        return 'product_cate';
    }

    protected function getModuleTitle(): string
    {
        return '商品分类';
    }
}

// Common/Model/ArticleCateModel.class.php
class ArticleCateModel extends CategoryModel
{
    protected function getTableName(): string
    {
        return 'article_cate';
    }

    protected function getModuleTitle(): string
    {
        return '文章分类';
    }
}
```

### When to Apply

- 3+ modules share the same structure and methods
- Base class provides 2+ reusable methods
- Future modules will follow the same pattern

---

## Redis Lock for Concurrency

Use Redis Lock to prevent concurrent execution of critical operations (e.g., batch processing, exports).

### Basic Usage

```php
use Qscmf\Lib\Redis\RedisLock;

public function batchProcess()
{
    $lock = new RedisLock('batch_process_' . $this->uid);

    if (!$lock->acquire()) {
        $this->error('操作进行中，请稍候');
    }

    try {
        // Process batch
        $result = $this->doBatchProcess();
        $lock->release();
        return $result;
    } catch (\Exception $e) {
        $lock->release();
        throw $e;
    }
}
```

### With Timeout

```php
public function exportData()
{
    // Lock with 60-second timeout
    $lock = new RedisLock('export_' . $this->uid, 60);

    if (!$lock->acquire()) {
        $this->error('导出任务进行中，请等待完成');
    }

    try {
        $result = $this->generateExport();
        $lock->release();
        $this->success('导出成功', '', ['file' => $result]);
    } catch (\Exception $e) {
        $lock->release();
        $this->error('导出失败: ' . $e->getMessage());
    }
}
```

### When to Apply

- Batch operations that should not run concurrently
- Long-running tasks triggered by user action
- Export/import operations that consume significant resources

---

## Queue Job Pattern

Use Queue Jobs for long-running or async tasks to avoid blocking HTTP requests.

### Create Job Class

```php
<?php
// lara/app/Jobs/ExportJob.php
namespace App\Jobs;

use Qscmf\Lib\Queue\QueueJob;

class ExportJob extends QueueJob
{
    public function handle(): void
    {
        $data = $this->getData();

        // Retrieve parameters
        $module = $data['module'];
        $filters = $data['filters'];
        $userId = $data['user_id'];

        // Process export...
        $filePath = $this->generateExport($module, $filters);

        // Notify user
        $this->notifyUser($userId, $filePath);
    }

    private function generateExport(string $module, array $filters): string
    {
        // Export logic...
        return '/exports/' . $module . '_' . date('YmdHis') . '.xlsx';
    }

    private function notifyUser(int $userId, string $filePath): void
    {
        // Send notification...
    }
}
```

### Dispatch Job

```php
use Qscmf\Lib\Queue\QueueJob;
use App\Jobs\ExportJob;

public function export()
{
    $filters = I('get.');

    // Dispatch async job
    QueueJob::dispatch(ExportJob::class, [
        'module' => 'Product',
        'filters' => $filters,
        'user_id' => $this->uid,
    ]);

    $this->success('导出任务已提交，完成后将通知您');
}
```

### Run Queue Worker

```bash
# Start queue worker
QUEUE_ENV=prod QUEUE_COUNT=1 php app/queue_resque.php
```

### When to Apply

- Operations taking more than 5 seconds
- Large data exports/imports
- Background data synchronization
- Email/notification sending in bulk

---

## Related Rules

- [Abstract Base](pattern/pattern-abstract-base.md) - Detailed abstract base pattern guide
- [Redis Lock](pattern/pattern-redis-lock.md) - Complete Redis lock reference
- [Queue Job](pattern/pattern-queue-job.md) - Queue job configuration
- [Batch Actions](crud/crud-batch-actions.md) - Batch operations in CRUD

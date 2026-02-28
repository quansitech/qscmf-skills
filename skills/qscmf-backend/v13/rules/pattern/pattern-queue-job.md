---
title: Queue Job Pattern (v13)
impact: HIGH
impactDescription: Required for async task processing
tags: pattern, queue, job, v13
---

## Queue Job Pattern (v13)

Async task processing using queues in QSCMF v13.

### When to Use This Rule

- Long-running tasks
- Batch processing
- Background operations

---

## Queue Configuration

QSCMF uses php-resque for queue processing:

```bash
# Start queue worker
QUEUE_ENV=prod QUEUE_COUNT=1 php app/queue_resque.php
```

---

## Defining Jobs

```php
// Job 类文件 (如 SendEmailJob.php)

namespace Common\Job;

use Gy_Library\Job\BaseJob;

class SendEmailJob extends BaseJob
{
    public function perform()
    {
        $args = $this->args;

        $to = $args['to'];
        $subject = $args['subject'];
        $body = $args['body'];

        // Send email logic
        $mailer = new \Gy_Library\GyMailer();
        $result = $mailer->send($to, $subject, $body);

        if (!$result) {
            throw new \Exception('Email send failed');
        }

        return true;
    }
}
```

---

## Dispatching Jobs

```php
use Resque;

// Dispatch job to queue
Resque::enqueue('default', 'Common\\Job\\SendEmailJob', [
    'to' => 'user@example.com',
    'subject' => 'Welcome',
    'body' => 'Welcome to our site!'
]);

// Dispatch to specific queue
Resque::enqueue('email', 'Common\\Job\\SendEmailJob', $args);

// Dispatch with delay (requires schedule plugin)
Resque::enqueueAt(time() + 300, 'default', 'Common\\Job\\SendEmailJob', $args);
```

---

## Job in Controller

```php
public function sendNotification()
{
    $ids = I('post.ids');
    if (empty($ids)) {
        $this->error('请选择要发送的用户');
    }

    $id_array = explode(',', $ids);

    foreach ($id_array as $id) {
        Resque::enqueue('notification', 'Common\\Job\\SendNotificationJob', [
            'user_id' => $id,
            'message' => '您有新消息'
        ]);
    }

    $this->success('发送任务已加入队列', U('index'));
}
```

---

## Batch Processing Job

```php
// Job 类文件 (如 BatchExportJob.php)

namespace Common\Job;

use Gy_Library\Job\BaseJob;

class BatchExportJob extends BaseJob
{
    public function perform()
    {
        $userId = $this->args['user_id'];
        $filters = $this->args['filters'];

        // Get data
        $list = D('Product')->where($filters)->select();

        // Generate export file
        $filename = 'export_' . date('YmdHis') . '.csv';
        $filepath = PUBLIC_PATH . '/uploads/export/' . $filename;

        $output = fopen($filepath, 'w');
        fputcsv($output, ['ID', '名称', '价格']);

        foreach ($list as $item) {
            fputcsv($output, [$item['id'], $item['name'], $item['price']]);
        }

        fclose($output);

        // Notify user
        Resque::enqueue('notification', 'Common\\Job\\NotifyJob', [
            'user_id' => $userId,
            'message' => '导出完成: ' . $filename,
            'download_url' => '/uploads/export/' . $filename
        ]);

        return true;
    }
}
```

---

## Job with Retry

```php
class ReliableJob extends BaseJob
{
    public function perform()
    {
        $maxRetries = 3;
        $attempt = $this->args['_attempt'] ?? 0;

        try {
            return $this->doWork();
        } catch (\Exception $e) {
            if ($attempt < $maxRetries) {
                // Retry with increment
                $args = $this->args;
                $args['_attempt'] = $attempt + 1;

                Resque::enqueue('default', get_class($this), $args);
                return true;
            }

            // Max retries reached
            throw $e;
        }
    }

    private function doWork()
    {
        // Actual work
    }
}
```

---

## Queue Management

```bash
# Check queue status
QUEUE_ENV=prod php app/queue_resque.php status

# Clear queue
QUEUE_ENV=prod php app/queue_resque.php clear

# Restart workers
QUEUE_ENV=prod php app/queue_resque.php restart
```

---

## Best Practices

1. **Keep jobs small** - Split large tasks
2. **Handle failures** - Log errors, notify users
3. **Use appropriate queues** - Separate by priority
4. **Monitor queue health** - Check worker status

---

## Related Rules

- [Pattern Redis Lock](pattern-redis-lock.md) - Distributed locking
- [Pattern Wall Class](pattern-wall-class.md) - External services
- [CRUD Batch Actions](../crud/crud-batch-actions.md) - Batch operations

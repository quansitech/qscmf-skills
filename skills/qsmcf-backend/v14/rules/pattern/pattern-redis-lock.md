---
title: Redis Lock Pattern (v14)
impact: HIGH
impactDescription: Required for concurrent operations
tags: pattern, redis, lock, v14
---

## Redis Lock Pattern (v14)

Distributed locking for concurrent operations in QSCMF v14.

### When to Use This Rule

- Preventing duplicate operations
- Batch processing with concurrency
- Critical section protection

---

## Basic Redis Lock

```php
use Qscmf\Lib\Redis\RedisLock;

public function batchProcess()
{
    $lock = new RedisLock('batch_process_' . $this->uid);

    if (!$lock->acquire()) {
        $this->error('操作进行中，请稍候');
    }

    try {
        // Critical section - only one process can execute
        $ids = I('post.ids');
        $id_array = explode(',', $ids);

        foreach ($id_array as $id) {
            $this->processItem($id);
        }

        $this->success('处理成功', U('index'));
    } catch (\Exception $e) {
        $this->error('处理失败: ' . $e->getMessage());
    } finally {
        $lock->release();
    }
}
```

---

## Lock with Timeout

```php
public function processWithTimeout()
{
    $lock = new RedisLock('process_' . $id, 30);  // 30 second timeout

    if (!$lock->acquire()) {
        $this->error('资源被锁定');
    }

    try {
        // Process with time limit
        $result = $this->doWork($id);
        $this->success('处理成功');
    } finally {
        $lock->release();
    }
}
```

---

## Lock in Model

```php
// app/Common/Model/OrderModel.class.php

class OrderModel extends GyListModel
{
    public function processOrder(int $orderId): bool
    {
        $lock = new RedisLock('order_process_' . $orderId, 60);

        if (!$lock->acquire()) {
            $this->error = '订单正在处理中';
            return false;
        }

        try {
            $this->startTrans();

            $order = $this->find($orderId);
            if ($order['status'] != DBCont::AUDIT_STATUS) {
                throw new \Exception('订单状态不正确');
            }

            // Process order logic...
            $this->where(['id' => $orderId])->save([
                'status' => DBCont::NORMAL_STATUS,
                'process_time' => time()
            ]);

            $this->commit();
            return true;
        } catch (\Exception $e) {
            $this->rollback();
            $this->error = $e->getMessage();
            return false;
        } finally {
            $lock->release();
        }
    }
}
```

---

## Preventing Duplicate Submissions

```php
public function save()
{
    $lockKey = 'form_submit_' . md5(json_encode(I('post.')));
    $lock = new RedisLock($lockKey, 5);

    if (!$lock->acquire()) {
        $this->error('请勿重复提交');
    }

    try {
        $data = I('post.');
        $result = parent::save($data);

        if ($result !== false) {
            $this->success('保存成功', U('index'));
        } else {
            $this->error('保存失败');
        }
    } finally {
        $lock->release();
    }
}
```

---

## Batch Processing with Lock

```php
public function batchExport()
{
    $lock = new RedisLock('export_' . $this->uid, 300);  // 5 minutes

    if (!$lock->acquire()) {
        $this->error('导出任务进行中，请稍候');
    }

    try {
        set_time_limit(0);

        $map = $this->buildSearchMap(I('get.'));
        $list = D('Product')->where($map)->select();

        // Generate export file
        $filename = $this->generateExport($list);

        $this->success('导出成功', U('download', ['file' => $filename]));
    } catch (\Exception $e) {
        $this->error('导出失败: ' . $e->getMessage());
    } finally {
        $lock->release();
    }
}
```

---

## Best Practices

1. **Always release lock** - Use try/finally
2. **Set appropriate timeout** - Prevent deadlocks
3. **Use unique lock keys** - Include resource identifier
4. **Handle lock failure** - Provide user feedback

---

## Related Rules

- [Pattern Abstract Base](pattern-abstract-base.md) - Base class pattern
- [Pattern Queue Job](pattern-queue-job.md) - Async processing
- [CRUD Batch Actions](../crud/crud-batch-actions.md) - Batch operations

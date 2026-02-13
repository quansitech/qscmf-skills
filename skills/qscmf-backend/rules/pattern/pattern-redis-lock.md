---
title: Redis Lock Pattern for Concurrency Control
impact: MEDIUM
impactDescription: Prevents race conditions in concurrent operations
tags: pattern, redis, lock, concurrency, both
---

## Redis Lock Pattern

Use RedisLock to prevent race conditions in concurrent operations.

**When to Use:**
- Inventory deduction (避免超卖)
- Resource allocation (避免重复分配)
- Batch operations (避免并发冲突)
- Unique constraints enforcement (避免重复创建)

**Pattern:**
```php
use Gy_Library\RedisLock;

public function save($id = null)
{
    $lock_key = 'product_save_' . ($id ?? 'new');
    $lock = new RedisLock($lock_key, 10); // 10秒超时

    if (!$lock->acquire()) {
        $this->error('操作频繁，请稍后再试');
        return false;
    }

    try {
        // 业务逻辑
        $result = parent::save($id);

        $lock->release();
        return $result;
    } catch (\Exception $e) {
        $lock->release();
        throw $e;
    }
}
```

**Idempotency Key Pattern:**
```php
// 使用唯一请求 ID 防止重复操作
$request_id = I('post.request_id');

if (S("processed_{$request_id}")) {
    return '重复请求';
}

S("processed_{$request_id}", true, 300); // 缓存5分钟
```

**Lock Options:**
```php
// 设置锁超时（秒）
$lock = new RedisLock($lock_key, 10);

// 检查锁状态
if ($lock->isLock()) {
    // 锁已被占用
}

// 强制释放锁
$lock->release();
```

**Best Practices:**
1. Keep lock time minimal (just cover critical section)
2. Always release lock in try-finally block
3. Use meaningful lock keys (include operation type and ID)
4. Set appropriate timeout based on operation complexity

**See Also:**
- [Abstract Base Pattern](pattern/pattern-abstract-base.md)

**Version Differences:**
- **v13/v14**: Same RedisLock API

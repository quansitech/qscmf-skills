---
title: Batch Actions Configuration
impact: HIGH
impactDescription: Used in 60% of table management operations
tags: crud, batch, actions, bulk, both
---

## Batch Actions Configuration

Implement batch operations (bulk actions) for table rows in QSCMF.

### When to Use This Rule

- You need to perform operations on multiple selected records
- You want to improve efficiency with bulk updates
- You need to implement batch delete, enable/disable, or custom actions
- You want to understand the complete batch actions system

---

## Batch Actions Overview

### What Are Batch Actions?

Batch actions allow users to:
- Select multiple rows using checkboxes
- Perform operations on all selected records at once
- Common operations: delete, enable, disable, export, custom actions

### Benefits

| Benefit | Description |
|---------|-------------|
| **Efficiency** | Update 100+ records with one click |
| **User Experience** | No need to edit each record individually |
| **Consistency** | Ensure all records updated with same logic |
| **Safety** | Confirmation dialogs prevent accidental bulk changes |

---

## v14 (AntdAdmin) Batch Actions

### Basic Batch Actions

```php
protected function tableContainer(\Gy_Library\Components\TableContainer $container): void
{
    // ... columns ...

    // Configure batch actions
    $container->setBatchActions([
        'enable' => [
            'title' => '批量启用',
            'confirm' => '确定要启用选中的记录吗?',
            'api' => U('batchEnable'),
            'icon' => 'CheckOutlined'
        ],
        'disable' => [
            'title' => '批量禁用',
            'confirm' => '确定要禁用选中的记录吗?',
            'api' => U('batchDisable'),
            'icon' => 'StopOutlined'
        ],
        'delete' => [
            'title' => '批量删除',
            'confirm' => '删除后无法恢复，确定要删除选中的记录吗?',
            'api' => U('batchDelete'),
            'danger' => true,
            'icon' => 'DeleteOutlined'
        ]
    ]);
}
```

### Batch Action Configuration Parameters

| Parameter | Type | Required | Description |
|-----------|------|-----------|-------------|
| `title` | string | ✅ Yes | Button label text |
| `api` | string | ✅ Yes | API endpoint URL |
| `confirm` | string | ❌ No | Confirmation message |
| `icon` | string | ❌ No | Ant Design icon name |
| `danger` | bool | ❌ No | Show as dangerous action (red) |
| `permission` | string | ❌ No | Permission node key |

---

## Batch Action Handlers

### Handler Method Signature

```php
public function batch{ActionName}()
{
    // 1. Get selected IDs
    // 2. Validate IDs
    // 3. Perform operation
    // 4. Return result
}
```

### Example 1: Batch Enable

```php
/**
 * Batch enable records
 */
public function batchEnable()
{
    $ids = I('post.ids');
    $ids = is_array($ids) ? $ids : explode(',', $ids);

    // Validate
    if (empty($ids)) {
        $this->error('请选择要操作的记录');
        return;
    }

    // Sanitize IDs
    $ids = array_map('intval', array_filter($ids));
    if (empty($ids)) {
        $this->error('无效的记录ID');
        return;
    }

    // Perform update
    $result = D('Product')->where([
        'id' => ['in', $ids]
    ])->setField('status', DBCont::NORMAL_STATUS);

    if ($result !== false) {
        $this->success('成功启用 ' . count($ids) . ' 条记录');
    } else {
        $this->error('操作失败，请重试');
    }
}
```

### Example 2: Batch Disable

```php
/**
 * Batch disable records
 */
public function batchDisable()
{
    $ids = I('post.ids');
    $ids = is_array($ids) ? $ids : explode(',', $ids);

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
        return;
    }

    $ids = array_map('intval', array_filter($ids));

    $result = D('Product')->where([
        'id' => ['in', $ids]
    ])->setField('status', DBCont::DISABLE_STATUS);

    if ($result !== false) {
        $this->success('成功禁用 ' . count($ids) . ' 条记录');
    } else {
        $this->error('操作失败，请重试');
    }
}
```

### Example 3: Batch Delete

```php
/**
 * Batch delete records
 */
public function batchDelete()
{
    $ids = I('post.ids');
    $ids = is_array($ids) ? $ids : explode(',', $ids);

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
        return;
    }

    $ids = array_map('intval', array_filter($ids));

    // Transaction for safety
    $model = D('Product');
    $model->startTrans();

    try {
        $count = 0;
        foreach ($ids as $id) {
            // Check if record exists
            $record = $model->find($id);
            if ($record) {
                // Trigger before delete callback
                if (method_exists($this, '_before_delete')) {
                    $this->_before_delete($id);
                }

                $result = $model->delete($id);
                if ($result !== false) {
                    $count++;

                    // Trigger after delete callback
                    if (method_exists($this, '_after_delete')) {
                        $this->_after_delete($id);
                    }
                }
            }
        }

        $model->commit();
        $this->success("成功删除 {$count} 条记录");

    } catch (\Exception $e) {
        $model->rollback();
        $this->error('删除失败: ' . $e->getMessage());
    }
}
```

### Example 4: Batch Update Field

```php
/**
 * Batch update specific field
 */
public function batchUpdateCategory()
{
    $ids = I('post.ids');
    $categoryId = I('post.category_id');

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
        return;
    }

    if (empty($categoryId)) {
        $this->error('请选择目标分类');
        return;
    }

    $ids = array_map('intval', array_filter($ids));

    $result = D('Product')->where([
        'id' => ['in', $ids]
    ])->setField('category_id', $categoryId);

    if ($result !== false) {
        $this->success('成功更新 ' . count($ids) . ' 条记录');
    } else {
        $this->error('操作失败');
    }
}
```

---

## Advanced Batch Actions

### Example 5: Batch Sync to External System

```php
/**
 * Batch sync to external service
 */
public function batchSyncToErp()
{
    $ids = I('post.ids');

    if (empty($ids)) {
        $this->error('请选择要同步的记录');
        return;
    }

    $ids = is_array($ids) ? $ids : explode(',', $ids);
    $ids = array_map('intval', array_filter($ids));

    $successCount = 0;
    $failedCount = 0;
    $results = [];

    foreach ($ids as $id) {
        $product = D('Product')->find($id);

        if (!$product) {
            $failedCount++;
            $results[] = "ID {$id}: 记录不存在";
            continue;
        }

        try {
            // Call external API
            $erpClient = new \App\Lib\ErpClient();
            $response = $erpClient->syncProduct($product);

            if ($response['success']) {
                D('Product')->where(['id' => $id])->save([
                    'sync_time' => date('Y-m-d H:i:s'),
                    'sync_status' => 1
                ]);
                $successCount++;
                $results[] = "ID {$id}: 同步成功";
            } else {
                $failedCount++;
                $results[] = "ID {$id}: " . $response['message'];
            }

        } catch (\Exception $e) {
            $failedCount++;
            $results[] = "ID {$id}: " . $e->getMessage();
        }
    }

    // Return detailed result
    $this->success("同步完成：成功 {$successCount} 条，失败 {$failedCount} 条", $results);
}
```

### Example 6: Batch Export

```php
/**
 * Batch export records
 */
public function batchExport()
{
    $ids = I('post.ids');

    if (empty($ids)) {
        $this->error('请选择要导出的记录');
        return;
    }

    $ids = is_array($ids) ? $ids : explode(',', $ids);
    $ids = array_map('intval', array_filter($ids));

    // Fetch records
    $products = D('Product')->where([
        'id' => ['in', $ids]
    ])->select();

    if (empty($products)) {
        $this->error('没有找到相关记录');
        return;
    }

    // Generate Excel
    $excel = new \PHPExcel();
    $sheet = $excel->getActiveSheet();

    // Header
    $sheet->setCellValue('A1', 'ID');
    $sheet->setCellValue('B1', '产品名称');
    $sheet->setCellValue('C1', '价格');
    $sheet->setCellValue('D1', '库存');
    $sheet->setCellValue('E1', '状态');

    // Data
    $row = 2;
    foreach ($products as $product) {
        $sheet->setCellValue('A' . $row, $product['id']);
        $sheet->setCellValue('B' . $row, $product['name']);
        $sheet->setCellValue('C' . $row, $product['price']);
        $sheet->setCellValue('D' . $row, $product['stock']);
        $sheet->setCellValue('E' . $row, $product['status'] == 1 ? '启用' : '禁用');
        $row++;
    }

    // Save file
    $filename = 'products_' . date('YmdHis') . '.xlsx';
    $writer = \PHPExcel_IOFactory::createWriter($excel, 'Excel2007');
    $writer->save('./uploads/' . $filename);

    $this->success('导出成功', ['download_url' => '/uploads/' . $filename]);
}
```

### Example 7: Batch Copy/Duplicate

```php
/**
 * Batch copy records
 */
public function batchCopy()
{
    $ids = I('post.ids');

    if (empty($ids)) {
        $this->error('请选择要复制的记录');
        return;
    }

    $ids = is_array($ids) ? $ids : explode(',', $ids);
    $ids = array_map('intval', array_filter($ids));

    $model = D('Product');
    $model->startTrans();

    try {
        $copyCount = 0;

        foreach ($ids as $id) {
            $source = $model->find($id);

            if (!$source) {
                continue;
            }

            // Create copy
            $copy = $source->data();
            unset($copy['id']); // Remove ID to create new record
            $copy['name'] .= ' (副本)';
            $copy['create_time'] = date('Y-m-d H:i:s');

            $newId = $model->add($copy);

            if ($newId) {
                $copyCount++;

                // Copy related data if needed
                $this->copyProductImages($id, $newId);
                $this->copyProductSpecs($id, $newId);
            }
        }

        $model->commit();
        $this->success("成功复制 {$copyCount} 条记录");

    } catch (\Exception $e) {
        $model->rollback();
        $this->error('复制失败: ' . $e->getMessage());
    }
}

protected function copyProductImages($sourceId, $targetId)
{
    $images = D('ProductImage')->where(['product_id' => $sourceId])->select();

    foreach ($images as $image) {
        D('ProductImage')->add([
            'product_id' => $targetId,
            'image_url' => $image['image_url'],
            'sort' => $image['sort']
        ]);
    }
}
```

---

## v13 (Legacy jQuery) Batch Actions

### Basic Batch Actions (v13)

```php
public function index()
{
    $builder = $this->builder();

    // ... columns ...

    // Add batch buttons
    $builder->addBatchButton('forbid', [
        'title' => '批量禁用',
        'confirm' => '确定要禁用选中的记录吗?',
        'handler' => 'batchDisable' // Controller method
    ]);

    $builder->addBatchButton('resume', [
        'title' => '批量启用',
        'confirm' => '确定要启用选中的记录吗?',
        'handler' => 'batchEnable'
    ]);

    $builder->addBatchButton('delete', [
        'title' => '批量删除',
        'confirm' => '删除后无法恢复，确定要删除选中的记录吗?',
        'handler' => 'batchDelete',
        'class' => 'btn-danger'
    ]);

    $builder->display();
}
```

### Handler Method (v13)

```php
public function batchDisable()
{
    $ids = I('post.ids');
    $ids = is_array($ids) ? $ids : explode(',', $ids);

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
        return;
    }

    // Convert to comma-separated for ThinkPHP
    $ids = implode(',', array_map('intval', $ids));

    $result = D('Product')->where([
        "id IN ({$ids})"
    ])->setField('status', 0);

    if ($result !== false) {
        $this->success('操作成功');
    } else {
        $this->error('操作失败');
    }
}
```

---

## Batch Action Best Practices

### 1. Always Validate Input

```php
public function batchDelete()
{
    $ids = I('post.ids');

    // Check if empty
    if (empty($ids)) {
        $this->error('请选择要操作的记录');
        return;
    }

    // Validate array format
    $ids = is_array($ids) ? $ids : explode(',', $ids);

    // Sanitize to integers
    $ids = array_map('intval', array_filter($ids));

    // Check again after sanitization
    if (empty($ids)) {
        $this->error('无效的记录ID');
        return;
    }

    // Proceed with operation...
}
```

### 2. Use Transactions for Destructive Operations

```php
public function batchDelete()
{
    // ... validation ...

    $model = D('Product');
    $model->startTrans();

    try {
        $count = 0;
        foreach ($ids as $id) {
            if ($model->delete($id)) {
                $count++;
            }
        }

        $model->commit();
        $this->success("成功删除 {$count} 条记录");

    } catch (\Exception $e) {
        $model->rollback();
        $this->error('删除失败: ' . $e->getMessage());
    }
}
```

### 3. Implement Progress Feedback for Long Operations

```php
public function batchLongOperation()
{
    $ids = I('post.ids');

    set_time_limit(300); // 5 minutes

    $total = count($ids);
    $processed = 0;
    $results = [];

    foreach ($ids as $id) {
        // Process record
        $result = $this->processRecord($id);
        $results[] = $result;
        $processed++;

        // Update progress every 10 records
        if ($processed % 10 === 0) {
            // Save progress to cache
            S('batch_progress_' . session_id(), [
                'total' => $total,
                'processed' => $processed,
                'percent' => round($processed / $total * 100, 1)
            ]);
        }
    }

    // Clear progress
    S('batch_progress_' . session_id(), null);

    $this->success("操作完成: {$processed}/{$total}", $results);
}
```

### 4. Add Permission Checks

```php
public function batchDelete()
{
    // Check permission
    if (!$this->checkAuth('Product/batchDelete')) {
        $this->error('您没有权限执行此操作');
        return;
    }

    $ids = I('post.ids');

    // ... proceed with operation
}
```

### 5. Provide Detailed Feedback

```php
public function batchEnable()
{
    $ids = I('post.ids');

    $results = [
        'success' => [],
        'failed' => []
    ];

    foreach ($ids as $id) {
        $product = D('Product')->find($id);

        if (!$product) {
            $results['failed'][] = "ID {$id}: 记录不存在";
            continue;
        }

        $result = D('Product')->where(['id' => $id])->save([
            'status' => 1
        ]);

        if ($result !== false) {
            $results['success'][] = "ID {$id}: " . $product['name'];
        } else {
            $results['failed'][] = "ID {$id}: 更新失败";
        }
    }

    $successCount = count($results['success']);
    $failedCount = count($results['failed']);

    if ($failedCount > 0) {
        $this->warning("部分成功：成功 {$successCount} 条，失败 {$failedCount} 条", $results);
    } else {
        $this->success("全部成功：共 {$successCount} 条记录");
    }
}
```

---

## Complete Batch Action Configuration

### v14 Full Example

```php
<?php
// app/Admin/Controller/ProductController.class.php

namespace Admin\Controller;
use Gy_Library\Components\TableContainer;

class ProductController extends \QsAdmin\Controller\QsListController
{
    protected $tableName = 'product';

    protected function tableContainer(TableContainer $container): void
    {
        $container->text('id', 'ID')->setWidth(80);
        $container->text('name', '产品名称')->setEllipsis(true);
        $container->text('price', '价格');
        $container->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList())
            ->setBadge([1 => 'success', 0 => 'default']);

        // Configure batch actions
        $container->setBatchActions([
            'enable' => [
                'title' => '批量启用',
                'confirm' => '确定要启用选中的产品吗?',
                'api' => U('batchEnable'),
                'icon' => 'CheckOutlined',
                'permission' => 'Product/batchEnable'
            ],
            'disable' => [
                'title' => '批量禁用',
                'confirm' => '确定要禁用选中的产品吗?',
                'api' => U('batchDisable'),
                'icon' => 'StopOutlined',
                'permission' => 'Product/batchDisable'
            ],
            'setHot' => [
                'title' => '设为热销',
                'confirm' => '确定要将选中产品设为热销吗?',
                'api' => U('batchSetHot'),
                'icon' => 'FireOutlined'
            ],
            'setNew' => [
                'title' => '设为新品',
                'confirm' => '确定要将选中产品设为新品吗?',
                'api' => U('batchSetNew'),
                'icon' => 'StarOutlined'
            ],
            'sync' => [
                'title' => '同步到ERP',
                'confirm' => '确定要将选中产品同步到ERP系统吗?',
                'api' => U('batchSyncErp'),
                'icon' => 'SyncOutlined'
            ],
            'export' => [
                'title' => '导出Excel',
                'api' => U('batchExport'),
                'icon' => 'DownloadOutlined',
                'confirm' => false // No confirmation for export
            ],
            'delete' => [
                'title' => '批量删除',
                'confirm' => '删除后无法恢复，确定要删除选中的产品吗?',
                'api' => U('batchDelete'),
                'danger' => true,
                'icon' => 'DeleteOutlined',
                'permission' => 'Product/batchDelete'
            ]
        ]);
    }

    /**
     * Batch enable products
     */
    public function batchEnable()
    {
        $ids = I('post.ids');
        $ids = is_array($ids) ? $ids : explode(',', $ids);

        if (empty($ids)) {
            $this->error('请选择要操作的产品');
            return;
        }

        $ids = array_map('intval', array_filter($ids));

        $result = D('Product')->where([
            'id' => ['in', $ids]
        ])->setField('status', DBCont::NORMAL_STATUS);

        if ($result !== false) {
            $this->success('成功启用 ' . count($ids) . ' 个产品');
        } else {
            $this->error('操作失败，请重试');
        }
    }

    /**
     * Batch disable products
     */
    public function batchDisable()
    {
        $ids = I('post.ids');
        $ids = is_array($ids) ? $ids : explode(',', $ids);

        if (empty($ids)) {
            $this->error('请选择要操作的产品');
            return;
        }

        $ids = array_map('intval', array_filter($ids));

        $result = D('Product')->where([
            'id' => ['in', $ids]
        ])->setField('status', DBCont::DISABLE_STATUS);

        if ($result !== false) {
            $this->success('成功禁用 ' . count($ids) . ' 个产品');
        } else {
            $this->error('操作失败，请重试');
        }
    }

    /**
     * Batch set as hot
     */
    public function batchSetHot()
    {
        $ids = I('post.ids');
        $ids = is_array($ids) ? $ids : explode(',', $ids);

        if (empty($ids)) {
            $this->error('请选择要操作的产品');
            return;
        }

        $ids = array_map('intval', array_filter($ids));

        $result = D('Product')->where([
            'id' => ['in', $ids]
        ])->setField('is_hot', 1);

        if ($result !== false) {
            $this->success('成功将 ' . count($ids) . ' 个产品设为热销');
        } else {
            $this->error('操作失败，请重试');
        }
    }

    /**
     * Batch set as new
     */
    public function batchSetNew()
    {
        $ids = I('post.ids');
        $ids = is_array($ids) ? $ids : explode(',', $ids);

        if (empty($ids)) {
            $this->error('请选择要操作的产品');
            return;
        }

        $ids = array_map('intval', array_filter($ids));

        $result = D('Product')->where([
            'id' => ['in', $ids]
        ])->setField('is_new', 1);

        if ($result !== false) {
            $this->success('成功将 ' . count($ids) . ' 个产品设为新品');
        } else {
            $this->error('操作失败，请重试');
        }
    }

    /**
     * Batch delete products
     */
    public function batchDelete()
    {
        $ids = I('post.ids');
        $ids = is_array($ids) ? $ids : explode(',', $ids);

        if (empty($ids)) {
            $this->error('请选择要删除的产品');
            return;
        }

        $ids = array_map('intval', array_filter($ids));

        $model = D('Product');
        $model->startTrans();

        try {
            $count = 0;
            foreach ($ids as $id) {
                $product = $model->find($id);
                if ($product) {
                    if ($model->delete($id)) {
                        $count++;
                    }
                }
            }

            $model->commit();
            $this->success("成功删除 {$count} 个产品");

        } catch (\Exception $e) {
            $model->rollback();
            $this->error('删除失败: ' . $e->getMessage());
        }
    }
}
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|--------|----------|
| Batch action not triggered | Wrong API URL or method name | Check API path and method name match |
| "ids" parameter empty | Frontend not sending IDs | Verify form submission format |
| Only first ID processed | Array not properly handled | Check `is_array()` and `explode()` logic |
| Transaction deadlock | Long-running operation without timeout | Add `set_time_limit()` and optimize queries |
| Partial updates failing | No error handling for individual records | Implement try-catch for each record |
| Permission denied | Missing permission node | Add permission check or configure qs_node |
| Memory exhausted | Processing too many records at once | Implement batch processing (chunking) |

---

## Version Differences

| Feature | v14 (AntdAdmin) | v13 (Legacy) |
|---------|------------------|--------------|
| **API** | `setBatchActions()` | `addBatchButton()` |
| **Configuration** | Array of action configs | Individual button calls |
| **Confirmation** | Built-in with `confirm` key | Manual HTML confirm |
| **Icons** | Ant Design icon names | Font Awesome or Glyphicon |
| **Danger style** | `danger => true` | `class => 'btn-danger'` |
| **Permission check** | `permission` key | Manual check in handler |
| **Progress feedback** | Built-in progress support | Manual implementation |
| **Error handling** | JSON response | HTML/JSON mixed |

---

## Performance Considerations

### For Large Batch Operations

```php
// Instead of processing all at once
public function batchDelete()
{
    $ids = I('post.ids');

    // Process in chunks of 100
    $chunks = array_chunk($ids, 100);
    $totalDeleted = 0;

    foreach ($chunks as $chunk) {
        $deleted = D('Product')->where([
            'id' => ['in', $chunk]
        ])->delete();
        $totalDeleted += $deleted;

        // Prevent timeout
        set_time_limit(30);
        sleep(1); // Brief pause
    }

    $this->success("共删除 {$totalDeleted} 条记录");
}
```

### Using Queue for Async Processing

```php
public function batchAsyncExport()
{
    $ids = I('post.ids');

    // Push to queue
    $jobId = Queue::push('App\Jobs\BatchExportJob', [
        'ids' => $ids,
        'user_id' => session('user.id')
    ]);

    $this->success('导出任务已创建，任务ID: ' . $jobId);
}

// Job class
class BatchExportJob
{
    public function perform($args)
    {
        $ids = $args['ids'];
        // Perform export...
        // Notify user when complete
    }
}
```

---

## See Also

- [Table Columns v14](crud-table-columns-v14.md) - Table configuration
- [Admin Controllers](../../references/admin-controllers.md) - Controller patterns
- [Queue Jobs](../pattern/pattern-queue-job.md) - Async job processing
- [Redis Lock](../pattern/pattern-redis-lock.md) - Concurrency control

---

## Iron Law

```
BATCH OPERATIONS MUST USE TRANSACTIONS AND VALIDATION
```

---
title: Batch Actions (v13)
impact: MEDIUM
impactDescription: Required for bulk operations
tags: crud, batch, actions, v13
---

## Batch Actions (v13)

Implement batch operations for v13 admin pages.

### When to Use This Rule

- Implementing bulk delete/update
- Adding batch status change
- Processing multiple records

---

## Enable Checkbox Selection

```php
public function index()
{
    $builder = $this->builder();

    // Enable checkbox column
    $builder->setCheckBox(true);

    // With conditional disable
    $builder->setCheckBox(true, function($attr, $data) {
        if ($data['is_system'] == 1) {
            $attr['disabled'] = 'disabled';
        }
        return $attr;
    });

    // Using helper method
    $builder->setCheckBox(true, ListBuilder::genCheckBoxDisableCb('is_system', 1));
}
```

---

## Batch Buttons

```php
// Batch delete
$builder->addTopButton('delete', [
    'title' => '删除',
    'href' => U('delete'),
    'ajax' => true,
    'confirm' => '确定要删除选中的记录吗？'
]);

// Batch disable
$builder->addTopButton('forbid', [
    'title' => '禁用',
    'href' => U('toggleStatus', ['type' => 'forbid']),
    'ajax' => true
]);

// Batch enable
$builder->addTopButton('resume', [
    'title' => '启用',
    'href' => U('toggleStatus', ['type' => 'resume']),
    'ajax' => true
]);

// Custom batch action with selection required
$builder->addTopButton('custom', [
    'title' => '批量导出',
    'href' => U('batchExport'),
    'class' => 'btn btn-info must-select-item',
    'must-select-msg' => '请选择要导出的数据'
]);
```

---

## Batch Delete

```php
public function delete()
{
    $ids = I('get.ids');
    if (empty($ids)) {
        $this->error('请选择要删除的记录');
    }

    $id_array = explode(',', $ids);
    $id_array = array_map('intval', $id_array);

    // Check dependencies
    foreach ($id_array as $id) {
        if (D('Order')->where(['product_id' => $id])->count() > 0) {
            $this->error('ID ' . $id . ' 存在关联订单，无法删除');
        }
    }

    $result = D('Product')->where(['id' => ['IN', $id_array]])->delete();

    if ($result !== false) {
        $this->success('删除成功', U('index'));
    } else {
        $this->error('删除失败');
    }
}
```

---

## Batch Status Change

```php
public function toggleStatus()
{
    $ids = I('get.ids');
    $type = I('get.type');

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    $id_array = explode(',', $ids);
    $status = ($type === 'forbid') ? DBCont::DISABLE_STATUS : DBCont::NORMAL_STATUS;

    $result = D('Product')->where(['id' => ['IN', $id_array]])->setField('status', $status);

    if ($result !== false) {
        $this->success('操作成功', U('index'));
    } else {
        $this->error('操作失败');
    }
}
```

---

## Batch Update Field

```php
public function batchUpdate()
{
    $ids = I('post.ids');
    $field = I('post.field');
    $value = I('post.value');

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    $id_array = explode(',', $ids);
    $result = D('Product')->where(['id' => ['IN', $id_array]])->setField($field, $value);

    if ($result !== false) {
        $this->success('操作成功', U('index'));
    } else {
        $this->error('操作失败');
    }
}
```

---

## Batch Export

```php
public function batchExport()
{
    $ids = I('get.ids');
    if (empty($ids)) {
        $this->error('请选择要导出的记录');
    }

    $id_array = explode(',', $ids);
    $list = D('Product')->where(['id' => ['IN', $id_array]])->select();

    $filename = 'products_' . date('YmdHis') . '.csv';
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="' . $filename . '"');

    $output = fopen('php://output', 'w');
    // BOM for Excel UTF-8
    fprintf($output, chr(0xEF) . chr(0xBB) . chr(0xBF));

    // Header
    fputcsv($output, ['ID', '名称', '价格', '状态']);

    // Data
    foreach ($list as $item) {
        fputcsv($output, [
            $item['id'],
            $item['name'],
            $item['price'],
            DBCont::getStatusList()[$item['status']] ?? ''
        ]);
    }

    fclose($output);
    exit;
}
```

---

## Batch with Transaction

```php
public function batchProcess()
{
    $ids = I('post.ids');
    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    $id_array = explode(',', $ids);

    D('Product')->startTrans();
    try {
        foreach ($id_array as $id) {
            // Process each record
            $product = D('Product')->find($id);
            if (!$product) {
                continue;
            }

            // Update related data
            D('ProductLog')->add([
                'product_id' => $id,
                'action' => 'batch_process',
                'create_time' => time()
            ]);
        }

        // Update status
        D('Product')->where(['id' => ['IN', $id_array]])->setField('processed', 1);

        D('Product')->commit();
        $this->success('处理成功', U('index'));
    } catch (\Exception $e) {
        D('Product')->rollback();
        $this->error('处理失败: ' . $e->getMessage());
    }
}
```

---

## Related Rules

- [ListBuilder API](../listbuilder-api.md) - Button configuration
- [CRUD Table Columns](crud-table-columns-v13.md) - Column configuration

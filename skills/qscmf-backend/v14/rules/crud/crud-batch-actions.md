---
title: Batch Actions (v14)
impact: MEDIUM
impactDescription: Required for bulk operations
tags: crud, batch, actions, v14, antdadmin
---

## Batch Actions (v14)

Implement batch operations for v14 admin pages using AntdAdmin Component API.

### When to Use This Rule

- Implementing bulk delete/update
- Adding batch status change
- Processing multiple records
- Exporting selected data

---

## Enable Row Selection

In v14, row selection is automatically enabled when batch actions are added. The framework handles checkbox rendering.

```php
use AntdAdmin\Component\Table;

$table->actions(function (Table\ActionsContainer $container) {
    // Adding batch actions automatically enables row selection
    $container->delete();  // Batch delete
    $container->forbid();  // Batch disable
    $container->resume();  // Batch enable
});
```

---

## Built-in Batch Actions

### Basic Batch Actions

```php
$table->actions(function (Table\ActionsContainer $container) {
    // Add new button
    $container->button('新增')
        ->setProps(['type' => 'primary'])
        ->modal((new Modal())
            ->setWidth('800px')
            ->setUrl(U('add'))
            ->setTitle('新增'));

    // Batch disable
    $container->forbid();

    // Batch enable
    $container->resume();

    // Batch delete
    $container->delete();

    // Save inline edits
    $container->editSave();
});
```

### Built-in Action Reference

| Action | Description | Handler |
|--------|-------------|---------|
| `forbid()` | Batch disable records | Auto-handled by model |
| `resume()` | Batch enable records | Auto-handled by model |
| `delete()` | Batch delete records | Auto-handled by model |
| `editSave()` | Save inline edits | Auto-handled by model |

---

## Custom Batch Actions

### Custom Batch Button

```php
$table->actions(function (Table\ActionsContainer $container) {
    // Custom batch action with selection required
    $container->button('批量审核')
        ->setProps(['type' => 'primary'])
        ->request('post', U('batchAudit'))
        ->setConfirm('确定要批量审核通过吗？')
        ->setRequireSelection(true, '请选择要审核的记录');

    // Custom batch action with download
    $container->button('导出选中')
        ->setProps(['type' => 'default'])
        ->request('post', U('batchExport'))
        ->setDownload(true)
        ->setRequireSelection(true, '请选择要导出的数据');

    // Custom batch action without selection
    $container->button('导出全部')
        ->setProps(['type' => 'default'])
        ->request('get', U('exportAll'))
        ->setDownload(true);
});
```

### Batch Action Handler

```php
public function batchAudit()
{
    $ids = I('post.ids');

    if (empty($ids)) {
        $this->error('请选择要审核的记录');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);
    $id_array = array_map('intval', $id_array);

    // Check if records can be audited
    $pending_count = D('Product')->where([
        'id' => ['in', $id_array],
        'status' => DBCont::AUDIT_STATUS
    ])->count();

    if ($pending_count != count($id_array)) {
        $this->error('部分记录不在待审核状态');
    }

    // Update status
    $result = D('Product')->where([
        'id' => ['in', $id_array]
    ])->setField('status', DBCont::NORMAL_STATUS);

    if ($result !== false) {
        $this->success('批量审核成功');
    } else {
        $this->error('批量审核失败');
    }
}
```

---

## Batch Delete

### Basic Batch Delete

```php
// In actions configuration
$container->delete();

// Handler (auto-generated, but can be customized)
public function delete()
{
    $ids = I('post.ids');

    if (empty($ids)) {
        $this->error('请选择要删除的记录');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);
    $id_array = array_map('intval', $id_array);

    // Check dependencies before delete
    foreach ($id_array as $id) {
        if (D('Order')->where(['product_id' => $id])->count() > 0) {
            $this->error('ID ' . $id . ' 存在关联订单，无法删除');
        }
    }

    $result = D('Product')->where(['id' => ['in', $id_array]])->delete();

    if ($result !== false) {
        $this->success('删除成功');
    } else {
        $this->error('删除失败');
    }
}
```

### Soft Delete (Status Change)

```php
public function delete()
{
    $ids = I('post.ids');

    if (empty($ids)) {
        $this->error('请选择要删除的记录');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);

    // Soft delete by setting status
    $result = D('Product')->where(['id' => ['in', $id_array]])
        ->setField('status', DBCont::DELETED_STATUS);

    if ($result !== false) {
        $this->success('删除成功');
    } else {
        $this->error('删除失败');
    }
}
```

---

## Batch Status Change

### Toggle Status

```php
public function toggleStatus()
{
    $ids = I('post.ids');
    $type = I('post.type', 'forbid');

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);
    $status = ($type === 'forbid')
        ? DBCont::FORBIDDEN_STATUS
        : DBCont::NORMAL_STATUS;

    $result = D('Product')->where(['id' => ['in', $id_array]])
        ->setField('status', $status);

    if ($result !== false) {
        $this->success('操作成功');
    } else {
        $this->error('操作失败');
    }
}
```

### Custom Status Update

```php
public function batchUpdateStatus()
{
    $ids = I('post.ids');
    $status = I('post.status');

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    if (!in_array($status, [0, 1, 2])) {
        $this->error('状态值不正确');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);

    $result = D('Product')->where(['id' => ['in', $id_array]])
        ->setField('status', $status);

    if ($result !== false) {
        $this->success('操作成功');
    } else {
        $this->error('操作失败');
    }
}
```

---

## Batch Field Update

### Update Single Field

```php
public function batchUpdateField()
{
    $ids = I('post.ids');
    $field = I('post.field');
    $value = I('post.value');

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    // Validate field name (prevent SQL injection)
    $allowed_fields = ['sort', 'is_recommend', 'is_hot'];
    if (!in_array($field, $allowed_fields)) {
        $this->error('字段不允许修改');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);

    $result = D('Product')->where(['id' => ['in', $id_array]])
        ->setField($field, $value);

    if ($result !== false) {
        $this->success('操作成功');
    } else {
        $this->error('操作失败');
    }
}
```

### Update Multiple Fields

```php
public function batchUpdate()
{
    $ids = I('post.ids');
    $data = I('post.data');

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);

    // Validate data
    $update_data = [];
    if (isset($data['cate_id'])) {
        $update_data['cate_id'] = intval($data['cate_id']);
    }
    if (isset($data['status'])) {
        $update_data['status'] = intval($data['status']);
    }

    if (empty($update_data)) {
        $this->error('没有要更新的数据');
    }

    $result = D('Product')->where(['id' => ['in', $id_array]])
        ->save($update_data);

    if ($result !== false) {
        $this->success('操作成功');
    } else {
        $this->error('操作失败');
    }
}
```

---

## Batch Export

### Export Selected Records

```php
public function batchExport()
{
    $ids = I('post.ids');

    if (empty($ids)) {
        $this->error('请选择要导出的记录');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);
    $list = D('Product')->where(['id' => ['in', $id_array]])->select();

    $filename = 'products_' . date('YmdHis') . '.csv';

    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="' . $filename . '"');

    $output = fopen('php://output', 'w');

    // BOM for Excel UTF-8
    fprintf($output, chr(0xEF) . chr(0xBB) . chr(0xBF));

    // Header row
    fputcsv($output, ['ID', '商品名称', '分类', '价格', '库存', '状态']);

    // Data rows
    foreach ($list as $item) {
        fputcsv($output, [
            $item['id'],
            $item['name'],
            D('Category')->where(['id' => $item['cate_id']])->getField('name'),
            $item['price'],
            $item['stock'],
            DBCont::getStatusList()[$item['status']] ?? ''
        ]);
    }

    fclose($output);
    exit;
}
```

### Export with Excel (PhpSpreadsheet)

```php
use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;

public function batchExportExcel()
{
    $ids = I('post.ids');

    if (empty($ids)) {
        $this->error('请选择要导出的记录');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);
    $list = D('Product')->where(['id' => ['in', $id_array]])->select();

    $spreadsheet = new Spreadsheet();
    $sheet = $spreadsheet->getActiveSheet();

    // Header row
    $sheet->setCellValue('A1', 'ID');
    $sheet->setCellValue('B1', '商品名称');
    $sheet->setCellValue('C1', '价格');
    $sheet->setCellValue('D1', '库存');
    $sheet->setCellValue('E1', '状态');

    // Data rows
    $row = 2;
    foreach ($list as $item) {
        $sheet->setCellValue('A' . $row, $item['id']);
        $sheet->setCellValue('B' . $row, $item['name']);
        $sheet->setCellValue('C' . $row, $item['price']);
        $sheet->setCellValue('D' . $row, $item['stock']);
        $sheet->setCellValue('E' . $row, DBCont::getStatusList()[$item['status']] ?? '');
        $row++;
    }

    $filename = 'products_' . date('YmdHis') . '.xlsx';

    header('Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    header('Content-Disposition: attachment; filename="' . $filename . '"');

    $writer = new Xlsx($spreadsheet);
    $writer->save('php://output');
    exit;
}
```

---

## Batch Operations with Async Jobs

### Pattern: Selection-Based Async Processing

Use `relateSelection()` to pass selected IDs to async job handlers:

```php
$table->actions(function (Table\ActionsContainer $container) {
    // Dispatch async job for selected items
    $container->button('批量处理')
        ->relateSelection()
        ->request('post', U('batchProcess'), [
            'selection' => '__id__',
            'context' => $this->getContext(),
        ], null, '确定要批量处理吗？');
});
```

### Handler Pattern

```php
public function batchProcess()
{
    $ids = I('post.selection');
    $context = I('post.context');

    if (empty($ids)) {
        $this->error('请选择要处理的记录');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);

    // Dispatch to queue
    foreach ($id_array as $id) {
        YourJob::dispatch($id, $context);
    }

    $this->success('已提交处理队列');
}
```

---

## Batch with Transaction

### Safe Batch Processing

```php
public function batchProcess()
{
    $ids = I('post.ids');

    if (empty($ids)) {
        $this->error('请选择要操作的记录');
    }

    $id_array = is_array($ids) ? $ids : explode(',', $ids);
    $model = D('Product');

    $model->startTrans();

    try {
        foreach ($id_array as $id) {
            $product = $model->find($id);
            if (!$product) {
                continue;
            }

            // Process each record
            $process_result = $this->processProduct($product);

            if (!$process_result) {
                throw new \Exception('处理商品 ' . $id . ' 失败');
            }

            // Log the action
            D('ProductLog')->add([
                'product_id' => $id,
                'action' => 'batch_process',
                'create_time' => time()
            ]);
        }

        // Update status after successful processing
        $model->where(['id' => ['in', $id_array]])
            ->setField('processed', 1);

        $model->commit();
        $this->success('处理成功');
    } catch (\Exception $e) {
        $model->rollback();
        $this->error('处理失败: ' . $e->getMessage());
    }
}

protected function processProduct($product)
{
    // Custom processing logic
    return true;
}
```

---

## Complete Example

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;
use AntdAdmin\Component\Modal\Modal;
use Gy_Library\DBCont;

class ProductController extends QsListController
{
    protected $modelName = 'Product';

    public function index()
    {
        $map = [];
        $this->buildSearchWhere(I('get.'), $map);

        $model = D('Product')->where($map);
        $count = $model->count();
        $page = new \Gy_Library\GyPage($count);
        $data_list = $model
            ->order('id desc')
            ->page($page->nowPage, $page->listRows)
            ->select();

        $table = new Table();
        $table->setMetaTitle('商品列表')
            ->actions(function (Table\ActionsContainer $container) {
                // Add new
                $container->button('新增')
                    ->setProps(['type' => 'primary'])
                    ->modal((new Modal())
                        ->setWidth('800px')
                        ->setUrl(U('add'))
                        ->setTitle('新增商品'));

                // Built-in batch actions
                $container->forbid();
                $container->resume();
                $container->delete();

                // Custom batch actions
                $container->button('批量审核')
                    ->setProps(['type' => 'default'])
                    ->request('post', U('batchAudit'))
                    ->setConfirm('确定要批量审核通过吗？');

                $container->button('导出选中')
                    ->setProps(['type' => 'default'])
                    ->request('post', U('batchExport'));

                // Save inline edits
                $container->editSave();
            })
            ->columns(function (Table\ColumnsContainer $container) {
                $container->text('id', 'ID');
                $container->text('product_name', '商品名称');
                $container->select('status', '状态')
                    ->setValueEnum(DBCont::getStatusList())
                    ->setBadge([1 => 'success', 0 => 'default']);
                $container->number('sort', '排序')
                    ->editable();
                $container->datetime('create_time', '创建时间');
                $container->action('', '操作')
                    ->actions(function (Table\ColumnType\ActionsContainer $container) {
                        $container->edit()->modal(
                            (new Modal())
                                ->setWidth('800px')
                                ->setUrl(U('edit', ['id' => '__id__']))
                                ->setTitle('编辑')
                        );
                        $container->delete();
                    });
            })
            ->setDataSource($data_list)
            ->setPagination(new Pagination($page->nowPage, $page->listRows, $count))
            ->render();
    }

    public function batchAudit()
    {
        $ids = I('post.ids');

        if (empty($ids)) {
            $this->error('请选择要审核的记录');
        }

        $id_array = is_array($ids) ? $ids : explode(',', $ids);

        $result = D('Product')->where(['id' => ['in', $id_array]])
            ->setField('status', DBCont::NORMAL_STATUS);

        if ($result !== false) {
            $this->success('批量审核成功');
        } else {
            $this->error('批量审核失败');
        }
    }

    public function batchExport()
    {
        $ids = I('post.ids');

        if (empty($ids)) {
            $this->error('请选择要导出的记录');
        }

        $id_array = is_array($ids) ? $ids : explode(',', $ids);
        $list = D('Product')->where(['id' => ['in', $id_array]])->select();

        $filename = 'products_' . date('YmdHis') . '.csv';

        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="' . $filename . '"');

        $output = fopen('php://output', 'w');
        fprintf($output, chr(0xEF) . chr(0xBB) . chr(0xBF));

        fputcsv($output, ['ID', '商品名称', '价格', '状态']);

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

    protected function buildSearchWhere($get_data, &$map)
    {
        if (!empty($get_data['product_name'])) {
            $map['product_name'] = ['like', '%' . $get_data['product_name'] . '%'];
        }
        if (isset($get_data['status']) && $get_data['status'] !== '') {
            $map['status'] = $get_data['status'];
        }
    }
}
```

---

## Related Rules

- [Table Columns](crud-table-columns.md) - Column configuration and custom renderers
- [AntdAdmin Components](../antdadmin.md) - Component reference
- [Form Validation](crud-form-validation.md) - Form validation rules

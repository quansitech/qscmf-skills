# Troubleshooting Guide

Comprehensive troubleshooting guide for AntdAdmin components.

## Table Issues

### Column not showing

**Symptoms**: Column header appears but no data, or column doesn't appear at all

**Checklist**:
- ✅ `dataIndex` matches field name in data source exactly
- ✅ Container closure syntax is correct: `function ($container) { ... }`
- ✅ `setDataSource()` is called with valid array
- ✅ Data contains the field you're trying to display
- ✅ Field name is spelled correctly (case-sensitive)

**Debug**:
```php
// Check your data
var_dump($tableData);
exit;

// Verify column setup
$table->columns(function ($container) {
    $container->text('my_field', 'My Field');  // Must match data key
});
```

---

### Search not working

**Symptoms**: Search box shows but no filtering happens, or search returns no results

**Checklist**:
- ✅ `setSearchUrl()` is set on table
- ✅ Search URL points to correct action
- ✅ Column doesn't have `setSearch(false)`
- ✅ Controller handles query parameters: `I('get.')`
- ✅ Database query uses search parameters
- ✅ Network request shows search params in browser console

**Debug**:
```php
// In controller
public function index() {
    $params = I('get.');
    var_dump($params);  // Check if search params arrive

    // Apply to query
    $where = [];
    if (!empty($params['name'])) {
        $where['name'] = ['like', '%' . $params['name'] . '%'];
    }

    $list = D('Product')->where($where)->select();
}
```

---

### Pagination not working

**Symptoms**: All data shows on one page, pagination controls don't work

**Checklist**:
- ✅ `setPagination()` is called with Pagination object
- ✅ Total count is correct
- ✅ Page size is reasonable
- ✅ Controller uses pagination parameters

**Debug**:
```php
// Check pagination setup
$total = D('Product')->count();
$pageSize = 20;
$pagination = new Table\Pagination($total, $pageSize);

$table->setPagination($pagination);

// In controller, use pagination
$page = I('get.page', 1);
$list = D('Product')->page($page, $pageSize)->select();
```

---

### Inline editing not saving

**Symptoms**: Edit mode enables but changes don't save

**Checklist**:
- ✅ `defaultEditMode()` is set on table
- ✅ Columns have `->editable()`
- ✅ `editSave()` action is configured
- ✅ `saveRequest()` URL is correct
- ✅ Controller accepts PUT/POST request
- ✅ Controller updates database

**Debug**:
```php
// Table setup
$table->defaultEditMode()
      ->columns(function ($container) {
          $container->digit('sort', '排序')->editable();
      })
      ->actions(function ($container) {
          $container->editSave()
                    ->saveRequest('put', U('updateSort'));
      });

// Controller
public function updateSort() {
    $data = I('put.');
    var_dump($data);  // Check incoming data

    $result = D('Product')->save($data);
    if ($result) {
        $this->success('保存成功');
    }
}
```

---

## Form Issues

### Form not submitting

**Symptoms**: Submit button clicked but nothing happens, or error occurs

**Checklist**:
- ✅ `setSubmitRequest()` is configured
- ✅ Button has `->submit()` action
- ✅ Form fields don't have validation errors
- ✅ Server endpoint exists and accepts the method
- ✅ Check browser console for JavaScript errors
- ✅ Check network tab for request/response

**Debug**:
```php
// Check form setup
$form->setSubmitRequest('post', U('save'))
     ->actions(function ($container) {
         $container->button('提交')->submit();  // Must call submit()
     });

// Check controller
public function save() {
    if (!IS_POST) {
        $this->error('非法请求');
    }

    $data = I('post.');
    var_dump($data);  // Check submitted data

    $result = D('Product')->add($data);
    if ($result) {
        $this->success('添加成功');
    } else {
        $this->error(D('Product')->getError());
    }
}
```

---

### Validation not working

**Symptoms**: Form submits even with invalid data, or validation errors don't show

**Checklist**:
- ✅ Validation rules are added with `addRule()`
- ✅ Using correct validation class (e.g., `Required`)
- ✅ Validation package is installed
- ✅ Check Model validation rules aren't conflicting

**Debug**:
```php
use Qscmf\Core\Validator\Rule\Required;

// Add validation
$container->text('title', '标题')
          ->addRule(new Required());  // Required validation

// Check Model validation
class ProductModel extends GyListModel {
    protected $_validate = [
        ['title', 'require', '标题不能为空'],  // Also validates here
    ];
}
```

---

### Initial values not showing

**Symptoms**: Edit form shows empty fields instead of existing data

**Checklist**:
- ✅ `setInitialValues()` is called
- ✅ Data is fetched from database correctly
- ✅ Field names in initial values match form field names
- ✅ Data format is correct (array, not object)

**Debug**:
```php
public function edit() {
    $id = I('get.id');
    $data = D('Product')->find($id);

    var_dump($data);  // Check data structure

    $form = new Form();
    $form->setInitialValues($data)  // Must be array
         ->columns(function ($container) {
             $container->text('name', '名称');  // Must match $data['name']
         });
}
```

---

### Image/File upload failing

**Symptoms**: Upload progress shows but then fails, or no response

**Checklist**:
- ✅ `setUploadRequest()` is called with valid URL
- ✅ object-storage package is installed
- ✅ Upload policy endpoint works
- ✅ PHP upload settings are correct:
  - `upload_max_filesize`
  - `post_max_size`
- ✅ Nginx/Apache upload limits
- ✅ Storage directory permissions
- ✅ Check network tab for error response

**Debug**:
```php
// Check upload configuration
phpinfo();  // Look for upload_max_filesize, post_max_size

// Test upload endpoint directly
curl -X POST http://your-site/upload-policy-endpoint

// Check storage permissions
ls -la lara/storage/uploads/

// In controller
public function uploadPolicy() {
    $policy = Common::genItemDataUrl('image');
    var_dump($policy);  // Check policy generation
}
```

**Common errors**:
```
413 Request Entity Too Large → Increase nginx client_max_body_size
500 Internal Server Error → Check PHP error log
403 Forbidden → Check storage permissions
```

---

## Modal Issues

### Modal not opening

**Symptoms**: Click button but modal doesn't appear

**Checklist**:
- ✅ Modal is attached to button with `->modal($modal)`
- ✅ Modal has `setContent()` or `setUrl()`
- ✅ If using URL, endpoint is accessible
- ✅ Check browser console for JavaScript errors
- ✅ Check network tab for failed requests (if using setUrl)

**Debug**:
```php
// Check modal setup
$modal = new Modal();
$modal->setTitle('编辑')
      ->setUrl(U('edit', ['id' => '__id__']));  // __id__ will be replaced

$container->link('编辑')->modal($modal);  // Must attach modal

// Check if URL endpoint works
// Visit: http://your-site/edit?id=1
```

---

### Modal content not loading (URL-based)

**Symptoms**: Modal opens but content area is empty or shows error

**Checklist**:
- ✅ URL in `setUrl()` is correct
- ✅ Controller action exists
- ✅ Controller returns proper response (not redirect)
- ✅ `__fieldName__` placeholders are valid
- ✅ Check network tab for request details

**Debug**:
```php
// Modal with URL
$modal = new Modal();
$modal->setUrl(U('edit', ['id' => '__id__']));  // __id__ from row data

// Controller must return renderable content
public function edit() {
    $id = I('get.id');
    $data = D('Product')->find($id);

    $form = new Form();
    $form->setInitialValues($data)
         ->columns(...)
         ->render();  // Must call render()

    // Don't redirect! Return rendered content
}
```

---

### Modal not closing after form submit

**Symptoms**: Form submits successfully but modal stays open

**Checklist**:
- ✅ Form submission is successful
- ✅ Response is in correct format
- ✅ Check if custom `afterAction` is overriding defaults

**Debug**:
```php
// Default behavior closes modal and reloads table
$form->setSubmitRequest('post', U('save'));

// If you need custom behavior
$form->setSubmitRequest('post', U('save'), null, null, [
    Button::AFTER_ACTION_CLOSE_MODAL,
    Button::AFTER_ACTION_TABLE_RELOAD
]);

// Controller must return success response
public function save() {
    $result = D('Product')->add(I('post.'));
    if ($result) {
        $this->success('保存成功');  // This triggers modal close
    }
}
```

---

## Action Issues

### Action button not working

**Symptoms**: Click button but nothing happens

**Checklist**:
- ✅ Action method is called correctly (`link()`, `request()`, `modal()`)
- ✅ URL is correct
- ✅ Permission node is configured (if using `setAuthNode()`)
- ✅ Condition for showing is met (if using `setShowCondition()`)
- ✅ Check browser console for errors

**Debug**:
```php
// Link action
$container->link('查看')->setHref(U('detail', ['id' => '__id__']));

// Request action
$container->link('删除')
          ->request('delete', U('delete', ['id' => '__id__']))
          ->setConfirmMessage('确定删除吗？');

// Check permission
$container->edit()->setAuthNode('product_edit');
// User must have 'product_edit' permission
```

---

### Batch operation not working

**Symptoms**: Batch buttons don't work or affect no rows

**Checklist**:
- ✅ `relateSelection()` is called
- ✅ Rows are selected (checkboxes)
- ✅ Request data includes selected IDs
- ✅ Controller handles batch operation

**Debug**:
```php
// Setup batch operation
$container->button('批量删除')
          ->relateSelection()  // Required for batch ops
          ->request('post', U('batchDelete'));

// Controller
public function batchDelete() {
    $ids = I('post.ids');  // Array of selected IDs
    var_dump($ids);  // Check if IDs received

    $result = D('Product')->where(['id' => ['in', $ids]])->delete();
    if ($result) {
        $this->success('删除成功');
    }
}
```

---

## Performance Issues

### Table loading slowly

**Symptoms**: Table takes long time to display data

**Checklist**:
- ✅ Use pagination (don't load all data)
- ✅ Check for N+1 queries
- ✅ Add database indexes on searchable fields
- ✅ Limit number of columns displayed
- ✅ Use `select()` instead of `select(false)`

**Debug**:
```php
// ❌ BAD: Load all data
$products = D('Product')->select();
$table->setDataSource($products);

// ✅ GOOD: Use pagination
$page = I('get.page', 1);
$pageSize = 20;
$products = D('Product')->page($page, $pageSize)->select();
$total = D('Product')->count();

$table->setDataSource($products)
      ->setPagination(new Table\Pagination($total, $pageSize));

// Check for N+1 queries
$products = D('Product')->relation('category')->select();  // Eager load
```

---

## Security Issues

### XSS vulnerability

**Symptoms**: User input displayed as HTML instead of text

**Checklist**:
- ✅ AntdAdmin auto-escapes by default
- ✅ Don't use `html_entity_decode` unnecessarily
- ✅ Be careful with `setDescription()`
- ✅ Validate and sanitize user input

**Debug**:
```php
// ❌ BAD: Potential XSS
$table->setDescription($_GET['user_input']);

// ✅ GOOD: Sanitize input
$table->setDescription(htmlspecialchars(I('get.description')));

// AntdAdmin auto-escapes column values
$container->text('content', '内容');  // Safe
```

---

## Getting Help

### Debug Checklist

1. **Check browser console** (F12 → Console tab)
   - JavaScript errors
   - Network request failures

2. **Check network tab** (F12 → Network tab)
   - Request URL is correct
   - Response status (200, 404, 500)
   - Response content

3. **Check PHP error logs**
   ```bash
   tail -f lara/storage/logs/laravel.log
   ```

4. **Add debugging output**
   ```php
   var_dump($data);
   var_dump(I('get.'));
   exit;
   ```

5. **Check official documentation**
   - `/mnt/www/antd-admin/doc/`
   - [Ant Design docs](https://ant.design/)

6. **Check examples in project**
   ```bash
   grep -r "new Table()" app/Admin/Controller/
   grep -r "new Form()" app/Admin/Controller/
   ```

---

## Common Error Messages

### "Call to undefined method"

**Cause**: Wrong method name or using Table method on Form

**Solution**: Check API reference, ensure correct component type

### "Column not found"

**Cause**: `dataIndex` doesn't match field name in data

**Solution**: Verify field names match exactly (case-sensitive)

### "Class not found"

**Cause**: Missing `use` statement

**Solution**: Add use statements:
```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Form;
use AntdAdmin\Component\Modal\Modal;
```

### "Maximum function nesting level reached"

**Cause**: Infinite loop in component configuration

**Solution**: Check for circular references in closures

### "Allowed memory size exhausted"

**Cause**: Loading too much data at once

**Solution**: Use pagination, limit queries

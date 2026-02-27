---
name: qscmf-backend-v13
description: |
  QSCMF v13 backend development (PHP 8.2, PHPUnit 9, Legacy jQuery rendering).
  Auto-loaded when v13 is detected from composer.json.

  Scaffold Mode triggers: "创建", "生成", "scaffold", "模块", "CRUD", "API"
  Guide Mode: Default for QSCMF development questions
---

# QSCMF v13 Backend Development

QSCMF v13 uses **PHP 8.2**, **PHPUnit 9**, and **Legacy jQuery rendering** with Bootstrap 3.

## Mode Selection

### Scaffold Mode (Code Generation)

**Triggers**: "创建", "生成", "scaffold", "模块", "CRUD", "API"

When user requests code generation, follow the 6-step scaffold workflow.

### Guide Mode (Development Assistance)

Default mode for QSCMF development questions. Provide guidance based on the rules and references.

---

## Scaffold Workflow (6 Steps)

### Step 1: Identify Requirements

Extract from user request:
- **Module Name**: e.g., "Product", "User", "Order"
- **Components**: Model, AdminController, ApiController, Migration, Test
- **Options**: Soft delete, status field, category relation, etc.

```
Example: "创建 Product 模块，需要后台 CRUD 和 API"
→ Module: Product
→ Components: Model, AdminController, ApiController
```

### Step 2: Parse Table Schema

Read from migration files or database:

```bash
# Check for existing migration
ls lara/database/migrations/*create_{table_name}*

# Or query database schema
php artisan tinker >>> Schema::getColumnListing('{table_name}')
```

**Metadata Format** (in migration comments):
```php
$table->string('name', 200)->comment('@title=名称;@type=text;@require=true;');
$table->integer('status')->comment('@title=状态;@type=select;@options=DBCont::getStatusList();');
```

### Step 3: Infer Field Types

Apply three-layer inference strategy:

1. **Configuration Layer**: Check `.claude/qscmf/field-rules.yaml`
2. **Learning Layer**: Scan existing controllers for patterns
3. **Default Layer**: Field name suffix patterns

| Pattern | Inferred Type |
|---------|---------------|
| `*_content` | ueditor |
| `*_date` | date |
| `*_time` | datetime |
| `*_id` (foreign key) | select |
| `status` | select |
| `cover` / `*_img` | picture |
| `file_id` | file |
| `sort` | num |

See: [rules/field-type-inference.md](rules/field-type-inference.md)

### Step 4: Generate Code

Use templates from `v13/templates/`:

| Component | Template | Output Path |
|-----------|----------|-------------|
| Model | `model.php.tpl` | `app/Common/Model/{Name}Model.class.php` |
| AdminController | `admin_controller.php.tpl` | `app/Admin/Controller/{Name}Controller.class.php` |
| ApiController | `api_controller.php.tpl` | `app/Api/Controller/{Name}Controller.class.php` |
| Test | `test_case.php.tpl` | `lara/tests/Feature/{Name}Test.php` |

### Step 5: Write Files

Create files in correct directories:

```
app/Common/Model/ProductModel.class.php
app/Admin/Controller/ProductController.class.php
app/Api/Controller/ProductController.class.php
lara/tests/Feature/ProductTest.php
```

### Step 6: Output TODO List

```markdown
## Generated Files
- [ ] app/Common/Model/ProductModel.class.php
- [ ] app/Admin/Controller/ProductController.class.php
- [ ] app/Api/Controller/ProductController.class.php
- [ ] lara/tests/Feature/ProductTest.php

## Manual Steps Required
1. [ ] Run migration: `php artisan migrate`
2. [ ] Configure permissions in admin_menu table
3. [ ] Add validation rules in Model::$_validate
4. [ ] Implement business logic in save() method
5. [ ] Add dependency checks in delete() method
6. [ ] Run tests: `vendor/bin/phpunit lara/tests/Feature/ProductTest.php`
```

---

## Framework Guide

### Core Base Classes

| Component | Base Class | Purpose |
|-----------|-----------|---------|
| Admin CRUD | `QsListController` | Backend management with ListBuilder |
| RESTful API | `RestController` | JSON API endpoints |
| Model | `GyListModel` | Data access with caching, validation |
| CLI Controller | `CliModeHelperController` | Command-line batch scripts |

### ListBuilder API (v13)

v13 uses the **ListBuilder** API with jQuery/Bootstrap rendering:

```php
$builder = $this->builder();

// Table columns
$builder->addTableColumn('id', 'ID');
$builder->addTableColumn('name', '名称');
$builder->addTableColumn('status', '状态', DBCont::getStatusList());

// Search items
$builder->addSearchItem('keyword', 'text', '关键词');
$builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());

// Top buttons
$builder->addTopButton('addnew', ['title' => '新增']);
$builder->addTopButton('forbid');
$builder->addTopButton('resume');
$builder->addTopButton('delete');

// Right buttons
$builder->addRightButton('edit', ['href' => U('edit', ['id' => '@id@'])]);
$builder->addRightButton('delete', ['href' => U('delete', ['ids' => '@id@'])]);

$builder->display();
```

See: [rules/listbuilder-api.md](rules/listbuilder-api.md)

### FormBuilder API

```php
$builder->addFormItem('name', 'text', '名称', '请输入名称', true);
$builder->addFormItem('cate_id', 'select', '分类', D('Category')->getFieldOptions());
$builder->addFormItem('cover', 'picture', '封面图');
$builder->addFormItem('content', 'ueditor', '内容');
$builder->addFormItem('status', 'radio', '状态', [1 => '启用', 0 => '禁用']);
```

See: [rules/formbuilder-api.md](rules/formbuilder-api.md)

### Database Constants

Use `Gy_Library\DBCont` for standard status values:

```php
use Gy_Library\DBCont;

DBCont::NORMAL_STATUS    // = 1 (enabled)
DBCont::DISABLE_STATUS   // = 0 (disabled)
DBCont::AUDIT_STATUS     // = 2 (pending review)

DBCont::getStatusList()  // [1 => '启用', 0 => '禁用']
```

---

## Common Code Patterns

### CRUD Controller Pattern

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;

class ProductController extends QsListController
{
    protected $modelName = 'Product';

    public function index()
    {
        $map = $this->buildSearchMap(I('get.'));
        $list = D('Product')->where($map)->order('id desc')->select();

        $builder = $this->builder();
        $this->buildTableColumns($builder);
        $this->buildSearchForm($builder);
        $this->buildButtons($builder);
        $builder->setData($list);
        $builder->display();
    }

    protected function buildTableColumns($builder)
    {
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('name', '名称');
        $builder->addTableColumn('status', '状态', DBCont::getStatusList());
    }

    protected function buildButtons($builder)
    {
        $builder->addTopButton('addnew');
        $builder->addRightButton('edit');
        $builder->addRightButton('delete');
    }
}
```

### Model Pattern

```php
<?php
namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;

class ProductModel extends GyListModel
{
    protected $tableName = 'product';
    protected $pk = 'id';

    protected $_validate = [
        ['name', 'require', '名称不能为空'],
    ];

    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT, 'function'],
        ['update_time', 'time', self::MODEL_UPDATE, 'function'],
    ];
}
```

### API Controller Pattern

```php
<?php
namespace Api\Controller;

use Qscmf\Api\RestController;
use QscmfApiCommon\Cache\Response;

class ProductController extends RestController
{
    protected $noAuthorization = ['gets', 'detail'];

    public function gets(): Response
    {
        $page = (int)I('get.page', 1);
        $limit = (int)I('get.limit', 10);

        $list = D('Product')->page($page, $limit)->select();
        $total = D('Product')->count();

        return new Response('成功', 1, [
            'list' => $list,
            'total' => $total,
            'page' => $page,
            'limit' => $limit
        ]);
    }
}
```

---

## v13-Specific: Legacy jQuery Rendering

### Rendering Mode

v13 uses **jQuery + Bootstrap 3** rendering:

```php
// Environment constant
ANTD_ADMIN_BUILDER_ENABLE = false  // v13 default
```

### Bootstrap CSS Classes

v13 admin pages use Bootstrap 3 classes:

```html
<!-- Status badges -->
<span class="label label-success">启用</span>
<span class="label label-default">禁用</span>
<span class="label label-warning">待审核</span>

<!-- Buttons -->
<button class="btn btn-primary">新增</button>
<button class="btn btn-danger">删除</button>

<!-- Tables -->
<table class="table table-striped table-bordered">
```

### jQuery Event Handling

```javascript
// Custom form submission
$('#myForm').on('submit', function(e) {
    e.preventDefault();
    $.post($(this).attr('action'), $(this).serialize(), function(res) {
        if (res.status) {
            location.reload();
        } else {
            alert(res.msg);
        }
    });
});

// Before search event
$('body').on('beforeSearch', '.builder #search', function() {
    var keyword = $("input[name='keyword']").val();
    if (!keyword) {
        $(this).data('jump', 0);
        alert('关键词不能为空');
    }
});
```

### DataTables Integration

v13 uses DataTables for table rendering:

```javascript
// DataTables configuration
$('#data-table').DataTable({
    processing: true,
    serverSide: false,
    pageLength: 20,
    order: [[0, 'desc']]
});
```

### AJAX Form Handling

```php
// Controller - AJAX response
public function toggleStatus()
{
    if (!IS_AJAX) {
        $this->error('非法请求');
    }

    $ids = I('post.ids');
    $result = D('Product')->where(['id' => ['IN', $ids]])
        ->setField('status', I('post.status'));

    $this->ajaxReturn([
        'status' => $result !== false ? 1 : 0,
        'msg' => $result !== false ? '操作成功' : '操作失败'
    ]);
}
```

### Known jQuery Quirks

1. **Modal z-index issues**: Use `data-backdrop="false"` or adjust CSS
2. **AJAX file upload**: Requires `FormData` object
3. **Event delegation**: Use `$('body').on('event', 'selector', fn)`
4. **IE11 compatibility**: v13 jQuery is more compatible with older browsers

See: [rules/legacy-jquery.md](rules/legacy-jquery.md)

---

## Rules Reference

### Core API Rules
- [ListBuilder API](rules/listbuilder-api.md) - Complete ListBuilder reference
- [FormBuilder API](rules/formbuilder-api.md) - Complete FormBuilder reference
- [Field Type Inference](rules/field-type-inference.md) - Three-layer inference strategy
- [Legacy jQuery](rules/legacy-jquery.md) - v13 specific jQuery quirks

### Workflow Rules
- [Create Module](rules/workflow/workflow-create-module.md) - Module creation workflow
- [Add CRUD](rules/workflow/workflow-add-crud.md) - CRUD implementation workflow

### CRUD Rules
- [Table Columns v13](rules/crud/crud-table-columns-v13.md) - Column configuration
- [Search Basic](rules/crud/crud-search-basic.md) - Search functionality
- [Form Validation](rules/crud/crud-form-validation.md) - Validation rules
- [Custom Components](rules/crud/crud-custom-components.md) - Custom renderers
- [Batch Actions](rules/crud/crud-batch-actions.md) - Batch operations

### API Rules
- [Response Format](rules/api/api-response-format.md) - JSON response format
- [Pagination Cursor](rules/api/api-pagination-cursor.md) - Pagination strategies
- [Auth JWT](rules/api/api-auth-jwt.md) - JWT authentication

### Test Rules
- [TDD First](rules/test/test-tdd-first.md) - Test-driven development
- [Wall Mock](rules/test/test-wall-mock.md) - Mocking external services
- [Transaction](rules/test/test-transaction.md) - Database transaction testing

### Pattern Rules
- [Abstract Base](rules/pattern/pattern-abstract-base.md) - Abstract base class pattern
- [Redis Lock](rules/pattern/pattern-redis-lock.md) - Distributed locking
- [Queue Job](rules/pattern/pattern-queue-job.md) - Async queue processing
- [Wall Class](rules/pattern/pattern-wall-class.md) - External service wrapper

### Scaffold Rules
- [Generate Code](rules/scaffold/scaffold-generate-code.md) - Code generation workflow
- [Parse Metadata](rules/scaffold/scaffold-parse-metadata.md) - Migration metadata parsing
- [Infer Types](rules/scaffold/scaffold-infer-types.md) - Field type inference
- [Migration First](rules/scaffold/scaffold-migration-first.md) - Migration-first approach

---

## References

- [Admin Controllers](references/admin-controllers.md) - Complete admin controller guide
- [API Controllers](references/api-controllers.md) - RESTful API development
- [Model Guide](references/model-guide.md) - GyListModel patterns
- [Migration Guide](references/migration-guide.md) - Schema Builder usage
- [Migration Metadata](references/migration-metadata.md) - @metadata system
- [CRUD Patterns](references/crud-patterns.md) - Common CRUD patterns
- [Where Query Reference](references/where-query-reference.md) - Query syntax
- [Development Standards](references/development-standards.md) - PHP 8.2 standards
- [Testing](references/testing.md) - PHPUnit testing guide
- [Abstract Base Patterns](references/abstract-base-patterns.md) - Reusable patterns

---

## Templates

Code generation templates are located in `v13/templates/`:

- `admin_controller.php.tpl` - QsListController with ListBuilder
- `model.php.tpl` - GyListModel with validation
- `api_controller.php.tpl` - RestController with JSON responses
- `test_case.php.tpl` - PHPUnit test cases

---

## Quick Reference

### File Paths

| Component | Path |
|-----------|------|
| Model | `app/Common/Model/{Name}Model.class.php` |
| AdminController | `app/Admin/Controller/{Name}Controller.class.php` |
| ApiController | `app/Api/Controller/{Name}Controller.class.php` |
| Migration | `lara/database/migrations/xxxx_create_{table}_table.php` |
| Test | `lara/tests/Feature/{Name}Test.php` |

### Common Commands

```bash
# Run migration
php artisan migrate

# Rollback migration
php artisan migrate:rollback

# Run tests
vendor/bin/phpunit

# Run specific test
vendor/bin/phpunit lara/tests/Feature/ProductTest.php

# CLI execution
php www/index.php Admin/Product/index
```

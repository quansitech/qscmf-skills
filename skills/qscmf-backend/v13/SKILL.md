---
name: qscmf-backend-v13
description: |
  QSCMF v13 backend development (PHP 8.2, PHPUnit 9, Legacy jQuery rendering).
  Auto-loaded when v13 is detected from composer.json.

  Scaffold Mode triggers: "创建", "生成", "scaffold", "模块", "CRUD", "API"
  Guide Mode: Default for QSCMF development questions
---

# QSCMF v13 Backend Development

## Overview

QSCMF v13 is the legacy version featuring:
- **PHP 8.2** with strict typing
- **PHPUnit 9** for testing
- **jQuery + Bootstrap 3** rendering
- **ListBuilder API** (same core API as v14, jQuery rendering)

---

## Mode Selection

| Mode | Triggers | Handler |
|------|----------|---------|
| Scaffold | "创建", "生成", "scaffold", "模块", "CRUD", "API" | [modes/scaffold.md](modes/scaffold.md) |
| Guide | "如何", "怎样", "?" | [modes/guide.md](modes/guide.md) |
| Learn | /qscmf-learn | [modes/learn.md](modes/learn.md) |

---

## Quick Reference

### Admin CRUD (QsListController)

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
}
```

### RESTful API (RestController)

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
        $list = D('Product')->page($page, 10)->select();
        return new Response('成功', 1, ['list' => $list]);
    }
}
```

---

## v13-Specific Features

- jQuery + Bootstrap 3 rendering
- `ANTD_ADMIN_BUILDER_ENABLE = false` (default)
- See [rules/legacy-jquery.md](rules/legacy-jquery.md)

---

## File Paths Reference

| Component | Path |
|-----------|------|
| AdminController | `app/Admin/Controller/{Name}Controller.class.php` |
| ApiController | `app/Api/Controller/{Name}Controller.class.php` |
| Model | `app/Common/Model/{Name}Model.class.php` |
| Migration | `lara/database/migrations/xxxx_create_{table}_table.php` |
| Test | `lara/tests/Feature/{Name}Test.php` |

---

## Rules Index

### Core API
- [ListBuilder API](rules/listbuilder-api.md)
- [FormBuilder API](rules/formbuilder-api.md)
- [Field Type Inference](rules/field-type-inference.md)
- [Legacy jQuery](rules/legacy-jquery.md)

### Workflow
- [Create Module](rules/workflow/workflow-create-module.md)
- [Add CRUD](rules/workflow/workflow-add-crud.md)

### CRUD
- [Table Columns v13](rules/crud/crud-table-columns-v13.md)
- [Search Basic](rules/crud/crud-search-basic.md)
- [Form Validation](rules/crud/crud-form-validation.md)
- [Batch Actions](rules/crud/crud-batch-actions.md)

### API
- [Response Format](rules/api/api-response-format.md)
- [Pagination](rules/api/api-pagination-cursor.md)
- [JWT Auth](rules/api/api-auth-jwt.md)

### Testing
- [TDD First](rules/test/test-tdd-first.md)
- [Transaction](rules/test/test-transaction.md)

### Patterns
- [Abstract Base](rules/pattern/pattern-abstract-base.md)
- [Redis Lock](rules/pattern/pattern-redis-lock.md)
- [Queue Job](rules/pattern/pattern-queue-job.md)

### Scaffold
- [Generate Code](rules/scaffold/scaffold-generate-code.md)
- [Parse Metadata](rules/scaffold/scaffold-parse-metadata.md)
- [Infer Types](rules/scaffold/scaffold-infer-types.md)

---

## References Index

- [Admin Controllers](references/admin-controllers.md)
- [API Controllers](references/api-controllers.md)
- [Model Guide](references/model-guide.md)
- [Migration Guide](references/migration-guide.md)
- [CRUD Patterns](references/crud-patterns.md)
- [Development Standards](references/development-standards.md)

---
name: qscmf-backend-v14
description: |
  QSCMF v14 backend development (PHP 8.2+, PHPUnit 10, AntdAdmin, Inertia.js).
  Auto-loaded when v14 is detected.

  Scaffold Mode: "创建", "生成", "scaffold", "模块", "CRUD", "API"
  Guide Mode: Default for QSCMF development questions
  Learn Mode: /qscmf-learn command
---

# QSCMF v14 Backend Development

## Overview

QSCMF v14 features PHP 8.2+, PHPUnit 10, AntdAdmin React components, Inertia.js SPA navigation. ListBuilder API compatible with v13, React rendering controlled by `ANTD_ADMIN_BUILDER_ENABLE`.

---

## Mode Selection

| Mode | Triggers | Handler |
|------|----------|---------|
| **Scaffold** | "创建", "生成", "scaffold", "模块", "CRUD", "API" | [modes/scaffold.md](modes/scaffold.md) |
| **Guide** | "如何", "怎样", "?", default mode | [modes/guide.md](modes/guide.md) |
| **Learn** | `/qscmf-learn` command | [modes/learn.md](modes/learn.md) |
| **Verify** | `/qscmf-verify` command | [modes/verify.md](modes/verify.md) |

> 详见 [intent-classification.md](rules/intent-classification.md)

---

## Quick Reference

```php
// Admin CRUD (QsListController)
class ProductController extends QsListController
{
    protected $modelName = 'Product';
    public function index() {
        $builder = $this->builder();
        $builder->addTableColumn('id', 'ID');
        $builder->setData(D('Product')->select());
        $builder->display();
    }
}

// RESTful API (RestController)
class ProductController extends RestController
{
    protected $modelName = 'Product';
    public function index_get() {
        $this->response([
            'status' => true,
            'data' => D('Product')->select()
        ]);
    }
}

// Model (GyListModel)
class ProductModel extends GyListModel
{
    protected $tableName = 'product';
    protected $_validate = [
        ['product_name', 'require', '商品名称不能为空', self::MUST_VALIDATE],
    ];
}
```

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

**Core API**: [ListBuilder](rules/listbuilder-api.md) | [FormBuilder](rules/formbuilder-api.md) | [Field Types](rules/field-type-inference.md)

**v14**: [Features](rules/v14-features.md) | [Patterns](rules/common-patterns.md) | [Inertia.js](rules/inertia.md) | [AntdAdmin](rules/antdadmin.md)

**CRUD**: [Table Columns](rules/crud/crud-table-columns.md) | [Search](rules/crud/crud-search-basic.md) | [Validation](rules/crud/crud-form-validation.md) | [Batch](rules/crud/crud-batch-actions.md)

**API**: [Response Format](rules/api/api-response-format.md) | [Pagination](rules/api/api-pagination-cursor.md) | [JWT Auth](rules/api/api-auth-jwt.md) | [Docs](rules/api/api-documentation.md)

**Testing**: [TDD](rules/test/test-tdd-first.md) | [Wall Mock](rules/test/test-wall-mock.md) | [Transaction](rules/test/test-transaction.md) | [CLI](rules/test/test-cli-controller.md)

**Patterns**: [Abstract Base](rules/pattern/pattern-abstract-base.md) | [Redis Lock](rules/pattern/pattern-redis-lock.md) | [Queue Job](rules/pattern/pattern-queue-job.md) | [Wall Class](rules/pattern/pattern-wall-class.md)

**Scaffold**: [Generate Code](rules/scaffold/scaffold-generate-code.md) | [Parse Metadata](rules/scaffold/scaffold-parse-metadata.md) | [Infer Types](rules/scaffold/scaffold-infer-types.md) | [Migration First](rules/scaffold/scaffold-migration-first.md)

---

## References Index

[Admin Controllers](references/admin-controllers.md) | [API Controllers](references/api-controllers.md) | [Model Guide](references/model-guide.md) | [Migration Guide](references/migration-guide.md) | [Metadata](references/migration-metadata.md) | [CRUD Patterns](references/crud-patterns.md) | [Where Query](references/where-query-reference.md) | [Standards](references/development-standards.md) | [Testing](references/testing.md) | [Abstract Base](references/abstract-base-patterns.md) | [Inertia](references/inertia-integration.md)

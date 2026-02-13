---
name: qscmf-backend
description: |
  QSCMF framework (ThinkPHP 3.2 + Laravel hybrid) backend development and code generation.

  **Auto-detects QSCMF projects**: Contains app/ + lara/ directories.
  Auto-detects version from composer.json (v13: PHP 8.2, v14: PHP 8.2+).

  Covers: migration, scaffold, CRUD, API, testing, advanced patterns.
  Triggers: "创建", "生成", "CRUD", "API", "QsListController" in QSCMF projects.

  Version override: "qscmf-backend v14 创建..." to force specific version.
---

# QSCMF Backend Development

## Version Detection

Auto-detect from `composer.json` → `tiderjian/think-core` version:
- `^13.0` → v13 (PHP 8.2, PHPUnit 9, Legacy jQuery)
- `^14.0` → v14 (PHP 8.2+, PHPUnit 10, antd-admin)

## Quick Start (Most Common Operations)

### 1. Create Complete Module
```
"创建 Product 模块"
```
→ [workflow-create-module.md](rules/workflow/workflow-create-module.md)

### 2. Add Search to Table
```php
$container->text('name', '名称')->setSearch(true)->setSearchType('like');
```
→ [crud-search-basic.md](rules/crud/crud-search-basic.md)

### 3. Add Form Validation
```php
$columns->text('title', '标题')->addRule(new Required());
```
→ [crud-form-validation.md](rules/crud/crud-form-validation.md)

### 4. Write Test First
```php
public function testCreate(): void {
    $id = D('Product')->add(['name' => 'Test']);
    $this->assertTrue($id > 0);
}
```
→ [test-tdd-first.md](rules/test/test-tdd-first.md)

### 5. Custom Renderer (v14)
```php
$container->custom('status', '状态')
    ->setRenderer(fn($v) => React::render('Badge', ['status' => $v]));
```
→ [crud-custom-components.md](rules/crud/crud-custom-components.md)

## Intent Routing (Classified by Function)

### Code Generation
| User Request | Reference |
|--------------|-----------|
| "创建 {Module} 模块" | [workflow-create-module.md](rules/workflow/workflow-create-module.md) |
| "生成 {Module} CRUD" | [workflow-add-crud.md](rules/workflow/workflow-add-crud.md) |
| "创建数据库表" | [scaffold-migration-first.md](rules/scaffold/scaffold-migration-first.md) |

### CRUD Implementation
| User Request | Reference |
|--------------|-----------|
| "配置 Table 列" | [crud-table-columns-v14.md](rules/crud/crud-table-columns-v14.md) |
| "配置搜索" | [crud-search-basic.md](rules/crud/crud-search-basic.md) |
| "表单验证" | [crud-form-validation.md](rules/crud/crud-form-validation.md) |
| "自定义组件" | [crud-custom-components.md](rules/crud/crud-custom-components.md) |
| "批量操作" | [crud-batch-actions.md](rules/crud/crud-batch-actions.md) |

### API Development
| User Request | Reference |
|--------------|-----------|
| "API 开发" | [api-response-format.md](rules/api/api-response-format.md) |
| "分页实现" | [api-pagination-cursor.md](rules/api/api-pagination-cursor.md) |
| "认证授权" | [api-auth-jwt.md](rules/api/api-auth-jwt.md) |

### Testing
| User Request | Reference |
|--------------|-----------|
| "编写测试" | [test-tdd-first.md](rules/test/test-tdd-first.md) |
| "Mock 外部 API" | [test-wall-mock.md](rules/test/test-wall-mock.md) |

### Architecture Patterns
| User Request | Reference |
|--------------|-----------|
| "抽象基类" | [pattern-abstract-base.md](rules/pattern/pattern-abstract-base.md) |
| "并发控制" | [pattern-redis-lock.md](rules/pattern/pattern-redis-lock.md) |
| "队列任务" | [pattern-queue-job.md](rules/pattern/pattern-queue-job.md) |
| "外部 API" | [pattern-wall-class.md](rules/pattern/pattern-wall-class.md) |

## Complete Index (A-Z)

### C
- [Create Module](rules/workflow/workflow-create-module.md)

### F
- [Form Validation](rules/crud/crud-form-validation.md)

### P
- [Pagination](rules/api/api-pagination-cursor.md)

### R
- [Redis Lock](rules/pattern/pattern-redis-lock.md)
- [Response Format](rules/api/api-response-format.md)

### S
- [Search Configuration](rules/crud/crud-search-basic.md)
- [Scaffold](rules/scaffold/scaffold-migration-first.md)
- [Table Columns v14](rules/crud/crud-table-columns-v14.md)
- [Table Columns v13](rules/crud/crud-table-columns-v13.md)
- [Test TDD First](rules/test/test-tdd-first.md)

### W
- [Wall Class Pattern](rules/pattern/pattern-wall-class.md)

## Iron Laws

### Scaffold
```
NO MIGRATION METADATA, NO CODE GENERATION
```

### Testing (from superpowers:test-driven-development)
```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
RED-GREEN-REFACTOR CYCLE
```

### Admin CRUD
```
NO ADMIN CRUD WITHOUT MIGRATION METADATA FIRST
```

## Version-Specific References

| Feature | v13 | v14 |
|---------|-----|-----|
| **PHP** | 8.2 | 8.2+ |
| **PHPUnit** | ^9.3.0 | ^10.0 |
| **UI Framework** | Legacy jQuery | antd-admin ^1.0 |
| **Table Builder** | ListBuilder | AntdAdmin |
| **Upload API** | Legacy | Refactored |

## References

Detailed guides in `references/`:
- [Admin Controllers](references/admin-controllers.md)
- [API Controllers](references/api-controllers.md)
- [Model Guide](references/model-guide.md)
- [Migration Guide](references/migration-guide.md)
- [Testing Patterns](references/testing.md)
- [CRUD Patterns](references/crud-patterns.md)
- [Architecture Patterns](references/abstract-base-patterns.md)

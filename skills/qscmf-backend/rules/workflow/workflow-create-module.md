---
title: Create Complete Module Workflow
impact: CRITICAL
impactDescription: Used in 80% of new module creations
tags: workflow, module-creation, crud, api, test, both
---

## Create Complete Module Workflow

Complete workflow for creating a QSCMF module from scratch.

## When to Use

- User says: "创建 {Module} 模块"
- User says: "生成 {Module} CRUD"
- User says: "QSCMF scaffold {Module}"

## Workflow Steps

### Step 1: Create Migration

**User Input:**
```
创建 Product 模块，包含：
- name: varchar(200), 产品名称
- price: decimal(10,2), 价格
- status: tinyint, 状态
```

**AI Actions:**
1. Generate migration file: `lara/database/migrations/xxxx_create_product_table.php`
2. Add @metadata to each field

**Output:** `lara/database/migrations/xxxx_create_product_table.php`

→ **Detailed Guide**: [scaffold-migration-first.md](../scaffold/scaffold-migration-first.md)

### Step 2: Generate Scaffold Code

**AI Actions:**
1. Parse @metadata from migration
2. Infer field types
3. Generate Model: `app/Common/Model/ProductModel.class.php`
4. Generate AdminController: `app/Admin/Controller/ProductController.class.php`
5. Generate Test: `lara/tests/Feature/ProductTest.php`

**Version-Aware Template Selection:**
- v13 → Use `templates/v13/*.tpl` (Legacy jQuery)
- v14 → Use `templates/v14/*.tpl` (antd-admin)

→ **Detailed Guide**: [scaffold-generate-code.md](../scaffold/scaffold-generate-code.md)

### Step 3: Write Tests First (TDD)

**AI Actions:**
1. Generate PHPUnit test case
2. Focus on critical paths:
   - Model validation
   - Controller actions
   - API responses

→ **Detailed Guide**: [test-tdd-first.md](../test/test-tdd-first.md)

### Step 4: Output TODO List

```markdown
✅ Generated files:
  - app/Common/Model/ProductModel.class.php
  - app/Admin/Controller/ProductController.class.php
  - lara/tests/Feature/ProductTest.php

📝 TODO (manual):
  - [ ] Run migration: php artisan migrate
  - [ ] Configure permissions in qs_node table
  - [ ] Add validation rules in Model::$_validate
  - [ ] Implement business logic (save, delete hooks)
  - [ ] Add foreign key relationships
  - [ ] Run tests: vendor/bin/phpunit
```

## Version Differences

### v14 (antd-admin)
- Generated AdminController uses antd-admin components
- Table/Form with enhanced features

### v13 (Legacy jQuery)
- Generated AdminController uses legacy jQuery
- Table/Form with basic features

## Prerequisites

- ✅ QSCMF project initialized
- ✅ Database connection configured
- ✅ Migration file exists with @metadata

## Estimated Time

- Simple module: 2-3 minutes
- Complex module: 5-10 minutes

**See Also:**
- [Parse Migration Metadata](../scaffold/scaffold-parse-metadata.md)
- [Infer Field Types](../scaffold/scaffold-infer-types.md)
- [Generate Code](../scaffold/scaffold-generate-code.md)
- [Test TDD First](../test/test-tdd-first.md)

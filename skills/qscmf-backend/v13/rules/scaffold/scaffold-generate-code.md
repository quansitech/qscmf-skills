---
title: Scaffold Generate Code (v13)
impact: CRITICAL
impactDescription: Required for all code generation
tags: scaffold, generate, code, v13
---

## Scaffold Generate Code (v13)

Generate Model, Controller, API, and Test code from migration metadata.

### When to Use This Rule

- Creating new modules from scratch
- Generating CRUD code
- Following scaffold workflow

---

## 6-Step Scaffold Workflow

### Step 1: Identify Requirements

Extract from user request:
- **Module Name**: e.g., "Product", "User", "Order"
- **Components**: Model, AdminController, ApiController, Test
- **Options**: Soft delete, status field, category relation

```
Example: "创建 Product 模块，需要后台 CRUD 和 API"
→ Module: Product
→ Components: Model, AdminController, ApiController
```

### Step 2: Parse Table Schema

Read from migration files or database:

```bash
# Check for existing migration
ls lara/database/migrations/*create_product*

# Or query database
php artisan tinker
>>> Schema::getColumnListing('product')
```

**Metadata Format** (in migration comments):
```php
$table->string('name', 200)->comment('@title=名称;@type=text;@require=true;');
$table->integer('status')->comment('@title=状态;@type=select;@options=DBCont::getStatusList();');
```

### Step 3: Infer Field Types

Apply three-layer inference strategy:

1. **Configuration Layer**: Check `.claude/qscmf/field-rules.yaml`
2. **Learning Layer**: Scan existing controllers
3. **Default Layer**: Field name suffix patterns

See: [Field Type Inference](../field-type-inference.md)

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

## Field Type to Code Mapping

| @type | ListBuilder Column | FormBuilder Item |
|-------|-------------------|------------------|
| `text` | `addTableColumn('name', '名称')` | `addFormItem('name', 'text', '名称')` |
| `textarea` | `addTableColumn('desc', '描述', 'textarea')` | `addFormItem('desc', 'textarea', '描述')` |
| `ueditor` | N/A | `addFormItem('content', 'editor', '内容')` |
| `select` | `addTableColumn('status', '状态', $options)` | `addFormItem('status', 'select', '状态', $options)` |
| `date` | `addTableColumn('date', '日期')` | `addFormItem('date', 'date', '日期')` |
| `picture` | `addTableColumn('cover', '封面', 'picture')` | `addFormItem('cover', 'picture', '封面')` |
| `num` | `addTableColumn('sort', '排序', 'num')` | `addFormItem('sort', 'num', '排序')` |

---

## Related Rules

- [Scaffold Parse Metadata](scaffold-parse-metadata.md) - Metadata parsing
- [Scaffold Infer Types](scaffold-infer-types.md) - Type inference
- [Scaffold Migration First](scaffold-migration-first.md) - Migration-first approach
- [Workflow Create Module](../workflow/workflow-create-module.md) - Complete workflow

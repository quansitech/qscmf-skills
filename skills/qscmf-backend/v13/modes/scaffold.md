---
title: Scaffold Mode (v13)
version: v13
impact: HIGH
when: "创建新模块、生成 CRUD 代码、scaffold 代码生成"
---

# Scaffold Mode (v13)

## Trigger Keywords

Mode is activated when user input contains:
- "创建" (create)
- "生成" (generate)
- "scaffold"
- "模块" (module)
- "CRUD"
- "API"

## Example Prompts

- "创建 Product 模块，需要后台 CRUD 和 API"
- "生成 User API"
- "QSCMF scaffold Order"

---

## Workflow

### Step 1: Identify Requirements

Extract module name and required components from user request.

| Request Pattern | Module | Components |
|----------------|--------|------------|
| "创建 Product 模块，需要后台 CRUD 和 API" | Product | AdminController, ApiController, Model, Migration |
| "生成 User API" | User | ApiController only |
| "QSCMF scaffold Order" | Order | All components |

### Step 2: Parse Table Schema

Read schema from:
1. Migration files (`lara/database/migrations/`)
2. Existing database table
3. User-provided field list

Look for metadata comments:
```php
$table->string('cover_id')->comment('封面图 @type=image @crop=16/9');
```

### Step 3: Infer Field Types

Apply three-layer inference strategy:

```
Layer 1: Configuration (.claude/qscmf/field-rules.yaml)
    ↓ (not found)
Layer 2: Learning (scan existing controllers)
    ↓ (not found)
Layer 3: Default rules (field name suffix patterns)
```

**Default Rules**:

| Pattern | Form Type | Table Type |
|---------|-----------|------------|
| `*_content` | ueditor | text (truncated) |
| `*_date` | date | date |
| `*_time` | datetime | datetime |
| `*_id` (FK) | select | select |
| `status` | select | select (with badge) |
| `cover`, `*_img`, `*_image` | picture | picture |
| `file_id`, `*_file` | file | text |
| `sort`, `*_sort` | num | num (editable) |
| `is_*` | checkbox | select |
| `*_url` | text | link |

### Step 4: Generate Code

Use templates with inferred field types:

| Component | Template | Output Path |
|-----------|----------|-------------|
| AdminController | `admin_controller.php.tpl` | `app/Admin/Controller/{Name}Controller.class.php` |
| Model | `model.php.tpl` | `app/Common/Model/{Name}Model.class.php` |
| ApiController | `api_controller.php.tpl` | `app/Api/Controller/{Name}Controller.class.php` |
| Test | `test_case.php.tpl` | `lara/tests/Feature/{Name}Test.php` |

### Step 5: Write Files

Create files in proper directories. Skip if file exists (unless `--force`).

### Step 6: Output TODO List

```markdown
## TODO List

### Required
- [ ] Run migration: `php artisan migrate`
- [ ] Configure permissions in admin_menu table
- [ ] Review and adjust field types in AdminController
- [ ] Add validation rules to Model::$_validate

### Recommended
- [ ] Write tests: `vendor/bin/phpunit lara/tests/Feature/{Name}Test.php`
- [ ] Configure cache if needed
- [ ] Add business logic to save() method
- [ ] Create API documentation: `docs/openapi.json` (if API controller generated)

### References
- [ListBuilder API](../rules/listbuilder-api.md)
- [FormBuilder API](../rules/formbuilder-api.md)
- [Field Type Inference](../rules/field-type-inference.md)
```

---

## Related Rules

- [Generate Code](../rules/scaffold/scaffold-generate-code.md) - Code generation rules
- [Parse Metadata](../rules/scaffold/scaffold-parse-metadata.md) - Migration metadata
- [Infer Types](../rules/scaffold/scaffold-infer-types.md) - Type inference
- [Migration First](../rules/scaffold/scaffold-migration-first.md) - Database-first approach

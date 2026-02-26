---
title: Scaffold Generate Code (v14)
impact: CRITICAL
impactDescription: Required for all code generation
tags: scaffold, generate, code, v14
---

## Scaffold Generate Code (v14)

Generate Model, Controller, API, and Test code from migration metadata using AntdAdmin Component API.

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
Example: "Create Product module with backend CRUD and API"
-> Module: Product
-> Components: Model, AdminController, ApiController
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
$table->string('name', 200)->comment('@title=Name;@type=text;@require=true;');
$table->integer('status')->comment('@title=Status;@type=select;@options=DBCont::getStatusList();');
```

### Step 3: Infer Field Types

Apply three-layer inference strategy:

1. **Configuration Layer**: Check `.claude/qscmf/field-rules.yaml`
2. **Learning Layer**: Scan existing controllers
3. **Default Layer**: Field name suffix patterns

See: [Field Type Inference](../field-type-inference.md)

### Step 4: Generate Code

Use templates from `v14/templates/`:

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

## v14 Key Differences from v13

### AdminController Uses AntdAdmin\Component API

v14 uses the modern AntdAdmin Component API with React rendering:

```php
// v14 - AntdAdmin Component API
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Form;

$table = new Table();
$table->setMetaTitle('Product List')
    ->columns(function (Table\ColumnsContainer $container) {
        $container->text('name', 'Name');
        $container->select('status', 'Status')
            ->setValueEnum(DBCont::getStatusList());
    })
    ->render();

// v13 - ListBuilder API (legacy)
$builder = $this->builder();
$builder->addTableColumn('name', 'Name');
$builder->addFormItem('name', 'text', 'Name');
```

### Table Column Types

| v13 ListBuilder | v14 AntdAdmin\Component | Notes |
|-----------------|------------------------|-------|
| `addTableColumn('name', 'Name')` | `$container->text('name', 'Name')` | Basic text |
| `addTableColumn('status', 'Status', $options)` | `$container->select('status', 'Status')->setValueEnum($options)` | Select with enum |
| `addTableColumn('cover', 'Cover', 'picture')` | `$container->image('cover', 'Cover')` | Image |
| `addTableColumn('sort', 'Sort', 'num')` | `$container->number('sort', 'Sort')` | Number |
| N/A | `$container->money('price', 'Price')` | Money format |
| `addTableColumn('date', 'Date')` | `$container->date('date', 'Date')` | Date |
| `addTableColumn('created', 'Created')` | `$container->datetime('created', 'Created')` | DateTime |

### Form Field Types

| v13 ListBuilder | v14 AntdAdmin\Component | Notes |
|-----------------|------------------------|-------|
| `addFormItem('name', 'text', 'Name')` | `$columns->text('name', 'Name')` | Text input |
| `addFormItem('desc', 'textarea', 'Desc')` | `$columns->textarea('desc', 'Desc')` | Textarea |
| `addFormItem('content', 'editor', 'Content')` | `$columns->ueditor('content', 'Content')` | Rich text |
| `addFormItem('status', 'select', 'Status', $options)` | `$columns->select('status', 'Status')->setValueEnum($options)` | Select |
| `addFormItem('cover', 'picture', 'Cover')` | `$columns->image('cover', 'Cover')` | Image upload |
| N/A | `$columns->file('file_id', 'File')` | File upload |
| `addFormItem('sort', 'num', 'Sort')` | `$columns->number('sort', 'Sort')` | Number input |

### Validation in v14

```php
use AntdAdmin\Component\ColumnType\RuleType\Required;
use AntdAdmin\Component\ColumnType\RuleType\Length;

// Required field
$columns->text('name', 'Name')
    ->addRule(new Required());

// Length validation
$columns->text('name', 'Name')
    ->addRule(new Length(1, 200));
```

---

## Field Type to Code Mapping (v14)

| @type | Table Column | Form Column |
|-------|-------------|-------------|
| `text` | `$container->text('name', 'Name')` | `$columns->text('name', 'Name')` |
| `textarea` | `$container->text('desc', 'Desc')` | `$columns->textarea('desc', 'Desc')` |
| `ueditor` | N/A (not shown in list) | `$columns->ueditor('content', 'Content')` |
| `select` | `$container->select('status', 'Status')->setValueEnum($options)` | `$columns->select('status', 'Status')->setValueEnum($options)` |
| `date` | `$container->date('date', 'Date')` | `$columns->date('date', 'Date')` |
| `datetime` | `$container->datetime('time', 'Time')` | `$columns->datetime('time', 'Time')` |
| `picture` | `$container->image('cover', 'Cover')` | `$columns->image('cover', 'Cover')` |
| `pictures` | `$container->image('images', 'Images')` | `$columns->images('images', 'Images')` |
| `num` | `$container->number('sort', 'Sort')` | `$columns->number('sort', 'Sort')` |
| `money` | `$container->money('price', 'Price')` | `$columns->money('price', 'Price')` |

---

## v14-Specific Features

### Inline Editing

```php
// Enable inline editing for table columns
$container->number('sort', 'Sort')
    ->editable();
```

### Badge Colors for Status

```php
$container->select('status', 'Status')
    ->setValueEnum(DBCont::getStatusList())
    ->setBadge([1 => 'success', 0 => 'default']);
```

### Search in Columns

```php
// Enable search for specific column
$container->text('name', 'Name')
    ->setSearch(true);

// Disable search for ID column
$container->text('id', 'ID')
    ->setSearch(false);
```

### Modal Forms

```php
use AntdAdmin\Component\Modal\Modal;

// Add button with modal form
$container->button('New')
    ->modal((new Modal())
        ->setWidth('800px')
        ->setUrl(U('add'))
        ->setTitle('New Record'));
```

### Form Width

```php
// Full width (24 = 100%)
$columns->ueditor('content', 'Content')
    ->setFormItemWidth(24);

// Half width (12 = 50%)
$columns->number('sort', 'Sort')
    ->setFormItemWidth(12);
```

---

## PHPUnit 10 Changes

v14 uses PHPUnit 10 with updated assertion methods:

```php
// PHPUnit 10 style
$response->assertStatus(200)
    ->assertJsonStructure(['status', 'data'])
    ->assertJsonPath('meta.page', 1);

// Database assertions
$this->assertDatabaseHas('table', ['field' => 'value']);
$this->assertDatabaseMissing('table', ['id' => 999]);
```

---

## Related Rules

- [Scaffold Parse Metadata](scaffold-parse-metadata.md) - Metadata parsing
- [Scaffold Infer Types](scaffold-infer-types.md) - Type inference
- [Scaffold Migration First](scaffold-migration-first.md) - Migration-first approach
- [Workflow Create Module](../workflow/workflow-create-module.md) - Complete workflow

# QSMCF Backend3 - QSCMF Backend Development Skill

A comprehensive Claude Code AI skill for developing applications using the QSCMF framework (QuickStart Content Management Framework). This skill provides intelligent assistance for both code generation (scaffolding) and development guidance across multiple framework versions.

## Overview

QSCMF is a hybrid PHP framework combining:
- **ThinkPHP 3.2** (legacy layer) - Business logic, controllers, models
- **Laravel** (modern layer) - Database migrations, testing, dependency injection

This skill supports two major versions with different frontend stacks and API patterns:
- **v13**: jQuery-based ListBuilder API with traditional rendering
- **v14**: React-based AntdAdmin Component API with Inertia.js SPA

## Installation

### Prerequisites
- Claude Code CLI installed
- A QSCMF project to work on

### Installation Steps

```bash
# Clone this repository
git clone https://github.com/quansitech/qscmf-skills.git

# Create symbolic link to Claude Code's skills directory
ln -s /path/to/qscmf-skills/skills/qsmcf-backend3/ /root/.claude/skills/qsmcf-backend3
```

## Version Detection

The skill automatically detects your QSCMF version from `composer.json`:

| composer.json | Version | Navigate to |
|---------------|---------|-------------|
| `"tiderjian/think-core": "^14.0"` | v14 | [v14/SKILL.md](v14/SKILL.md) |
| `"tiderjian/think-core": "^13.0"` | v13 | [v13/SKILL.md](v13/SKILL.md) |
| not found | Default | v14 (latest) |

### Detection Process

```bash
# Check composer.json in project root
cat composer.json | grep "tiderjian/think-core"

# Example output:
# "tiderjian/think-core": "^14.0"  -> Use v14/SKILL.md
# "tiderjian/think-core": "^13.0"  -> Use v13/SKILL.md
```

### Version Override

Force a specific version regardless of composer.json:

```
# Force v14 mode
"qscmf-backend v14 Create Product module"
"v14 Generate Order CRUD"

# Force v13 mode
"qscmf-backend v13 Create Product module"
"v13 How to configure ListBuilder"
```

## Quick Start Guide

### 1. Verify Project Detection

The skill activates when your project has QSCMF structure:

| Indicator | Description |
|-----------|-------------|
| `app/` directory | ThinkPHP layer (controllers, models, views) |
| `lara/` directory | Laravel layer (migrations, tests) |
| `Gy_Library` namespace | Core framework library |
| AntdAdmin components | v14 React components |

### 2. Choose Operation Mode

**Scaffold Mode** (Code Generation):
- Trigger keywords: "Create", "Generate", "scaffold", "CRUD", "API"
- Example: "Create Product module with backend CRUD and API"

**Guide Mode** (Development Assistance):
- Default mode for answering QSCMF development questions
- Example: "How to implement QsListController CRUD?"

### 3. Follow Version-Specific Workflow

- **Using v14?** -> Continue to [v14/SKILL.md](v14/SKILL.md)
- **Using v13?** -> Continue to [v13/SKILL.md](v13/SKILL.md)

## File Structure Reference

```
qscmf-backend/
├── SKILL.md                   # Main skill workflow (START HERE)
├── README.md                  # This file
├── _shared/                   # Shared content across all versions
│   ├── README.md              # Unified skill introduction
│   ├── concepts/              # Core concepts documentation
│   │   ├── architecture.md    # Framework architecture
│   │   └── core-concepts.md   # ListBuilder, AntdAdmin, GyListModel
│   ├── references/            # Comprehensive guides
│   │   ├── api-controllers.md
│   │   ├── model-guide.md
│   │   ├── development-standards.md
│   │   ├── migration-metadata.md
│   │   ├── abstract-base-patterns.md
│   │   └── glossary.md
│   └── learn/                 # Learning system
│       ├── workflow.md        # Learning workflow
│       └── deep-scan-impl.md  # Deep scan implementation
├── v13/                       # Version 13 specific
│   ├── SKILL.md               # v14 workflow
│   ├── README.md              # v13 details
│   ├── templates/             # Code generation templates
│   │   ├── admin_controller.php.tpl
│   │   ├── model.php.tpl
│   │   ├── api_controller.php.tpl
│   │   └── test_case.php.tpl
│   ├── rules/                 # Version-specific rules
│   │   ├── listbuilder-api.md
│   │   ├── formbuilder-api.md
│   │   ├── field-type-inference.md
│   │   ├── legacy-jquery.md
│   │   ├── workflow/
│   │   ├── crud/
│   │   └── api/
│   └── references/            # v13 reference docs
├── v14/                       # Version 14 specific
│   ├── SKILL.md               # v14 workflow
│   ├── README.md              # v14 details
│   ├── templates/             # Code generation templates
│   │   ├── admin_controller.php.tpl
│   │   ├── model.php.tpl
│   │   ├── api_controller.php.tpl
│   │   └── test_case.php.tpl
│   ├── rules/                 # Version-specific rules
│   │   ├── antdadmin.md
│   │   ├── inertia.md
│   │   ├── listbuilder-api.md
│   │   ├── formbuilder-api.md
│   │   ├── field-type-inference.md
│   │   ├── workflow/
│   │   ├── crud/
│   │   ├── api/
│   │   ├── test/
│   │   ├── pattern/
│   │   └── scaffold/
│   └── references/            # v14 reference docs
```

## Basic Usage

### Scaffold Mode (Code Generation)

Generate complete CRUD modules with a single prompt:

**Example prompts:**
```
"Create Product module with backend CRUD and API"
"Generate User API"
"QSCMF scaffold Order"
```

**Generated files:**
```
Model:          app/Common/Model/ProductModel.class.php
AdminController: app/Admin/Controller/ProductController.class.php
ApiController:  app/Api/Controller/ProductController.class.php
Migration:      lara/database/migrations/xxxx_create_product_table.php
Test:           lara/tests/Feature/ProductTest.php
```

**Workflow:**
1. Identify module name and required components
2. Parse table schema from migration files or database
3. Infer field types using three-layer strategy
4. Generate code from version-specific templates
5. Write files to appropriate project directories
6. Output TODO list for manual completion steps

### Guide Mode (Development Assistance)

Ask questions about QSCMF development:

**Example prompts:**
```
"How to implement QsListController CRUD?"
"How to use AntdAdmin Table component?"
"How to write PHPUnit tests?"
"How to configure GyListModel validation rules?"
```

## Advanced Usage Patterns

### Abstract Base Pattern

For multiple similar modules, use abstract base classes:

```php
// Abstract base controller
abstract class BaseCategoryController extends QsListController
{
    protected abstract function getCategoryType(): string;

    public function index()
    {
        $type = $this->getCategoryType();
        // Shared logic...
    }
}

// Concrete implementations
class ProductCategoryController extends BaseCategoryController
{
    protected function getCategoryType(): string
    {
        return 'product';
    }
}
```

### Redis Lock Pattern

For concurrent operations:

```php
use Gy_Library\RedisLock;

class BatchController extends QsListController
{
    public function batchProcess()
    {
        $lock = new RedisLock('batch_process', 30);

        if (!$lock->acquire()) {
            $this->error('Another process is running');
        }

        try {
            // Process...
        } finally {
            $lock->release();
        }
    }
}
```

### Queue + Job Pattern

For async tasks:

```php
// Job class
class ProcessOrderJob
{
    public function perform()
    {
        $orderId = $this->args['order_id'];
        // Process order...
    }
}

// Dispatch
Resque::enqueue('default', 'ProcessOrderJob', ['order_id' => $orderId]);
```

### Wall Class Pattern

For external API mocking in tests:

```php
class PaymentWall
{
    public function charge(float $amount): array
    {
        if (env('MOCK_PAYMENT')) {
            return ['success' => true, 'transaction_id' => 'mock_123'];
        }
        return $this->realCharge($amount);
    }
}
```

## API Differences: v13 vs v14

### Version Feature Matrix

| Feature | v13 | v14 |
|---------|-----|-----|
| **PHP Version** | 8.2 | 8.2+ |
| **PHPUnit** | ^9.3.0 | ^10.0 |
| **Primary UI API** | `ListBuilder` | `AntdAdmin\Component\Table` |
| **Backward Compat API** | N/A | `ListBuilder` (jQuery mode) |
| **Rendering** | jQuery + Bootstrap | React + Ant Design |
| **Frontend Framework** | Traditional templates | Inertia.js SPA |
| **HasLayoutProps Trait** | No | Yes |
| **X-Inertia Headers** | No | Yes |

### v13 API: ListBuilder (jQuery Rendering)

v13 uses the `\Qscmf\Builder\ListBuilder` API exclusively:

```php
// v13 Admin Controller Example
$builder = new \Qscmf\Builder\ListBuilder();
$builder->setMetaTitle('Product List')
    ->addTableColumn('id', 'ID')
    ->addTableColumn('name', 'Name')
    ->addTableColumn('status', 'Status', 'status')
    ->addTopButton('addnew', ['title' => 'Add Product'])
    ->addRightButton('edit')
    ->addRightButton('delete')
    ->addSearchItem('keyword', 'text', 'Search')
    ->setTableDataList($data_list)
    ->setTableDataPage($page->show())
    ->build();
```

**Key Methods:**
- `setMetaTitle($title)` - Set page title
- `addTableColumn($field, $title, $type)` - Add column
- `addTopButton($type, $options)` - Add toolbar button
- `addRightButton($type)` - Add row action button
- `addSearchItem($field, $type, $label)` - Add search field
- `setTableDataList($data)` - Set data source
- `build()` - Render the list

### v14 API: AntdAdmin Component (React Rendering)

v14 introduces a modern React-based API:

```php
// v14 Admin Controller Example (Modern API)
$table = new \AntdAdmin\Component\Table();
$table->setMetaTitle('Product List')
    ->actions(function (\AntdAdmin\Component\Table\ActionsContainer $container) {
        $container->button('Add Product')
            ->setProps(['type' => 'primary'])
            ->modal(...);
    })
    ->columns(function (\AntdAdmin\Component\Table\ColumnsContainer $container) {
        $container->text('id', 'ID');
        $container->text('name', 'Name');
        $container->status('status', 'Status');
        $container->action('', 'Actions')->actions(function ($container) {
            $container->edit();
            $container->delete();
        });
    })
    ->setDataSource($data_list)
    ->setPagination(new \AntdAdmin\Component\Table\Pagination($page, $limit, $count))
    ->render();
```

**Key Methods:**
- `setMetaTitle($title)` - Set page title
- `actions($callback)` - Define toolbar actions
- `columns($callback)` - Define table columns
- `setDataSource($data)` - Set data source
- `setPagination($pagination)` - Set pagination
- `render()` - Render the component

**Column Types:**
- `text($field, $title)` - Text column
- `status($field, $title)` - Status column with switch
- `image($field, $title)` - Image column
- `action($field, $title)` - Action column
- `date($field, $title)` - Date column
- `number($field, $title)` - Number column

### v14 API: ListBuilder (Backward Compatibility)

v14 also supports the legacy `ListBuilder` API:

```php
// v14 can still use ListBuilder API (jQuery rendering mode)
// Set ANTD_ADMIN_BUILDER_ENABLE = false in config
$builder = new \Qscmf\Builder\ListBuilder();
// ... same as v13 example above
$builder->build();
```

### Choosing the Right API

| Scenario | Recommended API |
|----------|-----------------|
| New v14 project | `AntdAdmin\Component\Table` (React) |
| Migrating from v13 | `ListBuilder` first, then migrate to Component API |
| v13 project | `ListBuilder` only |
| Need React SPA features | v14 with Component API |
| Legacy jQuery requirements | v13 or v14 with ListBuilder |

## Core Base Classes

| Component | Base Class | Purpose | Location |
|-----------|-----------|---------|----------|
| Admin CRUD | `QsListController` | Backend management UI with AntdAdmin | `app/Admin/Controller/` |
| RESTful API | `RestController` | JSON API endpoints | `app/Api/Controller/` |
| Model | `GyListModel` | Data access with caching, validation | `app/Common/Model/` |
| CLI Controller | `CliModeHelperController` | Command-line batch scripts | `app/Cli/Controller/` |

## Database Constants

Use `Gy_Library\DBCont` for standard status values:

```php
use Gy_Library\DBCont;

// Status values
DBCont::NORMAL_STATUS   // = 1 (enabled)
DBCont::DISABLE_STATUS  // = 0 (disabled)
DBCont::AUDIT_STATUS    // = 2 (pending review)

// Usage
if ($status === DBCont::NORMAL_STATUS) {
    // Item is enabled
}
```

## Common Development Commands

```bash
# Database migrations (run from project root)
php artisan make:migration create_table_name
php artisan migrate
php artisan migrate:rollback

# ThinkPHP CLI execution
php www/index.php <module>/<controller>/<action>

# Run tests
vendor/bin/phpunit

# Run specific test
vendor/bin/phpunit tests/Feature/ProductTest.php

# Queue worker
QUEUE_ENV=prod QUEUE_COUNT=1 php app/queue_resque.php
```

## Iron Laws

### Scaffold
```
NO MIGRATION METADATA, NO CODE GENERATION
```

### Testing
```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
RED-GREEN-REFACTOR CYCLE
```

### Admin CRUD
```
NO ADMIN CRUD WITHOUT MIGRATION METADATA FIRST
```

## Related Resources

- **[v13/SKILL.md](v13/SKILL.md)** - Complete v13 workflow
- **[v14/SKILL.md](v14/SKILL.md)** - Complete v14 workflow
- **[Glossary](_shared/references/glossary.md)** - Common terms and definitions

## License

This skill is part of the QSCMF Skills repository and follows the same license terms.

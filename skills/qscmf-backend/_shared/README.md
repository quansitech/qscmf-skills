# QSCMF - QSMCF Backend3 Skills

This repository provides Claude Code AI skills for developing applications using the QSMCF framework (QuickStart Management Framework), version 3.x. QSMCF is a modern PHP framework built on Laravel 10+ with TypeScript support and advanced features.

## Repository Structure

```
qsmcf-backend3/
├── _shared/                    # Shared content across all versions
│   ├── README.md               # Unified skill introduction and usage
│   ├── coding-style.md         # PHP 8.2+ coding standards
│   ├── api-controllers.md      # RESTful API patterns with QsListController/ListBuilder
│   ├── model-guide.md          # GyListModel patterns with ListBuilder integration
│   ├── development-standards.md # PHP 8.2+ development standards
│   ├── migration-metadata.md  # Enhanced metadata system for code generation
│   └── abstract-base-patterns.md # Reusable base class patterns
├── v13/                       # Version 13 (Laravel 9/10, PHP 8.1+)
│   ├── README.md              # Version-specific details
│   ├── templates/             # Code generation templates
│   └── rules/                 # Version-specific extensions
├── v14/                       # Version 14 (Laravel 11, PHP 8.3+)
│   ├── README.md              # Version-specific details
│   ├── templates/             # Code generation templates
│   └── rules/                 # Version-specific extensions
└── SKILL.md                   # Complete skill workflow (START HERE)
```

## How to Use This Repository

This is a **skills repository**, not a QSMCF application itself. The skills here are designed to be installed into Claude Code's skills directory and used when working on actual QSMCF projects.

### Installation for Claude Code

```bash
# Clone this repository
git clone https://github.com/quansitech/qsmcf-backend3.git

# Create symbolic link to Claude Code's skills directory
ln -s /path/to/qsmcf-backend3/ /root/.claude/skills/qsmcf-backend3
```

## QSMCF Framework Architecture

### Core Components

| Component | Base Class | Purpose | Location |
|-----------|-----------|---------|----------|
| Admin CRUD | `QsListController` | Backend management UI with AntdAdmin | `app/Admin/Controller/` |
| RESTful API | `RestController` | JSON API endpoints | `app/Api/Controller/` |
| Model | `GyListModel` | Data access with caching, validation | `app/Common/Model/` |
| List Builder | `ListBuilder` | Dynamic list building with AntdAdmin components | `app/Common/ListBuilder/` |

### Database Constants

Use `Gy_Library\DBCont` for standard status values:
- `DBCont::NORMAL_STATUS` = 1 (enabled)
- `DBCont::DISABLE_STATUS` = 0 (disabled)
- `DBCont::AUDIT_STATUS` = 2 (pending review)

## Common Development Commands

```bash
# Database migrations (run from project root)
cd /path/to/qsmcf/project
php artisan make:migration create_table_name
php artisan migrate
php artisan migrate:rollback

# Laravel CLI commands
php artisan make:model ModelName
php artisan make:controller Admin/ModelController
php artisan make:resource ModelResource

# Run tests
vendor/bin/phpunit

# Run specific test
vendor/bin/phpunit tests/Feature/ModelTest.php

# Queue worker
php artisan queue:work
```

## Version-Specific Features

### Version 13 (Laravel 9/10, PHP 8.1+)
- Legacy jQuery for frontend
- AntdAdmin v5 components
- Blade templates with legacy syntax
- `ListBuilder` class without type hints

### Version 14 (Laravel 11, PHP 8.3+)
- Modern Vue 3 composition API
- AntdAdmin v6+ components
- Blade templates with modern syntax
- `ListBuilder` class with full PHP 8.3+ type hints

## Skill Operation Modes

The qsmcf-backend3 skill operates in two distinct modes:

### 1. Scaffold Mode (Code Generation)

**Trigger Keywords**: "创建", "生成", "scaffold", "模块", "CRUD", "API"

**Example prompts**:
- "创建 Product 模块，需要后台 CRUD 和 API"
- "生成 User API"
- "QSCMF scaffold Order"

**Workflow**:
1. Identify module name and required components
2. Parse table schema from migration files or database
3. Infer field types using three-layer strategy
4. Generate code from version-specific templates
5. Write files to appropriate project directories
6. Output TODO list for manual completion steps

### 2. Guide Mode (Development Assistance)

Default mode for answering QSMCF development questions.

**Example prompts**:
- "如何实现 QsListController 的 CRUD？"
- "AntdAdmin Table 组件如何使用？"
- "如何编写 PHPUnit 测试？"
- "GyListModel 验证规则如何配置？"

## Field Type Inference System

The skill uses a three-layer strategy for determining form field types:

1. **Configuration Layer**: `.claude/qsmcf/field-rules.yaml` (project-specific overrides)
2. **Learning Layer**: Scan existing controllers to learn patterns
3. **Default Layer**: Field name suffix patterns (e.g., `*_content` → ueditor, `*_date` → date, `status` → select)

## Code Generation Templates

Version-specific templates located in `v13/templates/` and `v14/templates/`:
- `model.php.tpl` - GyListModel with CRUD methods, caching, validation
- `admin_controller.php.tpl` - QsListController with AntdAdmin Table/Form
- `api_controller.php.tpl` - RestController with JSON responses
- `test_case.php.tpl` - PHPUnit test cases with mocking

## Generated File Structure

When generating code for a module (e.g., "Product"):

```php
Model:          app/Common/Model/ProductModel.php
AdminController: app/Admin/Controller/ProductController.php
ApiController:  app/Api/Controller/ProductController.php
Migration:      database/migrations/xxxx_create_products_table.php
Test:          tests/Feature/ProductTest.php
```

## Key Reference Documentation

The `_shared/references/` directory contains comprehensive guides applicable to all versions:

- **api-controllers.md** - RESTful API development with QsListController/ListBuilder
- **model-guide.md** - GyListModel patterns, validation, query methods
- **development-standards.md** - PHP 8.2+ coding standards
- **migration-metadata.md** - Enhanced metadata system for code generation
- **abstract-base-patterns.md** - Reusable base class patterns

## Version Detection

The skill automatically detects QSMCF version from `composer.json`:
- `laravel/framework ^9.0` → v13 (Laravel 9/10, PHP 8.1+)
- `laravel/framework ^11.0` → v14 (Laravel 11, PHP 8.3+)

## Auto-Detection

The skill automatically detects QSMCF projects by looking for:
- `app/` directory (Laravel application)
- `app/Admin/Controller/` directory (Admin controllers)
- `app/Common/Model/` directory (Models)
- `app/Common/ListBuilder/` directory (List builders)

## PHP 8.2+ Coding Standards

When writing QSMCF code:
- Use type declarations on all methods: `public function getUserById(int $id): ?User`
- Use strict comparisons: `if ($status === DBCont::NORMAL_STATUS)`
- Use arrow functions for simple callbacks: `fn($item) => (int)$item['id']`
- Use match expressions instead of switch where appropriate
- Always handle transactions with proper rollback on errors

## Testing Guidelines

- Write PHPUnit tests in `tests/Feature/`
- Use `TestCase::class` base with Laravel testing features
- Mock external APIs using Laravel HTTP client
- Test both success and failure paths
- Use data providers for multiple scenarios

## Related Skills

For development with related frameworks:
- [qscmf-backend](../qscmf-backend/) - Legacy QSCMF framework (ThinkPHP + Laravel hybrid)
- [qscmf-frontend](../qscmf-frontend/) - Frontend development skills

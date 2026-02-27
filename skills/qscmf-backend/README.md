# QSCMF Backend Development Skill

A comprehensive Claude Code AI skill for developing applications using the QSCMF framework (QuickStart Content Management Framework). This skill provides intelligent assistance for both code generation (scaffolding) and development guidance.

> **Start Here**: See [SKILL.md](./SKILL.md) for the complete workflow and version detection.

## Overview

QSCMF is a hybrid PHP framework combining:
- **ThinkPHP 3.2** (legacy layer) - Business logic, controllers, models
- **Laravel** (modern layer) - Database migrations, testing, dependency injection

This skill supports multiple versions with different rendering modes:
- **jQuery Mode**: ListBuilder API with traditional rendering
- **React Mode**: AntdAdmin Component API with Inertia.js SPA

## Installation

### Prerequisites
- Claude Code CLI installed
- A QSCMF project to work on

### Installation Steps

```bash
# Clone this repository
git clone https://github.com/quansitech/qscmf-skills.git

# Create symbolic link to Claude Code's skills directory
ln -s /path/to/qscmf-skills/skills/qscmf-backend/ /root/.claude/skills/qscmf-backend
```

## Quick Start

1. **Version Detection**: The skill auto-detects your QSCMF version from `composer.json`
2. **Start Here**: Open [SKILL.md](./SKILL.md) for the complete workflow
3. **Choose Operation Mode**:
   - **Scaffold Mode**: Code generation (triggered by "创建", "生成", "CRUD")
   - **Guide Mode**: Development assistance for QSCMF questions

## File Structure

```
qscmf-backend/
├── SKILL.md                   # Main skill workflow (START HERE)
├── README.md                  # This file
├── _shared/                   # Shared content across all versions
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
│   └── learn/                 # Learning system for knowledge capture
│       ├── workflow.md        # Learning workflow
│       └── deep-scan-impl.md  # Deep scan implementation
├── v{version}/                # Version-specific content
│   ├── SKILL.md               # Version workflow
│   ├── README.md              # Version details
│   ├── templates/             # Code generation templates
│   └── rules/                 # Version-specific rules
```

## Core Base Classes

| Component | Base Class | Purpose | Location |
|-----------|-----------|---------|----------|
| Admin CRUD | `QsListController` | Backend management UI | `app/Admin/Controller/` |
| RESTful API | `RestController` | JSON API endpoints | `app/Api/Controller/` |
| Model | `GyListModel` | Data access with caching, validation | `app/Common/Model/` |
| CLI Controller | `CliModeHelperController` | Command-line batch scripts | `app/Cli/Controller/` |

## Database Constants

Use `Gy_Library\DBCont` for standard status values:

```php
use Gy_Library\DBCont;

// Status values
DBCont::NORMAL_STATUS   // = 1 (enabled)
DBCont::FORBIDDEN_STATUS  // = 0 (disabled)
DBCont::AUDIT_STATUS    // = 2 (pending review)
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

## Learning System

After a QSCMF development session, use `/qscmf-learn` to capture learnings and improve this skill. See [Learning Workflow](_shared/learn/workflow.md) for details.

## Related Resources

- **[SKILL.md](./SKILL.md)** - Complete workflow and version detection
- **[Glossary](_shared/references/glossary.md)** - Common terms and definitions

## License

This skill is part of the QSCMF Skills repository and follows the same license terms.

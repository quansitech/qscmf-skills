---
name: qscmf-backend
description: |
  QSCMF framework backend development. Auto-detects version from composer.json.

  **Version Detection**: Reads composer.json for `tiderjian/think-core` version.
  - `^14.0` -> v14 (PHP 8.2+, PHPUnit 10, AntdAdmin Component API, Inertia.js)
  - `^13.0` -> v13 (PHP 8.2, PHPUnit 9, ListBuilder API, jQuery)
  - not found -> v14 (default to latest)

  **API Differences**:
  - v13: Uses `\Qscmf\Builder\ListBuilder` API (jQuery rendering)
  - v14: Uses `\AntdAdmin\Component\Table` API (React rendering) OR ListBuilder API (backward compat)

  **Operation Modes**:
  - Scaffold Mode: Code generation triggered by "创建", "生成", "scaffold", "CRUD"
  - Guide Mode: Development assistance for QSCMF questions
  - Learning Mode: Capture knowledge via `/qscmf-learn` after sessions

  **Project Detection**: Activates when project contains app/ + lara/ directories.

  **Version Override**: Use "qscmf-backend v14 ..." or "qscmf-backend v13 ..." to force version.

  Triggers: "创建", "生成", "CRUD", "API", "QsListController", "GyListModel", "/qscmf-learn", "/qscmf-backend"
---

# QSCMF Backend Development

## Version Detection

This skill auto-detects your QSCMF version from `composer.json`:

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
"qscmf-backend v14 创建 Product 模块"
"v14 生成 Order CRUD"

# Force v13 mode
"qscmf-backend v13 创建 Product 模块"
"v13 如何配置 ListBuilder"
```

## Project Detection

This skill activates when your project has QSCMF structure:

| Indicator | Description |
|-----------|-------------|
| `app/` directory | ThinkPHP layer (controllers, models, views) |
| `lara/` directory | Laravel layer (migrations, tests) |
| `Gy_Library` namespace | Core framework library |
| AntdAdmin components | v14 React components |

## Quick Navigation

- **Using v14?** -> Continue to [v14/SKILL.md](v14/SKILL.md)
- **Using v13?** -> Continue to [v13/SKILL.md](v13/SKILL.md)

## Shared Concepts

The following concepts apply to all versions:

- **[Framework Architecture](_shared/concepts/architecture.md)** - ThinkPHP + Laravel hybrid structure
- **[Core Concepts](_shared/concepts/core-concepts.md)** - ListBuilder API, AntdAdmin Component API, GyListModel, DBCont
- **[Version History](_shared/concepts/version-history.md)** - Evolution from v13 to v14

## Migration Guides

- **[Migration: v13 to v14](_shared/references/migration-v13-to-v14.md)** - Upgrade guide between versions

## Terminology

- **[Glossary](_shared/references/glossary.md)** - Common terms and definitions

## Version Feature Matrix

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

## API Architecture (CRITICAL)

### v13 API: ListBuilder

v13 uses the `\Qscmf\Builder\ListBuilder` API exclusively with jQuery rendering:

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

### v14 API: AntdAdmin Component (Primary)

v14 introduces a **new React-based API** using `\AntdAdmin\Component\Table`:

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
        $container->action('', '操作')->actions(function ($container) {
            $container->edit();
            $container->delete();
        });
    })
    ->setDataSource($data_list)
    ->setPagination(new \AntdAdmin\Component\Table\Pagination($page, $limit, $count))
    ->render();
```

### v14 API: ListBuilder (Backward Compatibility)

v14 also supports the legacy `ListBuilder` API for backward compatibility:

```php
// v14 can still use ListBuilder API (jQuery rendering mode)
// Set ANTD_ADMIN_BUILDER_ENABLE = false in config
$builder = new \Qscmf\Builder\ListBuilder();
// ... same as v13 example above
$builder->build();
```

## Choosing the Right API

| Scenario | Recommended API |
|----------|-----------------|
| New v14 project | `AntdAdmin\Component\Table` (React) |
| Migrating from v13 | `ListBuilder` first, then migrate to Component API |
| v13 project | `ListBuilder` only |
| Need React SPA features | v14 with Component API |
| Legacy jQuery requirements | v13 or v14 with ListBuilder |

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

After a QSCMF development session, capture learnings to improve this skill:

### Trigger

Invoke `/qscmf-learn` to analyze the conversation and propose improvements.

### What It Does

1. **Detects Version** - Reads composer.json or scans conversation context
2. **Analyzes Conversation** - Scans entire history for QSCMF patterns, API usage, discoveries
3. **Categorizes Learnings** - Maps to appropriate skill locations (patterns, APIs, field types, templates)
4. **Groups by Risk** - Minor updates, new content, and modifications
5. **Requires Confirmation** - You select which proposals to apply
6. **Logs Changes** - Maintains traceability in `_shared/learn/log.yaml`

### Learning Categories

| Category | Target | Example |
|----------|--------|---------|
| **Pattern** | `rules/pattern/pattern-{name}.md` | Redis Lock for concurrent batches |
| **API Usage** | `rules/{api}.md` or `references/{topic}.md` | TableContainer setDataSource() method |
| **Field Type** | `rules/field-type-inference.md` | *_price fields → number input |
| **Template** | `templates/{component}.php.tpl` | Export form boilerplate |
| **Version Diff** | `_shared/references/migration-v*.md` | v14 Form validation differences |

### Workflow Details

→ See [Learning Workflow](_shared/learn/workflow.md) for complete implementation details

### Example Usage

```bash
# After working on QSCMF code
/qscmf-learn

# Output:
# Learning Proposals (3 items found)
#
# ### Minor Updates (1) - Batch Apply
# - [x] Fix typo in pattern-redis-lock.md
#
# ### New Content (2) - Review & Confirm
# - [ ] Field type rule: *_price → number
# - [ ] API usage: TableContainer setDataSource()
#
# [Apply Minor] [Review Selected] [Cancel]
```

## Getting Started

1. **Detect your version**: Check `composer.json` for `tiderjian/think-core`
2. **Navigate to version**: Open [v14/SKILL.md](v14/SKILL.md) or [v13/SKILL.md](v13/SKILL.md)
3. **Choose operation mode**:
   - Scaffold Mode: Generate CRUD modules
   - Guide Mode: Get development assistance
4. **Follow the workflow**: Each version SKILL.md provides complete instructions

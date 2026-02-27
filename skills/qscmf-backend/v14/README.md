# QSCMF Backend - Version 14

This directory contains version-specific implementation details for QSCMF v14.

> **Note**: For version detection, see the root [SKILL.md](../SKILL.md).

## Version Overview

QSCMF v14 features:
- **PHP 8.2+** with strict typing
- **PHPUnit 10** for testing
- **AntdAdmin** React components
- **Inertia.js** for SPA-like navigation
- **ListBuilder API** (same as v13, with React rendering)

## Rendering Mode

v14 uses `ANTD_ADMIN_BUILDER_ENABLE` to control rendering:
- `ANTD_ADMIN_BUILDER_ENABLE = true` (default) → React/AntdAdmin rendering
- `ANTD_ADMIN_BUILDER_ENABLE = false` → jQuery rendering (backward compatible)

## Key Features

### Inertia.js Integration

```php
use Qscmf\Lib\Inertia\HasLayoutProps;

class DashboardController extends QsListController
{
    use HasLayoutProps;

    public function index()
    {
        $this->shareLayoutProps([
            'title' => 'Dashboard',
            'breadcrumbs' => [
                ['title' => 'Home', 'href' => '/'],
                ['title' => 'Dashboard'],
            ],
        ]);
        // ... rest of controller
    }
}
```

### Direct AntdAdmin Component Usage

For advanced scenarios beyond ListBuilder, use direct AntdAdmin components:

```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Table\Pagination;

public function index()
{
    $table = new Table();
    $table->setMetaTitle('商品列表')
        ->columns(function (Table\ColumnsContainer $container) {
            $container->text('product_name', '商品名称');
            $container->select('status', '状态')
                ->setValueEnum(DBCont::getStatusList())
                ->setBadge([1 => 'success', 0 => 'default']);
        })
        ->setDataSource($data_list)
        ->setPagination(new Pagination($page, $limit, $count))
        ->render();
}
```

## Configuration

### composer.json
```json
{
    "require": {
        "php": "^8.2",
        "tiderjian/think-core": "^14.0"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.0"
    }
}
```

## Testing

v14 uses PHPUnit 10:

```php
class ProductTest extends TestCase
{
    public function test_index_returns_products(): void
    {
        $response = $this->get('/api/product');

        $response->assertStatus(200)
            ->assertJsonStructure([
                'status',
                'data' => [
                    '*' => ['id', 'product_name', 'status']
                ]
            ]);
    }
}
```

## Directory Structure

```
v14/
├── SKILL.md               # v14 workflow (main entry)
├── README.md              # This file
├── templates/             # Code generation templates
│   ├── admin_controller.php.tpl
│   ├── model.php.tpl
│   ├── api_controller.php.tpl
│   └── test_case.php.tpl
└── rules/                 # Version-specific rules
    ├── listbuilder-api.md
    ├── formbuilder-api.md
    ├── antdadmin.md
    ├── inertia.md
    └── ...
```

## Getting Started

1. Read the [SKILL.md](./SKILL.md) for complete v14 workflow
2. Use shared references from [_shared/](../_shared/) for cross-version concepts

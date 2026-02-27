# QSCMF Framework Architecture

## Overview

QSCMF (QuickStart Content Management Framework) is a **hybrid PHP framework** that combines two powerful ecosystems:

- **ThinkPHP 3.2** - Legacy layer for business logic, controllers, models
- **Laravel** - Modern layer for database migrations, testing, dependency injection

This hybrid architecture allows gradual modernization while maintaining backward compatibility.

## Directory Structure

```
qscmf-project/
├── app/                          # ThinkPHP Layer (Legacy)
│   ├── Admin/                    # Backend admin module
│   │   ├── Controller/           # Admin controllers
│   │   │   └── ProductController.class.php
│   │   └── View/                 # Admin views (jQuery mode)
│   ├── Api/                      # RESTful API module
│   │   └── Controller/           # API controllers
│   ├── Common/                   # Shared components
│   │   ├── Conf/                 # Configuration files
│   │   └── Model/                # Data models
│   │       └── ProductModel.class.php
│   ├── Home/                     # Frontend module
│   └── Cli/                      # CLI commands
│       └── Controller/           # Batch job controllers
│
├── lara/                         # Laravel Layer (Modern)
│   ├── app/                      # Laravel application
│   ├── database/                 # Database management
│   │   └── migrations/           # Schema migrations
│   │       └── 2024_01_01_create_product_table.php
│   ├── tests/                    # PHPUnit tests
│   │   ├── Feature/              # Feature tests
│   │   └── Unit/                 # Unit tests
│   ├── config/                   # Laravel config
│   └── routes/                   # Laravel routes
│
├── vendor/                       # Composer dependencies
│   └── tiderjian/think-core/     # QSCMF core framework
│
├── public/                       # Public web root
│   └── index.php                 # Application entry point
│
├── composer.json                 # Dependency management
└── .env                          # Environment configuration
```

## Layer Responsibilities

### ThinkPHP Layer (`app/`)

| Component | Purpose | Example |
|-----------|---------|---------|
| **Controllers** | HTTP request handling, page rendering | `ProductController.class.php` |
| **Models** | Data access, business logic, validation | `ProductModel.class.php` |
| **Views** | Template rendering (jQuery mode or Inertia) | `index.html` |
| **Configuration** | Module-specific settings | `config.php` |

### Laravel Layer (`lara/`)

| Component | Purpose | Example |
|-----------|---------|---------|
| **Migrations** | Database schema version control | `create_product_table.php` |
| **Tests** | PHPUnit testing framework | `ProductTest.php` |
| **Dependency Injection** | Service container, bindings | `AppServiceProvider.php` |
| **Queue Jobs** | Background job processing | `ProcessOrder.php` |

## Core Framework Components

### Base Classes

| Class | Location | Purpose |
|-------|----------|---------|
| `QsListController` | `Gy_Library\Controller` | Admin CRUD base with ListBuilder |
| `RestController` | `Gy_Library\Controller` | RESTful API base with JSON responses |
| `GyListModel` | `Gy_Library\Model` | Model base with caching, validation |
| `CliModeHelperController` | `Gy_Library\Controller` | CLI batch job base |

### Builder Classes

| Class | Purpose | Rendering |
|-------|---------|-----------|
| `ListBuilder` | Admin data tables with CRUD | jQuery or React mode |
| `FormBuilder` | Admin forms with validation | jQuery or React mode |
| `ModalButtonBuilder` | Modal dialogs | jQuery Bootstrap |

### Database Constants

Use `Gy_Library\DBCont` for standard status values:

```php
use Gy_Library\DBCont;

// Status values
DBCont::NORMAL_STATUS = 1;     // Enabled/Active
DBCont::DISABLE_STATUS = 0;    // Disabled/Inactive
DBCont::AUDIT_STATUS = 2;      // Pending review
DBCont::DELETE_STATUS = -1;    // Soft deleted

// Boolean values
DBCont::BOOLEAN_TRUE = 1;
DBCont::BOOLEAN_FALSE = 0;
```

## Request Flow

### Admin CRUD Request (React mode example)

```
1. Browser Request
   GET /admin/product/index
   |
2. Route Resolution (ThinkPHP)
   Module: Admin
   Controller: ProductController
   Action: index
   |
3. Controller Processing
   ProductController extends QsListController
   |
4. ListBuilder Configuration
   $builder->addTableColumn()
   $builder->addTopButton()
   $builder->addRightButton()
   |
5. Data Retrieval
   D('Product')->getListForPage()
   |
6. Rendering
   ANTD_ADMIN_BUILDER_ENABLE=true
   |
7. Inertia.js Response
   X-Inertia header + JSON props
   |
8. React Component Rendering
   AntdAdmin\Component\Table
```

### API Request Flow

```
1. API Request
   GET /api/products
   |
2. Route Resolution
   Module: Api
   Controller: ProductController
   Action: index
   |
3. Controller Processing
   ProductController extends RestController
   |
4. Data Retrieval
   D('Product')->getListForApi()
   |
5. JSON Response
   $this->apiSuccess($data)
```

## Model Instantiation Patterns

QSCMF uses ThinkPHP's model instantiation:

```php
// D() - Instantiates model with business logic (recommended)
$product_model = D('Product');        // Returns ProductModel instance
$product_model = D('Product/Category'); // Nested model

// M() - Instantiates basic table model (no custom methods)
$product_model = M('Product');        // Returns basic Model instance

// With module prefix
$product_model = D('Admin/Product');  // Admin module's Product model
```

## Configuration Files

### ThinkPHP Configuration (`app/Common/Conf/config.php`)

```php
return [
    // Database
    'DB_TYPE'   => 'mysql',
    'DB_HOST'   => env('DB_HOST', 'localhost'),
    'DB_NAME'   => env('DB_DATABASE'),
    'DB_USER'   => env('DB_USERNAME'),
    'DB_PWD'    => env('DB_PASSWORD'),

    // Admin pagination
    'ADMIN_PER_PAGE_NUM' => 20,

    // React mode: Enable AntdAdmin rendering
    'ANTD_ADMIN_BUILDER_ENABLE' => true,
];
```

### Laravel Configuration (`lara/config/`)

```php
// database.php - Database connections
// queue.php - Queue configuration
// app.php - Application settings
```

## Hybrid Framework Benefits

| Benefit | Description |
|---------|-------------|
| **Gradual Migration** | Modernize incrementally without full rewrite |
| **Laravel Tooling** | Access to migrations, queues, testing |
| **ThinkPHP Stability** | Proven business logic layer |
| **Shared Database** | Both layers use same database |
| **Dependency Injection** | Laravel container available in ThinkPHP |

## Key Integration Points

### 1. Database Access

Both layers share the same database:

```php
// ThinkPHP style (in app/)
$products = D('Product')->where(['status' => 1])->select();

// Laravel style (in lara/)
$products = DB::table('product')->where('status', 1)->get();
```

### 2. Configuration Sharing

Environment variables in `.env` are accessible from both layers:

```php
// Both work in ThinkPHP and Laravel
env('DB_HOST')
env('APP_ENV')
```

### 3. Service Container

Laravel's service container is available:

```php
// In ThinkPHP controller
$app = app();  // Laravel container
$service = app(MyService::class);
```

## Common Commands

```bash
# Database migrations (from project root)
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

## Rendering Modes

| Aspect | jQuery Mode | React Mode |
|--------|-------------|------------|
| **Rendering** | jQuery + Bootstrap | React + AntdAdmin |
| **Frontend** | Traditional templates | Inertia.js SPA |
| **API** | Mixed HTML/JSON | Clean JSON responses |
| **Testing** | PHPUnit 9 | PHPUnit 10 |

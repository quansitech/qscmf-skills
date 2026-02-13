---
name: qscmf-backend
description: |
  QSCMF framework (ThinkPHP 3.2 + Laravel hybrid) backend development and code generation.

  **Auto-detects QSCMF projects**: Contains app/ + lara/ directories, Gy_Library, AntdAdmin components.

  **Scaffold Mode** (在 QSCMF 项目中自动触发, or 强制触发 with "QSCMF"):
  - "创建 Product 模块" → Generate CRUD module (in QSCMF project context)
  - "生成 User API" → Generate RESTful API (in QSCMF project context)
  - "QSCMF scaffold Order" → Force trigger scaffold mode
  - "创建 QSCMF CRUD for Article" → Explicit framework reference

  **Guide Mode** (QSCMF 开发问题):
  - "如何实现 QsListController CRUD?" - Admin development
  - "AntdAdmin Table 组件如何使用?" - UI components
  - "如何编写 PHPUnit 测试?" - Testing patterns
  - "GyListModel 验证规则?" - Model development

  **When to use**: Any QSCMF backend development (CRUD, API, tests, migrations) in projects with QSCMF structure.
---

# QSCMF Backend Development

## Mode Selection

This skill operates in two modes based on user request:

### Scaffold Mode (Code Generation)

Triggers: "创建", "生成", "scaffold", "模块", "CRUD", "API"

**Quick Start**:
```markdown
User: 创建 Product 模块，需要后台 CRUD 和 API

AI Workflow:
  1. Identify: Module=Product, Requirements=CRUD+API
  2. Parse schema from migration or database
  3. Infer field types using three-layer strategy
  4. Generate code from templates
  5. Write files to project directories
  6. Output TODO list for manual steps
```

See [Scaffold Workflow](#scaffold-workflow) below.

### Guide Mode (Development Guide)

Default mode for QSCMF development questions.

**Quick Start**:
```markdown
User: 如何实现 QsListController 的 CRUD？
User: AntdAdmin Table 组件如何使用？
User: 如何编写 PHPUnit 测试？
```

See [Framework Guide](#framework-guide) below.

---

## Scaffold Workflow

### Step 1: Identify Requirements

Extract from user request:
- **Module name**: Product, User, Order, etc.
- **Components needed**:
  - Model? (GyListModel)
  - AdminController? (QsListController + AntdAdmin)
  - ApiController? (RestController)
  - Migration? (Laravel Schema)
  - Test? (PHPUnit)

### Step 2: Parse Table Schema

**Option A**: From Migration (preferred)
```bash
# Find migration file
ls lara/database/migrations/*create_product*
```

**Option B**: Using script
```bash
php scripts/parse_schema.php qs_product
```

Output:
```json
{
  "table": "qs_product",
  "fields": [
    {"name": "product_name", "type": "varchar(200)", "comment": "@title=产品名称;@type=text"},
    {"name": "cover", "type": "int", "comment": "@title=封面图;@type=image"},
    {"name": "status", "type": "tinyint", "comment": "@title=状态;@type=select"}
  ]
}
```

### Step 3: Infer Field Types

Use three-layer inference:

**Layer 1**: Configuration
```yaml
# .claude/qscmf/field-rules.yaml
product_content: ueditor
*_date: date
status: select
cover: image
```

**Layer 2**: Learning from code
```bash
php scripts/infer_types.php --scan app/Admin/Controller/
```

**Layer 3**: Default rules
```php
// Field name suffix patterns
*_content → ueditor
*_date → date
*_time → time
*_id → select/foreign
status → select
cover → image
file_id → file
sort → number
```

### Step 4: Generate Code

Use templates from `assets/templates/`:

**Model Template** → `model.php.tpl`
```php
class {{MODEL_NAME}}Model extends GyListModel
{
    protected $_validate = [
{{VALIDATE_RULES}}
    ];
}
```

**AdminController Template** → `admin_controller.php.tpl`
```php
class {{MODEL}}Controller extends QsListController
{
    public function index() {
        $table = new Table();
{{TABLE_COLUMNS}}
        return $table->render();
    }

    protected function buildTableColumns($container) {
        $container->text('{{FIELD_NAME}}', '{{FIELD_TITLE}}');
    }
}
```

**ApiController Template** → `api_controller.php.tpl`
```php
class {{MODEL}}Controller extends RestController
{
    public function gets(): Response {
        // ...
    }
}
```

### Step 5: Write Files

Rules:
- ✅ Create new files
- ❌ Skip existing files (unless --force confirmed)
- 📁 Maintain proper directory structure

File paths:
```
Model:          app/Common/Model/{{MODEL}}Model.class.php
AdminController: app/Admin/Controller/{{MODEL}}Controller.class.php
ApiController:  app/Api/Controller/{{MODEL}}Controller.class.php
Migration:      lara/database/migrations/xxxx_create_{{table}}_table.php
Test:           lara/tests/Feature/{{MODEL}}Test.php
```

### Step 6: Output TODO List

```markdown
✅ Generated files:
  - app/Common/Model/ProductModel.class.php
  - app/Admin/Controller/ProductController.class.php
  - app/Api/Controller/ProductController.class.php

📝 TODO (manual):
  - [ ] Run migration: php artisan migrate
  - [ ] Configure permissions in qs_node table
  - [ ] Add validation rules in Model::$_validate
  - [ ] Implement business logic (save, delete hooks)
  - [ ] Add foreign key relationships
  - [ ] Run tests: vendor/bin/phpunit

📚 References:
  - Admin Controllers: references/admin-controllers.md
  - Testing Guide: references/development-standards.md
```

---

## Framework Guide

### Quick Reference

#### Standard CRUD Module

```php
// 1. Migration (lara/database/migrations/)
Schema::create('qs_demo', function (Blueprint $table) {
    $table->id();
    $table->string('title', 200)->comment('标题');
    $table->text('content')->nullable()->comment('内容');
    $table->tinyInteger('status')->default(1)->comment('状态');
    $table->timestamps();
});

// 2. Model (app/Common/Model/)
class DemoModel extends GyListModel
{
    protected $_validate = [
        ['title', 'require', '标题不能为空', self::MUST_VALIDATE],
    ];
}

// 3. Controller (app/Admin/Controller/)
class DemoController extends QsListController
{
    // See references/admin-controllers.md for full code
}
```

#### RESTful API

```php
namespace Api\Controller;

use Qscmf\Api\RestController;
use QscmfApiCommon\Cache\Response;

class DemoController extends RestController
{
    protected $noAuthorization = ['gets', 'detail'];

    public function gets(): Response
    {
        $get_data = I('get.');
        // ...
        return new Response('成功', 1, $data);
    }
}
```

See [API Controllers](references/api-controllers.md).

#### Unit Testing

```php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;

class DemoTest extends TestCase
{
    public function testGetList(): void
    {
        $response = $this->get('/api.php/Demo/gets');
        $response->assertStatus(200)->assertJson(['status' => 1]);
    }

    public function testWithMock(): void
    {
        $mock = $this->createMock(ApiService::class);
        $mock->method('fetch')->willReturn(['success' => true]);
        app()->instance(ApiService::class, $mock);

        $result = D('Demo')->processData(123);
        $this->assertTrue($result);
    }
}
```

See [Development Standards](references/development-standards.md).

---

### Common Code Patterns

#### Table Columns

```php
$container->text('title', '标题');
$container->select('status', '状态')
    ->setValueEnum(DBCont::getStatusList());
$container->date('create_time', '创建时间')->setSearch(false);
$container->text('sort', '排序')->editable();
$container->action('', '操作')
    ->actions(function ($container) {
        $container->edit()->modal(...);
        $container->delete();
    });
```

#### Form Fields

```php
$columns->text('title', '标题')
    ->addRule(new Required())
    ->setFormItemWidth(24);

$columns->image('cover_id', '封面图')
    ->setUploadRequest(FormItem\ObjectStorage\Lib\Common::genItemDataUrl('image'))
    ->setCrop('866/490');

$columns->ueditor('content', '详情内容')->setFormItemWidth(24);

$columns->select('cate_id', '分类')
    ->setValueEnum(D('Cate')->getField('id,name'))
    ->addRule(new Required());
```

#### Database Constants

```php
use Gy_Library\DBCont;

DBCont::NORMAL_STATUS      // = 1 (启用)
DBCont::DISABLE_STATUS     // = 0 (禁用)
DBCont::AUDIT_STATUS       // = 2 (待审核)

\Qscmf\Lib\DBCont::getStatusList()    // [1 => '启用', 0 => '禁用']
```

#### PHP 8.2 Best Practices

```php
// ✅ Type declarations
public function getUserById(int $id): ?array
{
    return $this->where(['id' => $id])->find();
}

// ✅ Strict comparison
if ($status === DBCont::NORMAL_STATUS) { }

// ✅ Arrow functions
$ids = array_map(fn($item) => (int)$item['id'], $list);

// ✅ Match expressions
$type = match($field) {
    'content' => 'ueditor',
    'status' => 'select',
    default => 'text'
};
```

---

## Architecture Overview

### Hybrid Framework

**ThinkPHP Layer** (`app/`):
- Business logic, controllers, models
- Use `D('ModelName')` for models
- Use `M()` for raw table operations

**Laravel Layer** (`lara/`):
- Database migrations (Schema Builder)
- Dependency injection, PHPUnit tests

### Core Components

| Component | Base Class | Purpose |
|-----------|-----------|---------|
| Admin Controller | `QsListController` | CRUD management UI |
| API Controller | `RestController` | RESTful API |
| Model | `GyListModel` | Data access layer |

### Development Mode Decision Tree

```
What feature do you need?
│
├─ Admin CRUD
│  ├─ Simple CRUD? → Standard CRUD (QsListController + AntdAdmin)
│  └─ Multiple similar modules? → Abstract Base pattern
│
├─ RESTful API
│  └─ API Controller pattern (RestController)
│
├─ Complex Business Logic
│  ├─ Batch operations? → Custom controller + RedisLock
│  ├─ Async tasks? → Queue + Job
│  └─ External API? → Wall class + Mock testing
│
└─ Frontend Page
   └─ HomeController + Inertia.js + React/TS
```

---

## Common Commands

```bash
# Database
php artisan make:migration create_table_name
php artisan migrate
php artisan migrate:rollback

# ThinkPHP CLI
php www/index.php <module>/<controller>/<action>

# Testing
vendor/bin/phpunit

# Queue
QUEUE_ENV=prod QUEUE_COUNT=1 php app/queue_resque.php
```

---

## References

Detailed guides in `references/`:

### Core Guides

- **[Admin Controllers](references/admin-controllers.md)** - Admin controller guide
  - Standard CRUD pattern
  - Abstract base class pattern
  - Table/Form configuration
  - Knowledge store sync
  - Redis lock usage

- **[API Controllers](references/api-controllers.md)** - API controller guide
  - RestController base class
  - Authentication & authorization
  - Response handling
  - Pagination & filtering
  - Data formatting

- **[CRUD Patterns](references/crud-patterns.md)** - Development patterns
  - Mode selection decision tree
  - Field type configuration
  - Validation rules
  - Business logic encapsulation
  - Performance optimization
  - Concurrency control

- **[Model Guide](references/model-guide.md)** - 模型开发指南
  - GyListModel 代码规范
  - 验证规则
  - 查询方法封装
  - 性能优化（N+1、缓存）
  - 状态变更逻辑
  - 完整模型示例

- **[Migration Guide](references/migration-guide.md)** - 数据库迁移指南
  - 迁移命令
  - 列类型和修饰符
  - 元数据注释系统
  - 枚举列表
  - 索引设计
  - 表结构规范

- **[Where Query Reference](references/where-query-reference.md)** - 查询语法参考
  - Where 条件表达式
  - 聚合查询
  - JOIN 关联
  - 排序和分页

- **[Development Standards](references/development-standards.md)** - Standards & testing
  - PHP 8.2 coding standards
  - React/TypeScript standards
  - Caching & locking
  - Unit testing guide
  - Mock third-party APIs
  - Wall class pattern
  - Code review checklist

### Architecture Patterns

- **[Abstract Base Patterns](references/abstract-base-patterns.md)** - 抽象基类模式
  - 分类模块模式 (ACate/ACateModel)
  - 内容模块模式 (AContent/AContentModel)
  - 标签模块模式 (ATag/ATagModel)
  - 自定义扩展策略

- **[Migration Metadata](references/migration-metadata.md)** - 迁移文件元数据系统
  - 元数据属性和字段类型映射
  - 代码生成规则
  - 枚举列表系统
  - 命名规范和最佳实践

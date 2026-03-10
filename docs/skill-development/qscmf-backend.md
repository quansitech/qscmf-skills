# QSCMF Backend 技能开发文档

> **注意**: 本文档是技能开发者的参考文档，不属于技能包本身。
> 技能入口文件是 `skills/qscmf-backend/SKILL.md`。

## 概览

QSCMF Backend 是一个用于 QSCMF 框架开发的 Claude Code AI 技能包。QSCMF（QuickStart Content Management Framework）是一个混合 PHP 框架，结合了：

- **ThinkPHP 3.2**（遗留层）- 业务逻辑、控制器、模型
- **Laravel**（现代层）- 数据库迁移、测试、依赖注入

### 技能特性

本技能支持两种操作模式：

1. **脚手架模式**（Scaffold Mode）：代码生成，通过关键词触发（如"创建"、"生成"、"CRUD"）
2. **指导模式**（Guide Mode）：QSCMF 开发问题解答

### 渲染模式支持

技能支持多种渲染模式：
- **jQuery 模式**：ListBuilder API 配合传统模板渲染
- **React 模式**：AntdAdmin 组件 API 配合 Inertia.js SPA

### 安装方式

```bash
# 克隆仓库
git clone https://github.com/quansitech/qscmf-skills.git

# 创建符号链接到 Claude Code 的技能目录
ln -s /path/to/qscmf-skills/skills/qscmf-backend/ /root/.claude/skills/qscmf-backend
```

### 文件结构

```
qscmf-backend/
├── SKILL.md                   # 主技能工作流（从这里开始）
├── README.md                  # 概览文档
├── _shared/                   # 跨版本共享内容
│   ├── concepts/              # 核心概念文档
│   │   ├── architecture.md    # 框架架构
│   │   └── core-concepts.md   # ListBuilder, AntdAdmin, GyListModel
│   ├── references/            # 综合指南
│   │   ├── api-controllers.md
│   │   ├── model-guide.md
│   │   ├── development-standards.md
│   │   ├── migration-metadata.md
│   │   ├── abstract-base-patterns.md
│   │   └── glossary.md
│   └── learn/                 # 知识捕获学习系统
│       ├── workflow.md        # 学习工作流
│       └── deep-scan-impl.md  # 深度扫描实现
├── v{version}/                # 版本特定内容
│   ├── SKILL.md               # 版本工作流
│   ├── README.md              # 版本详情
│   ├── templates/             # 代码生成模板
│   └── rules/                 # 版本特定规则
```

### 核心基类

| 组件 | 基类 | 用途 | 位置 |
|------|------|------|------|
| Admin CRUD | `QsListController` | 后台管理界面 | `app/Admin/Controller/` |
| RESTful API | `RestController` | JSON API 端点 | `app/Api/Controller/` |
| Model | `GyListModel` | 数据访问（含缓存、验证） | `app/Common/Model/` |
| CLI Controller | `CliModeHelperController` | 命令行批处理脚本 | `app/Cli/Controller/` |

### 数据库常量

使用 `Gy_Library\DBCont` 获取标准状态值：

```php
use Gy_Library\DBCont;

// 状态值
DBCont::NORMAL_STATUS     // = 1（启用）
DBCont::FORBIDDEN_STATUS  // = 0（禁用）
DBCont::AUDIT_STATUS      // = 2（待审核）
```

### 常用开发命令

```bash
# 数据库迁移（在项目根目录执行）
php artisan make:migration create_table_name
php artisan migrate
php artisan migrate:rollback

# ThinkPHP CLI 执行
php www/index.php <module>/<controller>/<action>

# 运行测试
vendor/bin/phpunit

# 队列工作进程
QUEUE_ENV=prod QUEUE_COUNT=1 php app/queue_resque.php
```

### 铁律

#### 脚手架
```
NO MIGRATION METADATA, NO CODE GENERATION
```

#### 测试
```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
RED-GREEN-REFACTOR CYCLE
```

#### Admin CRUD
```
NO ADMIN CRUD WITHOUT MIGRATION METADATA FIRST
```

---

## Shared Components（共享组件）

此目录包含适用于所有 QSCMF 版本的共享内容。

> **注意**：版本检测在根目录 [SKILL.md](../../skills/qscmf-backend/SKILL.md) 中处理。请先导航到那里确定你的 QSCMF 版本。

### 目录结构

```
_shared/
├── concepts/           # 核心框架概念
│   ├── architecture.md     - ThinkPHP + Laravel 混合结构
│   └── core-concepts.md    - ListBuilder API, AntdAdmin 组件 API, GyListModel, DBCont
├── references/         # 综合参考指南
│   ├── api-controllers.md  - RESTful API 模式
│   ├── model-guide.md      - GyListModel 模式
│   ├── development-standards.md - PHP 8.2+ 编码标准
│   ├── migration-metadata.md - 代码生成的元数据系统
│   ├── abstract-base-patterns.md - 可复用基类模式
│   └── glossary.md         - 常用术语和定义
└── learn/              # 知识捕获学习系统
    ├── workflow.md         - 学习工作流详情
    ├── deep-scan-impl.md   - 深度扫描实现
    ├── version-mapping.yaml - 版本检测和功能映射
    ├── llm-learning-principles.md - LLM 学习的设计决策
    ├── cache.yaml          - 学习缓存结构
    ├── log.yaml            # 学习日志
    └── schema/             # 模式定义
        └── extracted_rules.yaml
```

### 关键参考文档

#### API 开发
- **[api-controllers.md](../../skills/qscmf-backend/_shared/references/api-controllers.md)** - 使用 RestController 的 RESTful API 模式

#### 数据层
- **[model-guide.md](../../skills/qscmf-backend/_shared/references/model-guide.md)** - GyListModel 模式、验证、查询方法
- **[migration-metadata.md](../../skills/qscmf-backend/_shared/references/migration-metadata.md)** - 用于代码生成的增强元数据系统

#### 开发标准
- **[development-standards.md](../../skills/qscmf-backend/_shared/references/development-standards.md)** - PHP 8.2+ 编码标准
- **[abstract-base-patterns.md](../../skills/qscmf-backend/_shared/references/abstract-base-patterns.md)** - 可复用基类模式

#### 框架概念
- **[architecture.md](../../skills/qscmf-backend/_shared/concepts/architecture.md)** - ThinkPHP + Laravel 混合结构
- **[core-concepts.md](../../skills/qscmf-backend/_shared/concepts/core-concepts.md)** - 核心框架组件

#### 术语表
- **[glossary.md](../../skills/qscmf-backend/_shared/references/glossary.md)** - 常用术语和定义

### 学习系统

QSCMF 开发会话结束后，使用 `/qscmf-learn` 捕获学习内容：

- **[workflow.md](../../skills/qscmf-backend/_shared/learn/workflow.md)** - 完整学习工作流
- **[deep-scan-impl.md](../../skills/qscmf-backend/_shared/learn/deep-scan-impl.md)** - 深度扫描实现细节
- **[version-mapping.yaml](../../skills/qscmf-backend/_shared/learn/version-mapping.yaml)** - 版本检测和功能映射
- **[llm-learning-principles.md](../../skills/qscmf-backend/_shared/learn/llm-learning-principles.md)** - LLM 学习效率的设计决策

### 快速开始

1. 查看根目录 [SKILL.md](../../skills/qscmf-backend/SKILL.md) 进行版本检测
2. 导航到你的版本特定 SKILL.md（v13/ 或 v14/）
3. 使用共享参考资料了解跨版本概念

---

## Version 13（版本 13）

此目录包含 QSCMF v13 的版本特定实现细节。

> **注意**：版本检测请参阅根目录 [SKILL.md](../../skills/qscmf-backend/SKILL.md)。

### 版本概览

QSCMF v13 特性：
- **PHP 8.2** 支持类型声明
- **PHPUnit 9** 测试框架
- **jQuery + Bootstrap** 前端渲染
- **ListBuilder API** 传统模板渲染

### 渲染模式

v13 使用 **jQuery + Bootstrap 3** 渲染：

```php
// 环境常量
ANTD_ADMIN_BUILDER_ENABLE = false  // v13 默认值
```

### 关键特性

#### ListBuilder API

v13 使用 ListBuilder API 配合 jQuery/Bootstrap 渲染：

```php
$builder = $this->builder();

// 表格列
$builder->addTableColumn('id', 'ID');
$builder->addTableColumn('name', '名称');
$builder->addTableColumn('status', '状态', DBCont::getStatusList());

// 搜索项
$builder->addSearchItem('keyword', 'text', '关键词');
$builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());

// 按钮
$builder->addTopButton('addnew', ['title' => '新增']);
$builder->addRightButton('edit', ['href' => U('edit', ['id' => '@id@'])]);
$builder->addRightButton('delete', ['href' => U('delete', ['ids' => '@id@'])]);

$builder->display();
```

#### Bootstrap CSS 类

v13 后台页面使用 Bootstrap 3 类：

```html
<!-- 状态标签 -->
<span class="label label-success">启用</span>
<span class="label label-default">禁用</span>

<!-- 按钮 -->
<button class="btn btn-primary">新增</button>
<button class="btn btn-danger">删除</button>
```

#### jQuery 事件处理

```javascript
// 自定义表单提交
$('#myForm').on('submit', function(e) {
    e.preventDefault();
    $.post($(this).attr('action'), $(this).serialize(), function(res) {
        if (res.status) {
            location.reload();
        }
    });
});
```

### 配置要求

#### composer.json
```json
{
    "require": {
        "php": "^8.2",
        "tiderjian/think-core": "^13.0"
    },
    "require-dev": {
        "phpunit/phpunit": "^9.3.0"
    }
}
```

### 测试

v13 使用 PHPUnit 9：

```php
class ProductTest extends TestCase
{
    public function testIndex()
    {
        $response = $this->get('/admin/product/index');
        $response->assertStatus(200);
        $response->assertSee('Product List');
    }
}
```

### 目录结构

```
v13/
├── SKILL.md               # v13 工作流（主入口）
├── README.md              # 本文件
├── templates/             # 代码生成模板
│   ├── admin_controller.php.tpl
│   ├── model.php.tpl
│   ├── api_controller.php.tpl
│   └── test_case.php.tpl
└── rules/                 # 版本特定规则
    ├── listbuilder-api.md
    ├── formbuilder-api.md
    ├── legacy-jquery.md
    └── ...
```

### 快速开始

1. 阅读 [SKILL.md](../../skills/qscmf-backend/v13/SKILL.md) 了解完整的 v13 工作流
2. 使用 [_shared/](../../skills/qscmf-backend/_shared/) 中的共享参考资料了解跨版本概念

---

## Version 14（版本 14）

此目录包含 QSCMF v14 的版本特定实现细节。

> **注意**：版本检测请参阅根目录 [SKILL.md](../../skills/qscmf-backend/SKILL.md)。

### 版本概览

QSCMF v14 特性：
- **PHP 8.2+** 严格类型支持
- **PHPUnit 10** 测试框架
- **AntdAdmin** React 组件
- **Inertia.js** SPA 风格导航
- **ListBuilder API**（与 v13 相同，使用 React 渲染）

### 渲染模式

v14 使用 `ANTD_ADMIN_BUILDER_ENABLE` 控制渲染：
- `ANTD_ADMIN_BUILDER_ENABLE = true`（默认）→ React/AntdAdmin 渲染
- `ANTD_ADMIN_BUILDER_ENABLE = false` → jQuery 渲染（向后兼容）

### 关键特性

#### Inertia.js 集成

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
        // ... 控制器其余代码
    }
}
```

#### 直接使用 AntdAdmin 组件

对于超出 ListBuilder 的高级场景，可直接使用 AntdAdmin 组件：

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

### 配置要求

#### composer.json
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

### 测试

v14 使用 PHPUnit 10：

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

### 目录结构

```
v14/
├── SKILL.md               # v14 工作流（主入口）
├── README.md              # 本文件
├── templates/             # 代码生成模板
│   ├── admin_controller.php.tpl
│   ├── model.php.tpl
│   ├── api_controller.php.tpl
│   └── test_case.php.tpl
└── rules/                 # 版本特定规则
    ├── listbuilder-api.md
    ├── formbuilder-api.md
    ├── antdadmin.md
    ├── inertia.md
    └── ...
```

### 快速开始

1. 阅读 [SKILL.md](../../skills/qscmf-backend/v14/SKILL.md) 了解完整的 v14 工作流
2. 使用 [_shared/](../../skills/qscmf-backend/_shared/) 中的共享参考资料了解跨版本概念

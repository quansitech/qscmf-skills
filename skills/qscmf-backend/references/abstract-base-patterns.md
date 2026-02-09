# Abstract Base Patterns Reference

> QSCMF 抽象基类模式 - 多相似模块的代码复用方案

## 概述

当项目中有多个相似的模块时，使用抽象基类模式可以：

- ✅ 避免重复代码
- ✅ 统一业务逻辑
- ✅ 简化新模块开发
- ✅ 便于维护和升级

## 何时使用抽象基类模式

**适用场景**：
- 项目中有 2+ 个功能相似的模块
- 模块的业务逻辑基本一致，仅配置不同
- 希望统一维护，避免多处修改

**不适用的场景**：
- 单一功能的简单 CRUD
- 业务逻辑差异较大的模块
- 不需要维护一致性的独立模块

## 模式架构

### 三层结构

```
Abstract Layer (抽象层)
├── Controllers/
│   ├── A{Module}Cate.class.php      (分类控制器抽象基类)
│   ├── A{Module}Content.class.php   (内容控制器抽象基类)
│   └── A{Module}Tag.class.php       (标签控制器抽象基类)
│
└── Models/
    ├── A{Module}CateModel.class.php    (分类模型抽象基类)
    ├── A{Module}ContentModel.class.php (内容模型抽象基类)
    └── A{Module}TagModel.class.php     (标签模型抽象基类)

Concrete Layer (实现层)
├── XxxCateController    extends A{Module}Cate
├── XxxContentController extends A{Module}Content
├── XxxTagController     extends A{Module}Tag
│
└── XxxCateModel    extends A{Module}CateModel
    XxxContentModel extends A{Module}ContentModel
    XxxTagModel     extends A{Module}TagModel
```

## 分类模块模式 (ACate/ACateModel)

### 适用场景

- 树形分类结构
- 需要管理名称、排序、状态
- 可选：展示类型 (show_type)、详情内容 (content)

### 控制器抽象基类结构

```php
abstract class A{Module}Cate extends QsListController
{
    // 配置属性（子类实现）
    abstract protected function getModelName(): string;
    abstract protected function getMetaTitle(): string;
    abstract protected function getLogPrefix(): string;

    // 可配置属性
    protected $formWidth = '800px';

    // 私有方法（内部使用）
    private function _filter(array $get_data, array &$map): void;

    // 公共方法（业务流程）
    public function index();      // 列表页
    public function add();        // 新增
    public function edit($id);    // 编辑
    public function forbid();     // 禁用
    public function resume();     // 启用
    public function delete();     // 删除
    public function save();       // 批量保存排序

    // 可重写方法（子类扩展）
    protected function buildColumns(Table\ColumnsContainer $container);
    protected function addBuilderFormItem(Form &$form);
}
```

### 关键方法说明

| 方法 | 用途 | 子类是否重写 |
|------|------|-------------|
| `getModelName()` | 返回模型名称 | ✅ 必须实现 |
| `getMetaTitle()` | 返回页面标题 | ✅ 必须实现 |
| `getLogPrefix()` | 返回日志前缀 | ✅ 必须实现 |
| `buildColumns()` | 构建表格列 | ⚠️ 可选重写 |
| `addBuilderFormItem()` | 构建表单字段 | ⚠️ 可选重写 |
| `index()` | 列表页逻辑 | ❌ 一般不重写 |
| `add()` | 新增逻辑 | ❌ 一般不重写 |
| `edit()` | 编辑逻辑 | ❌ 一般不重写 |

### 模型抽象基类结构

```php
abstract class A{Module}CateModel extends GyListModel
{
    // 配置属性（子类实现）
    abstract protected function getContentModelName(): string;

    // 验证规则（可重写）
    protected $_validate = [/* ... */];

    // 自动完成（可重写）
    protected $_auto = [/* ... */];

    // 删除验证（子类添加）
    protected $_delete_validate = [/* ... */];

    // 公共方法（查询方法）
    public function parseCatetMap(array $get_data, array &$map): void;
    public function getCateCount(array $map): int;
    public function getCateList(array $map, ?int $page, ?int $per_page): array;
}
```

### 关键方法说明

| 方法 | 用途 | 子类是否重写 |
|------|------|-------------|
| `getContentModelName()` | 返回关联的内容模型名称 | ✅ 必须实现 |
| `parseCatetMap()` | 解析查询条件 | ⚠️ 可选重写 |
| `getCateCount()` | 获取分类数量 | ⚠️ 可选重写 |
| `getCateList()` | 获取分类列表 | ⚠️ 可选重写 |
| `$_delete_validate` | 删除时验证关联 | ⚠️ 子类添加 |

### 具体实现示例

**控制器**:
```php
class XxxCateController extends A{Module}Cate
{
    protected function getModelName() { return 'XxxCate'; }
    protected function getMetaTitle() { return '分类管理'; }
    protected function getLogPrefix() { return 'XXX分类'; }
}
```

**模型**:
```php
class XxxCateModel extends A{Module}CateModel
{
    protected function getContentModelName()
    {
        return 'XxxContent';
    }

    protected $_delete_validate = [
        ['XxxContent', 'cate_id', parent::EXIST_VALIDATE, '该分类已有关联内容'],
    ];
}
```

## 内容模块模式 (AContent/AContentModel)

### 适用场景

- 带分类的内容管理
- 需要标签关联
- 复杂表单依赖（根据分类类型动态显示字段）
- 可选扩展：知识库同步、AI 标签生成等

### 控制器抽象基类结构

```php
abstract class A{Module}Content extends QsListController
{
    // 配置属性（子类实现）
    abstract protected function getModelName(): string;
    abstract protected function getCateModelName(): string;
    abstract protected function getTagModelName(): string;
    abstract protected function getMetaTitle(): string;
    abstract protected function getLogPrefix(): string;

    // 可配置属性
    protected $formWidth = '800px';

    // 可选 Trait（根据需要引入）
    // use KnowledgeStoreTrait;
    // use AiTagTrait;

    // 公共方法（业务流程）
    public function index();      // 列表页（含关联数据）
    public function add();        // 新增
    public function edit($id);    // 编辑
    public function forbid();     // 禁用
    public function resume();     // 启用
    public function delete();     // 删除
    public function save();       // 批量保存排序

    // 可重写方法（子类扩展）
    protected function buildColumns(Table\ColumnsContainer $container);
    protected function addBuilderFormItem(Form &$form, array $data = []);
}
```

### 关键方法说明

| 方法 | 用途 | 子类是否重写 |
|------|------|-------------|
| `getModelName()` | 返回自身模型名称 | ✅ 必须实现 |
| `getCateModelName()` | 返回分类模型名称 | ✅ 必须实现 |
| `getTagModelName()` | 返回标签模型名称 | ✅ 必须实现 |
| `getMetaTitle()` | 返回页面标题 | ✅ 必须实现 |
| `getLogPrefix()` | 返回日志前缀 | ✅ 必须实现 |
| `buildColumns()` | 构建表格列 | ⚠️ 可选重写 |
| `addBuilderFormItem()` | 构建表单字段 | ⚠️ 可选重写 |

### 模型抽象基类结构

```php
abstract class A{Module}ContentModel extends GyListModel
{
    // 配置属性（子类实现）
    abstract protected function getCateModelName(): string;
    abstract protected function getTagModelName(): string;

    // 验证规则（可重写）
    protected $_validate = [/* ... */];

    // 自动完成（可重写）
    protected $_auto = [/* ... */];

    // 公共方法（业务逻辑）
    public function parseContentMap(array $get_data, array &$map, array &$bind): void;
    public function getContentCount(array $map, array $bind): int;
    public function getContentList(array $map, array $bind, ?int $page, ?int $per_page): array;
    public function addContent(array $data): int;
    public function editContent(array $data): bool;
    public function formatListToFront(array &$list): void;
}
```

### 具体实现示例

**控制器**:
```php
class XxxContentController extends A{Module}Content
{
    protected function getModelName() { return 'XxxContent'; }
    protected function getCateModelName() { return 'XxxCate'; }
    protected function getTagModelName() { return 'XxxTag'; }
    protected function getMetaTitle() { return '内容管理'; }
    protected function getLogPrefix() { return 'XXX内容'; }
}
```

**模型**:
```php
class XxxContentModel extends A{Module}ContentModel
{
    protected function getCateModelName() { return 'XxxCate'; }
    protected function getTagModelName() { return 'XxxTag'; }

    // 可选：添加自定义验证
    protected $_validate = [
        // 父类验证 + 自定义验证
    ];

    // 可选：添加自定义业务逻辑
    public function addContent(array $data): int
    {
        // 自定义前置处理
        $data = $this->processCustomLogic($data);

        // 调用父类方法
        return parent::addContent($data);
    }
}
```

## 标签模块模式 (ATag/ATagModel)

### 适用场景

- 简单标签管理
- 名称、描述、排序、状态
- 与内容多对多关联

### 控制器抽象基类结构

```php
abstract class A{Module}Tag extends QsListController
{
    // 配置属性（子类实现）
    abstract protected function getModelName(): string;
    abstract protected function getMetaTitle(): string;
    abstract protected function getLogPrefix(): string;

    // 可配置属性
    protected $formWidth = '500px';

    // 公共方法（业务流程）
    public function index();      // 列表页
    public function add();        // 新增
    public function edit($id);    // 编辑
    public function forbid();     // 禁用
    public function resume();     // 启用
    public function delete();     // 删除
    public function save();       // 批量保存排序

    // 可重写方法（子类扩展）
    protected function buildColumns(Table\ColumnsContainer $container);
    protected function addBuilderFormItem(Form &$form);
}
```

### 模型抽象基类结构

```php
abstract class A{Module}TagModel extends GyListModel
{
    // 配置属性（子类实现）
    abstract protected function getContentModelName(): string;

    // 验证规则（可重写）
    protected $_validate = [/* ... */];

    // 删除验证（子类添加）
    protected $_delete_validate = [/* ... */];

    // 公共方法（查询方法）
    public function parseTagMap(array $get_data, array &$map): void;
    public function getTagCount(array $map): int;
    public function getTagList(array $map, ?int $page, ?int $per_page): array;
    public function getTagListByCateIds(array $id_with_tag): array;
}
```

### 具体实现示例

**控制器**:
```php
class XxxTagController extends A{Module}Tag
{
    protected function getModelName() { return 'XxxTag'; }
    protected function getMetaTitle() { return '标签管理'; }
    protected function getLogPrefix() { return 'XXX标签'; }
}
```

**模型**:
```php
class XxxTagModel extends A{Module}TagModel
{
    protected function getContentModelName() { return 'XxxContent'; }

    protected $_delete_validate = [
        ['XxxContent', 'tag_id', parent::EXIST_VALIDATE, '该标签已关联内容'],
    ];
}
```

## 创建新模块的步骤

### 1. 创建抽象基类（如果不存在）

在 `app/Admin/Controller/Module/` 和 `app/Common/Model/Module/` 目录下创建抽象基类。

### 2. 创建数据库迁移

```bash
php artisan make:migration create_xxx_cate_table
php artisan make:migration create_xxx_content_table
php artisan make:migration create_xxx_tag_table
```

参考 [Migration Metadata](migration-metadata.md) 添加元数据注释。

### 3. 创建模型

```php
// app/Common/Model/XxxCateModel.class.php
class XxxCateModel extends AModuleCateModel
{
    protected function getContentModelName() { return 'XxxContent'; }
}

// app/Common/Model/XxxContentModel.class.php
class XxxContentModel extends AModuleContentModel
{
    protected function getCateModelName() { return 'XxxCate'; }
    protected function getTagModelName() { return 'XxxTag'; }
}

// app/Common/Model/XxxTagModel.class.php
class XxxTagModel extends AModuleTagModel
{
    protected function getContentModelName() { return 'XxxContent'; }
}
```

### 4. 创建控制器

```php
// app/Admin/Controller/XxxCateController.class.php
class XxxCateController extends AModuleCate
{
    protected function getModelName() { return 'XxxCate'; }
    protected function getMetaTitle() { return '栏目管理'; }
    protected function getLogPrefix() { return 'XXX栏目'; }
}

// app/Admin/Controller/XxxContentController.class.php
class XxxContentController extends AModuleContent
{
    protected function getModelName() { return 'XxxContent'; }
    protected function getCateModelName() { return 'XxxCate'; }
    protected function getTagModelName() { return 'XxxTag'; }
    protected function getMetaTitle() { return '内容管理'; }
    protected function getLogPrefix() { return 'XXX内容'; }
}

// app/Admin/Controller/XxxTagController.class.php
class XxxTagController extends AModuleTag
{
    protected function getModelName() { return 'XxxTag'; }
    protected function getMetaTitle() { return '标签管理'; }
    protected function getLogPrefix() { return 'XXX标签'; }
}
```

### 5. 运行迁移并配置权限

```bash
# 运行迁移
php artisan migrate

# 在 qs_node 表中添加菜单项和权限配置
```

## 自定义扩展策略

### 重写表单字段

```php
class XxxContentController extends AModuleContent
{
    protected function addBuilderFormItem(Form &$form, array $data = [])
    {
        // 调用父类方法（可选）
        parent::addBuilderFormItem($form, $data);

        // 添加自定义字段
        $form->columns(function (Form\ColumnsContainer $columns) {
            $columns->text('custom_field', '自定义字段')
                ->setFormItemWidth(24);
        });
    }
}
```

### 重写表格列

```php
class XxxContentController extends AModuleContent
{
    protected function buildColumns(Table\ColumnsContainer $container)
    {
        // 调用父类方法（可选）
        parent::buildColumns($container);

        // 添加自定义列
        $container->text('custom_field', '自定义字段')->setSearch(false);
    }
}
```

### 添加自定义业务逻辑

```php
class XxxContentModel extends AModuleContentModel
{
    public function addContent(array $data): int
    {
        $this->startTrans();

        try {
            // 自定义前置处理
            $data = $this->processCustomLogic($data);

            // 调用父类方法
            $content_id = parent::addContent($data);

            // 自定义后置处理
            $this->syncToExternalSystem($content_id);

            $this->commit();
            return $content_id;

        } catch (\Exception $e) {
            $this->rollback();
            $this->error = $e->getMessage();
            return false;
        }
    }

    private function processCustomLogic(array $data): array
    {
        // 自定义逻辑
        return $data;
    }
}
```

### 添加新的抽象方法

```php
abstract class AModuleContent extends QsListController
{
    // 新增抽象方法（子类必须实现）
    abstract protected function getCustomConfig(): array;

    public function index()
    {
        $config = $this->getCustomConfig();
        // 使用配置
    }
}
```

## 最佳实践

1. **保持抽象基类的稳定性**：抽象基类一旦创建，尽量保持接口稳定
2. **最小化子类实现**：子类只需实现必要的抽象方法
3. **合理使用 protected 方法**：提供可重写的钩子方法
4. **文档化扩展点**：明确哪些方法可以安全重写
5. **避免过度抽象**：只有真正的共性才需要抽象

---

**相关文档**：
- [Admin Controllers](admin-controllers.md) - 标准 CRUD 模式
- [Migration Metadata](migration-metadata.md) - 迁移文件元数据系统
- [Migration Guide](migration-guide.md) - 数据库迁移指南
- [Model Guide](model-guide.md) - 模型开发指南

---

**相关文档**：
- [Admin Controllers](admin-controllers.md)
- [Migration Metadata](migration-metadata.md)
- [Model Guide](model-guide.md)

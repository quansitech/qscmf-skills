# Abstract Base Patterns Reference

> QSCMF v13 抽象基类模式 - 多相似模块的代码复用方案

## 版本特性

| 特性 | v13 |
|------|-----|
| PHP 版本 | >= 8.1 |
| 列表构建器 | ListBuilder |
| 表单构建器 | FormBuilder |

## 概述

当项目中有多个相似的模块时，使用抽象基类模式可以：

- 避免重复代码
- 统一业务逻辑
- 简化新模块开发
- 便于维护和升级

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
    protected string $formWidth = '800px';

    // 公共方法（业务流程）
    public function index(): void      // 列表页
    public function add(): void        // 新增
    public function edit(int $id): void    // 编辑
    public function forbid(): void     // 禁用
    public function resume(): void     // 启用
    public function delete(): void     // 删除
    public function save(): void       // 批量保存排序

    // 可重写方法（子类扩展）
    protected function buildColumns(ListBuilder $builder): void;
    protected function buildFormItems(FormBuilder $builder): void;
}
```

### 模型抽象基类结构

```php
abstract class A{Module}CateModel extends GyListModel
{
    // 配置属性（子类实现）
    abstract protected function getContentModelName(): string;

    // 验证规则（可重写）
    protected array $_validate = [
        ['name', 'require', '名称不能为空', self::MUST_VALIDATE],
        ['name', '1,100', '名称长度1-100', self::EXISTS_VALIDATE, 'length'],
    ];

    // 删除验证（子类添加）
    protected array $_delete_validate = [];

    // 公共方法（查询方法）
    public function parseCateMap(array $get_data, array &$map): void;
    public function getCateCount(array $map): int;
    public function getCateList(array $map, ?int $page, ?int $per_page): array;
}
```

### 具体实现示例

**控制器**:
```php
class XxxCateController extends A{Module}Cate
{
    protected function getModelName(): string { return 'XxxCate'; }
    protected function getMetaTitle(): string { return '分类管理'; }
    protected function getLogPrefix(): string { return 'XXX分类'; }
}
```

**模型**:
```php
class XxxCateModel extends A{Module}CateModel
{
    protected function getContentModelName(): string
    {
        return 'XxxContent';
    }

    protected array $_delete_validate = [
        ['XxxContent', 'cate_id', parent::EXIST_VALIDATE, '该分类已有关联内容'],
    ];
}
```

## 内容模块模式 (AContent/AContentModel)

### 适用场景

- 带分类的内容管理
- 需要标签关联
- 复杂表单依赖（根据分类类型动态显示字段）

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
    protected string $formWidth = '800px';

    // 公共方法（业务流程）
    public function index(): void      // 列表页（含关联数据）
    public function add(): void        // 新增
    public function edit(int $id): void    // 编辑
    public function forbid(): void     // 禁用
    public function resume(): void     // 启用
    public function delete(): void     // 删除
    public function save(): void       // 批量保存排序

    // 可重写方法（子类扩展）
    protected function buildColumns(ListBuilder $builder): void;
    protected function buildFormItems(FormBuilder $builder, array $data = []): void;
}
```

### 具体实现示例

**控制器**:
```php
class XxxContentController extends A{Module}Content
{
    protected function getModelName(): string { return 'XxxContent'; }
    protected function getCateModelName(): string { return 'XxxCate'; }
    protected function getTagModelName(): string { return 'XxxTag'; }
    protected function getMetaTitle(): string { return '内容管理'; }
    protected function getLogPrefix(): string { return 'XXX内容'; }
}
```

**模型**:
```php
class XxxContentModel extends A{Module}ContentModel
{
    protected function getCateModelName(): string { return 'XxxCate'; }
    protected function getTagModelName(): string { return 'XxxTag'; }

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
    protected string $formWidth = '500px';

    // 公共方法（业务流程）
    public function index(): void      // 列表页
    public function add(): void        // 新增
    public function edit(int $id): void    // 编辑
    public function forbid(): void     // 禁用
    public function resume(): void     // 启用
    public function delete(): void     // 删除
    public function save(): void       // 批量保存排序

    // 可重写方法（子类扩展）
    protected function buildColumns(ListBuilder $builder): void;
    protected function buildFormItems(FormBuilder $builder): void;
}
```

### 具体实现示例

**控制器**:
```php
class XxxTagController extends A{Module}Tag
{
    protected function getModelName(): string { return 'XxxTag'; }
    protected function getMetaTitle(): string { return '标签管理'; }
    protected function getLogPrefix(): string { return 'XXX标签'; }
}
```

**模型**:
```php
class XxxTagModel extends A{Module}TagModel
{
    protected function getContentModelName(): string { return 'XxxContent'; }

    protected array $_delete_validate = [
        ['XxxContent', 'tag_id', parent::EXIST_VALIDATE, '该标签已关联内容'],
    ];
}
```

## 创建新模块的步骤

### 1. 创建数据库迁移

```bash
php artisan make:migration create_xxx_cate_table
php artisan make:migration create_xxx_content_table
php artisan make:migration create_xxx_tag_table
```

参考 [Migration Metadata](migration-metadata.md) 添加元数据注释。

### 2. 创建模型

```php
// app/Common/Model/XxxCateModel.class.php
class XxxCateModel extends AModuleCateModel
{
    protected function getContentModelName(): string { return 'XxxContent'; }
}

// app/Common/Model/XxxContentModel.class.php
class XxxContentModel extends AModuleContentModel
{
    protected function getCateModelName(): string { return 'XxxCate'; }
    protected function getTagModelName(): string { return 'XxxTag'; }
}

// app/Common/Model/XxxTagModel.class.php
class XxxTagModel extends AModuleTagModel
{
    protected function getContentModelName(): string { return 'XxxContent'; }
}
```

### 3. 创建控制器

```php
// app/Admin/Controller/XxxCateController.class.php
class XxxCateController extends AModuleCate
{
    protected function getModelName(): string { return 'XxxCate'; }
    protected function getMetaTitle(): string { return '栏目管理'; }
    protected function getLogPrefix(): string { return 'XXX栏目'; }
}

// app/Admin/Controller/XxxContentController.class.php
class XxxContentController extends AModuleContent
{
    protected function getModelName(): string { return 'XxxContent'; }
    protected function getCateModelName(): string { return 'XxxCate'; }
    protected function getTagModelName(): string { return 'XxxTag'; }
    protected function getMetaTitle(): string { return '内容管理'; }
    protected function getLogPrefix(): string { return 'XXX内容'; }
}

// app/Admin/Controller/XxxTagController.class.php
class XxxTagController extends AModuleTag
{
    protected function getModelName(): string { return 'XxxTag'; }
    protected function getMetaTitle(): string { return '标签管理'; }
    protected function getLogPrefix(): string { return 'XXX标签'; }
}
```

### 4. 运行迁移并配置权限

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
    protected function buildFormItems(FormBuilder $builder, array $data = []): void
    {
        // 调用父类方法（可选）
        parent::buildFormItems($builder, $data);

        // 添加自定义字段
        $builder->addFormItem('custom_field', 'text', '自定义字段', '', '', '', 'required');
    }
}
```

### 重写表格列

```php
class XxxContentController extends AModuleContent
{
    protected function buildColumns(ListBuilder $builder): void
    {
        // 调用父类方法（可选）
        parent::buildColumns($builder);

        // 添加自定义列
        $builder->addTableColumn('custom_field', '自定义字段');
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
            return 0;
        }
    }

    private function processCustomLogic(array $data): array
    {
        // 自定义逻辑
        return $data;
    }
}
```

## 最佳实践

1. **保持抽象基类的稳定性**：抽象基类一旦创建，尽量保持接口稳定
2. **最小化子类实现**：子类只需实现必要的抽象方法
3. **合理使用 protected 方法**：提供可重写的钩子方法
4. **文档化扩展点**：明确哪些方法可以安全重写
5. **避免过度抽象**：只有真正的共性才需要抽象

## 相关文档

- [Admin Controllers](admin-controllers.md) - 标准 CRUD 模式
- [Migration Metadata](migration-metadata.md) - 迁移文件元数据系统
- [Migration Guide](migration-guide.md) - 数据库迁移指南
- [Model Guide](model-guide.md) - 模型开发指南

# 渲染模式配置 (v14)

> **重要**: v14 新项目 **必须** 使用 React Mode

## 铁律

```
NEW V14 PROJECTS = REACT MODE ONLY
```

v14 项目强制使用 React + Ant Design 渲染，jQuery Mode 仅用于 v13 迁移过渡期。

---

## 配置

### 强制配置 (新项目)

```php
// app/Common/Conf/config.php
'ANTD_ADMIN_BUILDER_ENABLE' => true,  // 必须为 true
```

### 环境变量

```bash
# .env
INERTIA_SSR_URL=http://localhost:13714
```

---

## React Mode (v14 标准)

### API 风格

使用 `AntdAdmin\Component` API：

```php
use AntdAdmin\Component\Table;
use AntdAdmin\Component\Form;
use AntdAdmin\Component\Table\Pagination;

// Table
$table = new Table();
$table->setMetaTitle('商品列表')
    ->columns(function ($container) {
        $container->text('id', 'ID');
        $container->text('name', '名称');
    })
    ->setDataSource($list)
    ->setPagination(new Pagination($page, $limit, $total))
    ->render();

// Form
$form = new Form();
$form->setSubmitRequest('post', U('add'))
    ->columns(function ($columns) {
        $columns->text('name', '名称')->addRule(new Required());
    });
```

### 前端构建

```bash
# 开发
npm run dev:backend

# 生产
npm run build:backend
```

---

## jQuery Mode (仅迁移用)

> **警告**: jQuery Mode 仅用于 v13 项目迁移过渡，新项目禁止使用

### 适用场景 (有限)

- v13 项目逐步迁移
- 需要 IE11 兼容 (不推荐)

### API 风格 (兼容层)

```php
// ListBuilder API 在 React Mode 下仍然兼容
$builder = $this->builder();
$builder->setMetaTitle('商品列表')
    ->addTableColumn('id', 'ID')
    ->addTopButton('addnew')
    ->setData($list)
    ->display();
```

### 迁移路径

```
v13 项目 → jQuery Mode (过渡) → React Mode (目标)
```

---

## API 兼容性

| ListBuilder API | React Mode |
|-----------------|------------|
| `addTableColumn()` | ✅ |
| `addTopButton()` | ✅ |
| `addRightButton()` | ✅ |
| `addSearchItem()` | ✅ |
| `setTableDataList()` | ✅ |

> ListBuilder API 在 React Mode 下可正常运行，但新代码应使用 AntdAdmin Component API

---

## 新项目检查清单

- [ ] `ANTD_ADMIN_BUILDER_ENABLE = true`
- [ ] 使用 `AntdAdmin\Component\Table` 和 `Form`
- [ ] 前端资源已构建 (`npm run build:backend`)
- [ ] SSR 服务已配置 (生产环境)

---

## 相关文档

- [AntdAdmin Components](../rules/antdadmin.md)
- [HasLayoutProps Trait](has-layout-props.md)
- [Inertia.js Integration](../rules/inertia.md)

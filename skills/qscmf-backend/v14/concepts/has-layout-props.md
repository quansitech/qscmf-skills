# HasLayoutProps Trait

> v14 布局属性管理机制

## 概述

`HasLayoutProps` 是 v14 版本中用于管理 AntdAdmin 布局属性的 Trait。它提供了统一的方式来配置和管理后台管理界面的布局属性。

## 位置

```php
// 在 QsController 中使用
use Qscmf\Core\Traits\HasLayoutProps;
```

## 核心功能

### 1. 布局属性管理

```php
trait HasLayoutProps
{
    /**
     * 布局属性数组
     */
    protected array $layoutProps = [];

    /**
     * 设置布局属性
     */
    protected function setLayoutProp(string $key, mixed $value): void
    {
        $this->layoutProps[$key] = $value;
    }

    /**
     * 获取布局属性
     */
    protected function getLayoutProps(): array
    {
        return $this->layoutProps;
    }

    /**
     * 处理布局属性（v14 专用）
     */
    protected function handleLayoutProps(): void
    {
        // 仅在 ANTD_ADMIN_BUILDER_ENABLE = true 时执行
        if (!C('ANTD_ADMIN_BUILDER_ENABLE')) {
            return;
        }

        // 设置默认布局属性
        $this->setLayoutProp('metaTitle', $this->metaTitle ?? '');
        // ... 其他布局属性
    }
}
```

## 使用场景

### 在 QsController 中的应用

```php
// vendor/tiderjian/think-core/src/Library/Qscmf/Core/QsController.class.php

class QsController extends Think\Controller
{
    use HasLayoutProps;

    protected function _initialize()
    {
        // ... 其他初始化逻辑

        // v14 布局处理
        if (C('ANTD_ADMIN_BUILDER_ENABLE')) {
            $this->handleLayoutProps();
        }
    }
}
```

### 在控制器中自定义布局属性

```php
class ProductController extends GyListController
{
    public function index()
    {
        // 自定义布局属性
        $this->setLayoutProp('metaTitle', '商品管理');
        $this->setLayoutProp('breadcrumbs', [
            ['title' => '首页', 'href' => '/admin'],
            ['title' => '商品管理'],
        ]);

        // ... CRUD 逻辑
    }
}
```

## 常用布局属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `metaTitle` | string | 页面标题 |
| `breadcrumbs` | array | 面包屑导航 |
| `sidebar` | array | 侧边栏配置 |
| `header` | array | 顶部导航配置 |
| `footer` | array | 底部信息 |

## 与 Inertia.js 的集成

布局属性会自动传递给 Inertia.js 的页面组件：

```php
// 控制器中设置
$this->setLayoutProp('metaTitle', '商品列表');

// 自动传递给 React 组件
// resources/js/frontend/Pages/Admin/Product/Index.tsx
// 可通过 page.props.metaTitle 访问
```

## 注意事项

1. **仅在 v14 模式下生效**: 需要 `ANTD_ADMIN_BUILDER_ENABLE = true`
2. **继承自 QsController**: 所有继承 QsController 的控制器自动拥有此 Trait
3. **优先级**: 子控制器设置的属性会覆盖默认值

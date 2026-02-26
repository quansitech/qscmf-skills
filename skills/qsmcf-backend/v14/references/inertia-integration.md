# Inertia Integration

Inertia.js integration guide for QSCMF v14.

## Overview

Inertia.js enables SPA-like navigation without building a separate API.

## HasLayoutProps Trait

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
            ],
        ]);
    }
}
```

## Detect Inertia Request

```php
protected function isInertiaRequest(): bool
{
    return !empty($_SERVER['HTTP_X_INERTIA']);
}
```

## Render Inertia Page

```php
if ($this->isInertiaRequest()) {
    return Inertia::render('Product/Index', [
        'products' => $products,
    ]);
}
```

---

## Related Documentation
- [Inertia Rules](../rules/inertia.md)
- [AntdAdmin Components](../rules/antdadmin.md)

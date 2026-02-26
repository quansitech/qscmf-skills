# Inertia.js Integration (v14)

Guide for using Inertia.js in QSCMF v14 for SPA-like navigation.

## Overview

Inertia.js enables SPA-like navigation without building a separate API. It works by:
1. Server returns page props as JSON when `X-Inertia` header is present
2. Client-side React updates without full page reload

## HasLayoutProps Trait

The `HasLayoutProps` trait provides layout data sharing:

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

### Available Methods

| Method | Description |
|--------|-------------|
| `shareLayoutProps($props)` | Share props with layout |
| `getSharedProps()` | Get all shared props |
| `clearSharedProps()` | Clear shared props |

## X-Inertia Header Detection

Detect Inertia requests to return JSON props:

```php
public function detail()
{
    $data = D('Product')->find(I('get.id'));

    if ($this->isInertiaRequest()) {
        return Inertia::render('Product/Detail', [
            'product' => $data,
            'related' => $this->getRelatedData($data['id']),
        ]);
    }

    // Traditional page render for non-Inertia requests
    $this->assign('data', $data);
    $this->display();
}

protected function isInertiaRequest(): bool
{
    return !empty($_SERVER['HTTP_X_INERTIA']);
}
```

## Inertia Response

```php
use Inertia\Inertia;

// Render Inertia page
return Inertia::render('Product/Index', [
    'products' => $products,
    'filters' => $filters,
    'pagination' => [
        'total' => $total,
        'page' => $page,
        'perPage' => $perPage,
    ],
]);

// Redirect with Inertia
return Inertia::redirect('/products');

// Back redirect
return Inertia::back();

// Share data with all pages
Inertia::share('auth', [
    'user' => $this->user,
    'permissions' => $this->permissions,
]);
```

## React Page Component

Create corresponding React component:

```tsx
// resources/js/Pages/Product/Index.tsx
import { Head, Link } from '@inertiajs/react';
import { Table, Button } from 'antd';

interface Product {
    id: number;
    product_name: string;
    status: number;
}

interface Props {
    products: Product[];
    pagination: {
        total: number;
        page: number;
        perPage: number;
    };
}

export default function ProductIndex({ products, pagination }: Props) {
    const columns = [
        { title: 'ID', dataIndex: 'id' },
        { title: '名称', dataIndex: 'product_name' },
        { title: '状态', dataIndex: 'status' },
    ];

    return (
        <>
            <Head title="商品列表" />
            <div className="page-header">
                <h1>商品列表</h1>
                <Link href="/admin/product/add">
                    <Button type="primary">新增</Button>
                </Link>
            </div>
            <Table
                columns={columns}
                dataSource={products}
                pagination={{
                    total: pagination.total,
                    current: pagination.page,
                    pageSize: pagination.perPage,
                }}
                rowKey="id"
            />
        </>
    );
}
```

## Partial Reloads

Reload only specific props:

```php
// Controller
return Inertia::render('Product/Index', [
    'products' => fn () => D('Product')->getList(),
    'categories' => fn () => D('Category')->getAll(), // Only loaded when needed
]);
```

```tsx
// Client-side partial reload
import { router } from '@inertiajs/react';

router.reload({ only: ['products'] });
```

## Form Handling

```php
// Controller
public function store()
{
    $data = I('post.');

    $validator = $this->validate($data);
    if ($validator->fails()) {
        return Inertia::back()
            ->withErrors($validator->errors())
            ->withInput();
    }

    D('Product')->add($data);

    return Inertia::redirect('/admin/product')
        ->with('success', 'Product created successfully');
}
```

```tsx
// React form component
import { useForm } from '@inertiajs/react';

export default function ProductForm() {
    const { data, setData, post, processing, errors } = useForm({
        product_name: '',
        status: 1,
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        post('/admin/product');
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                value={data.product_name}
                onChange={e => setData('product_name', e.target.value)}
            />
            {errors.product_name && <span>{errors.product_name}</span>}
            <button type="submit" disabled={processing}>Submit</button>
        </form>
    );
}
```

## History Preservation

```php
// Preserve URL state
return Inertia::render('Product/Index', $props)
    ->preserveUrl();
```

## Best Practices

1. **Use lazy evaluation** for optional props
2. **Share common data** via middleware
3. **Validate early** to avoid unnecessary rendering
4. **Use partial reloads** for better performance
5. **Handle loading states** in React components

## Related Documentation

- [AntdAdmin Components](antdadmin.md) - React component API
- [API Controllers](../references/api-controllers.md) - RESTful API

# QSCMF Version History

This document describes the evolution of the QSCMF framework from v13 to v14.

## Version Timeline

| Version | Release | PHP | PHPUnit | Status |
|---------|---------|-----|---------|--------|
| v13 | 2023 | 8.2 | ^9.3.0 | Stable (maintenance) |
| v14 | 2024 | 8.2+ | ^10.0 | Current (active development) |

---

## v13 (Legacy)

### Overview

v13 is the stable legacy version of QSCMF, using traditional jQuery and Bootstrap for admin interfaces.

### Key Characteristics

- **PHP Version**: 8.2
- **Testing Framework**: PHPUnit 9.3.0+
- **UI Framework**: jQuery + Bootstrap
- **Template Engine**: ThinkPHP templates
- **Primary API**: `\Qscmf\Builder\ListBuilder`

### UI Architecture

```
Controller (PHP)
    |
    v
ListBuilder (PHP)
    |
    v
HTML + jQuery Events
    |
    v
Bootstrap CSS Styling
```

### Data Flow

1. Controller calls `ListBuilder->build()`
2. ListBuilder generates HTML with embedded jQuery
3. Browser renders HTML with Bootstrap styles
4. jQuery handles client-side interactions
5. Form submissions trigger page reload

### Limitations

- Page reloads on every action
- Limited real-time updates
- jQuery dependency for all interactions
- Template-based rendering
- No modern SPA features

### When to Use v13

- Existing projects that don't need SPA features
- Teams familiar with jQuery/Bootstrap
- Projects requiring maximum stability
- Simple admin interfaces without complex interactions

---

## v14 (Modern)

### Overview

v14 is the modern version of QSCMF, featuring React-based admin interfaces with Inertia.js and Ant Design.

### Key Characteristics

- **PHP Version**: 8.2+
- **Testing Framework**: PHPUnit 10.0+
- **UI Framework**: React + Ant Design (AntdAdmin)
- **Frontend Bridge**: Inertia.js
- **Primary API**: `\AntdAdmin\Component\Table`
- **Legacy API**: `\Qscmf\Builder\ListBuilder` (backward compatible)

### UI Architecture

```
Controller (PHP)
    |
    v
AntdAdmin\Component\Table (PHP)
    |
    v
Inertia.js Response (JSON)
    |
    v
React Components
    |
    v
Ant Design Styling
```

### Data Flow

1. Controller calls `Table->render()`
2. Table returns Inertia.js response (JSON props)
3. React components render with Ant Design
4. Client-side interactions without page reload
5. AJAX requests for data updates
6. Real-time UI updates

### New Features

#### Inertia.js Integration

```php
// v14 returns Inertia responses
class ProductController extends QsListController {
    public function index() {
        $table = new \AntdAdmin\Component\Table();
        // ... configuration
        return $table->render();  // Returns X-Inertia response
    }
}
```

#### HasLayoutProps Trait

v14 introduces `HasLayoutProps` trait for sharing layout data:

```php
use HasLayoutProps;

class ProductController extends QsListController {
    use HasLayoutProps;

    public function index() {
        $this->shareLayoutProps([
            'title' => 'Products',
            'breadcrumb' => [...]
        ]);
        // ...
    }
}
```

#### X-Inertia Headers

v14 responses include Inertia headers:

```
X-Inertia: true
X-Inertia-Version: abc123
```

### Backward Compatibility

v14 maintains backward compatibility with ListBuilder API:

```php
// v14 can still use ListBuilder (jQuery mode)
// Set ANTD_ADMIN_BUILDER_ENABLE = false in config
$builder = new \Qscmf\Builder\ListBuilder();
$builder->addTableColumn('name', 'Name')
    // ...
    ->build();  // Renders jQuery/Bootstrap UI
```

### When to Use v14

- New projects
- Projects requiring SPA features
- Teams wanting modern React interfaces
- Applications with complex admin interactions
- Projects needing real-time updates

---

## Migration Path: v13 to v14

### Phase 1: Preparation

1. **Upgrade PHP**: Ensure PHP 8.2+ is available
2. **Upgrade PHPUnit**: Update to PHPUnit 10
3. **Update Dependencies**: Run `composer update`
4. **Run Tests**: Ensure all tests pass

### Phase 2: Gradual Migration

1. **Enable v14 Mode**: Set `ANTD_ADMIN_BUILDER_ENABLE = true`
2. **Migrate One Controller**: Start with a simple controller
3. **Test Thoroughly**: Verify functionality
4. **Repeat**: Migrate remaining controllers

### Phase 3: API Migration

Convert ListBuilder API to AntdAdmin Component API:

| From (v13) | To (v14) |
|------------|----------|
| `new ListBuilder()` | `new \AntdAdmin\Component\Table()` |
| `->addTableColumn('name', 'Name')` | `$container->text('name', 'Name')` |
| `->addTopButton('addnew', [...])` | `$container->button('Add')->modal(...)` |
| `->addRightButton('edit')` | `$container->action('')->edit()` |
| `->build()` | `->render()` |

### Breaking Changes

| Change | Impact | Migration |
|--------|--------|-----------|
| PHPUnit 10 | Test syntax changes | Update test assertions |
| React rendering | jQuery events removed | Use React event handlers |
| Inertia responses | Response format changed | Update client handling |

### Compatibility Layer

The `ANTD_ADMIN_BUILDER_ENABLE` flag allows gradual migration:

```php
// In config.php
'ANTD_ADMIN_BUILDER_ENABLE' => env('ANTD_ADMIN_ENABLE', true),

// Per-controller override
class LegacyController extends QsListController {
    protected $antdAdminEnable = false;  // Use jQuery for this controller
}
```

---

## Version Comparison Summary

| Feature | v13 | v14 |
|---------|-----|-----|
| **PHP Version** | 8.2 | 8.2+ |
| **PHPUnit** | ^9.3.0 | ^10.0 |
| **Primary UI API** | ListBuilder | AntdAdmin Component |
| **Rendering** | jQuery + Bootstrap | React + Ant Design |
| **Page Navigation** | Full reload | SPA (no reload) |
| **Inertia.js** | No | Yes |
| **HasLayoutProps** | No | Yes |
| **X-Inertia Headers** | No | Yes |
| **Real-time Updates** | Limited | Full support |
| **Backward Compat** | N/A | ListBuilder supported |

---

## Future Roadmap

### v14.x

- Enhanced Inertia.js integration
- More Ant Design components
- Improved performance
- Better TypeScript support

### v15 (Planned)

- PHP 8.3+ support
- Full TypeScript frontend
- API-first architecture
- Microservices support

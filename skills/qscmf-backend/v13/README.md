# QSMCF Backend3 - Version 13

This directory contains version-specific implementation details for QSMCF Backend3 v13, which is built on Laravel 9/10 with PHP 8.1+ support.

## Version Overview

QSMCF v13 maintains compatibility with:
- Laravel 9.0 - 10.0
- PHP 8.1+ (with 8.2+ recommended)
- Legacy jQuery for frontend
- AntdAdmin v5 components
- Blade templates with legacy syntax

## Key Differences from v14

### Frontend Stack
- **jQuery-based**: Traditional jQuery for DOM manipulation
- **AntdAdmin v5**: Uses AntdAdmin version 5 components
- **Legacy blade syntax**: No modern blade features like `@json` or `@vite`

### ListBuilder Implementation
```php
// v13 ListBuilder without type hints
class ProductListBuilder extends BaseListBuilder
{
    public function getListFields()
    {
        return [
            'id' => ['title' => 'ID', 'width' => 80],
            'name' => ['title' => 'Name', 'minWidth' => 120],
            // ... fields
        ];
    }
}
```

### Controller Patterns
```php
// v13 Admin Controller with minimal type hints
class ProductController extends BaseAdminController
{
    protected $model = 'Product';
    
    protected function getListFields()
    {
        return [
            'id' => ['title' => 'ID', 'width' => 80],
            // ... fields
        ];
    }
}
```

## Version-Specific Features

### Compatibility Mode

To maintain backward compatibility:

```php
// Check Laravel version
if (app()->version() < '11.0') {
    // v13 specific code
    $this->usingLegacyjQuery = true;
} else {
    // v14 specific code
    $this->usingVue3 = true;
}
```

### Database Schema

v13 uses:
- `unsignedInteger()` for primary keys
- `boolean()` for tinyint(1) fields
- Legacy index syntax

```php
Schema::create('products', function (Blueprint $table) {
    $table->increments('id');
    $table->string('name', 255);
    $table->decimal('price', 10, 2)->default(0);
    $table->boolean('status')->default(true);
    $table->timestamps();
});
```

## Migration Considerations

When upgrading from v12 to v13:
1. Update Laravel to 9.x or 10.x
2. Keep jQuery for existing components
3. Update AntdAdmin to v5
4. Maintain legacy blade syntax

## Testing

v13 uses:
- PHPUnit 9.x
- Laravel TestSuite
- Legacy factory methods

```php
class ProductTest extends TestCase
{
    use RefreshDatabase;
    
    public function test_product_creation()
    {
        $product = Product::factory()->create();
        $this->assertNotNull($product);
    }
}
```

## Configuration

### composer.json
```json
{
    "require": {
        "php": "^8.1",
        "laravel/framework": "^9.0|^10.0",
        "tiderjian/qsmcf-core": "^3.0"
    }
}
```

### PHP Version Support
- PHP 8.1: Full support
- PHP 8.2: Recommended for new features
- PHP 8.3: Supported with some deprecations

## Upgrade Path

From v12 to v13:
1. Update dependencies
2. Review blade templates for syntax changes
3. Update jQuery-based components
4. Test all admin functionality

From v13 to v14:
1. Upgrade Laravel to 11.x
2. Migrate to Vue 3 components
3. Update AntdAdmin to v6+
4. Modernize blade templates

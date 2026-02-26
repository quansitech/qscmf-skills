# QSMCF Backend3 - Version 14

This directory contains version-specific implementation details for QSMCF Backend3 v14, which is built on Laravel 11 with PHP 8.3+ support and modern features.

## Version Overview

QSMCF v14 requires:
- Laravel 11.0+
- PHP 8.3+
- Modern Vue 3 composition API
- AntdAdmin v6+ components
- Modern blade templates with new syntax

## Key Features

### Modern PHP 8.3+ Support
```php
// Full type declarations
public function getUserById(int $id): ?User
{
    return $this->user->find($id);
}

// Readonly properties
readonly class UserProfile
{
    public function __construct(
        public readonly int $id,
        public readonly string $name,
        public readonly string $email
    ) {}
}
```

### Vue 3 Composition API
```vue
<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'

const list = ref([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/products')
    list.value = await response.json()
  } catch (error) {
    message.error('Failed to fetch products')
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>
```

### Modern ListBuilder Implementation
```php
// v14 ListBuilder with full PHP 8.3+ type hints
class ProductListBuilder extends BaseListBuilder
{
    public function getListFields(): array
    {
        return [
            'id' => ['title' => 'ID', 'width' => 80],
            'name' => ['title' => 'Name', 'minWidth' => 120],
            // ... fields
        ];
    }
}
```

## Advanced Features

### Laravel 11 Specific Features

#### Route Caching
```php
// routes/web.php
use Illuminate\Support\Facades\Route;

Route::middleware(['auth'])->group(function () {
    Route::get('/products', [ProductController::class, 'index']);
});
```

#### New Enum Types
```php
enum UserStatus: string
{
    case ACTIVE = 'active';
    case INACTIVE = 'inactive';
    
    public function label(): string
    {
        return match($this) {
            self::ACTIVE => 'Active',
            self::INACTIVE => 'Inactive'
        };
    }
}
```

#### Modern Blade Syntax
```blade
{{--
Modern blade features
--}}
@json($data)
@vite('resources/css/app.css')
@once
    <script>console.log('This runs only once')</script>
@endonce
```

### AntdAdmin v6+ Components

```vue
<script setup>
import { Table, Button, Modal, Form } from 'ant-design-vue'

const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    width: 150
  },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
    width: 100,
    customRender: ({ text }) => ({
      text,
      children: h(Tag, { color: text === 'active' ? 'green' : 'red' }, text)
    })
  }
]
</script>
```

## Database Updates

### Laravel 11 Migration Syntax
```php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('products', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->decimal('price', 10, 2)->default(0);
            $table->enum('status', ['active', 'inactive'])->default('active');
            $table->timestamps();
            
            // Modern index syntax
            $table->index('status');
        });
    }
};
```

### Enum Casts
```php
class Product extends Model
{
    protected $casts = [
        'status' => ProductStatus::class
    ];
}
```

## Performance Improvements

### PHP 8.3 JIT Compilation
```php
// Benefit from JIT for performance-critical code
class ProductService
{
    public function calculateTax(float $price): float
    {
        // JIT will optimize this
        return $price * 0.08;
    }
}
```

### Laravel 11 Optimizations
```php
// New query builder features
Product::query()
    ->where('status', 'active')
    ->whereBetween('created_at', [$start, $end])
    ->lazy()  // Memory-efficient iteration
    ->each(fn($product) => $this->process($product));
```

## Testing with Modern Tools

### PHPUnit 10
```php
use PHPUnit\Framework\Attributes\Test;

class ProductTest extends TestCase
{
    #[Test]
    public function it_can_create_product()
    {
        $product = Product::factory()->create();
        
        $this->assertDatabaseHas('products', [
            'id' => $product->id,
            'name' => $product->name
        ]);
    }
}
```

### PestPHP Integration
```php
// tests/Feature/ProductTest.php
test('can create product', function () {
    $product = Product::factory()->create();
    
    expect($product)->toBeInstanceOf(Product::class)
        ->and($product->name)->toBeString();
});

// tests/Unit/ProductServiceTest.php
describe('ProductService', function () {
    it('can calculate price with tax', function () {
        $service = new ProductService();
        $price = 100;
        
        expect($service->calculateWithTax($price))->toBe(108);
    });
});
```

## Configuration

### composer.json
```json
{
    "require": {
        "php": "^8.3",
        "laravel/framework": "^11.0",
        "tiderjian/qsmcf-core": "^3.0"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.0",
        "pestphp/pest": "^2.0"
    }
}
```

### .env
```
APP_ENV=production
APP_DEBUG=false
APP_URL=https://your-app.com

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=your_db
DB_USERNAME=your_username
DB_PASSWORD=your_password

PHP_MEMORY_LIMIT=512M
```

## Migration Guide

### From v13 to v14

1. **Upgrade Dependencies**
```bash
composer require laravel/framework:^11.0 php:^8.3
```

2. **Update Blade Templates**
- Replace jQuery with Vue 3
- Update AntdAdmin to v6
- Use new blade syntax

3. **Modernize Controllers**
- Add full type declarations
- Use modern PHP features
- Implement new ListBuilder patterns

4. **Update Tests**
- Use PHPUnit 10
- Consider PestPHP
- Update assertion methods

5. **Database Schema**
- Use new migration syntax
- Implement enum casts
- Add modern indexes

### Automatic Upgrade

Run the upgrade command:
```bash
php artisan qsmcf:upgrade-to-v14
```

This will:
- Update composer.json
- Migrate templates
- Convert controllers
- Update tests
- Run migrations

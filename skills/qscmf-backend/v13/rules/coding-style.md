> This file extends [../../_shared/references/coding-style.md](../../_shared/references/coding-style.md) with v13-specific patterns for Laravel 9/10 and PHP 8.1+.

# PHP 8.1+ Coding Standards for QSMCF v13

This document extends the common coding style with Laravel 9/10 and PHP 8.1+ specific patterns for backward compatibility.

## v13 Specific Standards

### Type Declarations (Limited)

v13 supports PHP 8.1+ type declarations but maintains backward compatibility:

```php
// Supported with PHP 8.1+
public function getUserById(int $id): ?User
{
    return $this->find($id);
}

// For nullable properties (PHP 8.1+)
protected ?User $user = null;

// For return types (PHP 8.1+)
public function getProducts(): array
{
    return $this->all()->toArray();
}
```

### Constructor Property Promotion (Limited)

```php
// v13 compatible constructor promotion
class UserService
{
    public function __construct(
        protected UserRepository $userRepository,
        protected MailService $mailService
    ) {}
    
    // No promotion for readonly properties (not available in PHP 8.1)
    public function createUser(array $data): User
    {
        $user = new User();
        $user->fill($data);
        $user->save();
        
        return $user;
    }
}
```

### Modern Features (Partial Support)

```php
// Enums (PHP 8.1+)
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

// Match expressions (PHP 8.0+)
$status = 'active';
$label = match($status) {
    'active' => 'Active',
    'inactive' => 'Inactive',
    default => 'Unknown'
};

// Readonly properties (PHP 8.2+)
class UserProfile
{
    // Not readonly in v13 - mutable for compatibility
    public int $id;
    public string $name;
    public string $email;
    
    public function __construct(int $id, string $name, string $email)
    {
        $this->id = $id;
        $this->name = $name;
        $this->email = $email;
    }
}
```

### Legacy jQuery Support

```javascript
// v13 uses jQuery for DOM manipulation
$(document).ready(function() {
    $('#product-form').on('submit', function(e) {
        e.preventDefault();
        
        $.ajax({
            url: '/api/products',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    window.location.reload();
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr) {
                alert('Error: ' + xhr.responseText);
            }
        });
    });
});
```

### AntdAdmin v5 Components

```javascript
// v13 uses AntdAdmin v5
define(['jquery', 'antd'], function($, antd) {
    var Table = antd.Table;
    var Modal = antd.Modal;
    var Form = antd.Form;
    
    return {
        init: function() {
            new Table({
                element: '#product-table',
                url: '/api/products',
                columns: [
                    {
                        title: 'Name',
                        dataIndex: 'name',
                        key: 'name'
                    },
                    {
                        title: 'Status',
                        dataIndex: 'status',
                        key: 'status',
                        render: function(text) {
                            return text === 'active' ? 
                                '<span class="label label-success">Active</span>' : 
                                '<span class="label label-default">Inactive</span>';
                        }
                    }
                ]
            });
        }
    };
});
```

### Laravel 9/10 Specific Patterns

#### Route Definitions
```php
// routes/web.php
use Illuminate\Support\Facades\Route;

Route::middleware(['web', 'auth'])->group(function () {
    Route::get('/admin/products', [ProductController::class, 'index']);
    Route::post('/admin/products', [ProductController::class, 'store']);
    Route::put('/admin/products/{id}', [ProductController::class, 'update']);
    Route::delete('/admin/products/{id}', [ProductController::class, 'destroy']);
});
```

#### Controller with Type Hints
```php
use App\Common\Model\Product;
use App\Common\ListBuilder\ProductListBuilder;
use Illuminate\Http\Request;

class ProductController extends BaseAdminController
{
    protected $model = Product::class;
    
    // Partial type declarations
    public function index(Request $request)
    {
        $listBuilder = new ProductListBuilder($this, $request);
        $data = $listBuilder->getResults();
        
        return view('admin.products.index', ['data' => $data]);
    }
    
    // Form request validation
    public function store(StoreProductRequest $request)
    {
        $product = Product::create($request->validated());
        
        return redirect()->route('admin.products.index')
                        ->with('success', 'Product created successfully');
    }
}
```

#### Blade Templates (Legacy)
```blade
@extends('layouts.admin')

@section('content')
<div class="container">
    <h1>Products Management</h1>
    
    <div class="card">
        <div class="card-header">
            <button class="btn btn-primary" onclick="showCreateModal()">
                <i class="fa fa-plus"></i> Add Product
            </button>
        </div>
        
        <div class="card-body">
            <table class="table table-striped" id="product-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($products as $product)
                    <tr>
                        <td>{{ $product->id }}</td>
                        <td>{{ $product->name }}</td>
                        <td>¥{{ number_format($product->price, 2) }}</td>
                        <td>
                            <span class="label {{ $product->status == 'active' ? 'label-success' : 'label-default' }}">
                                {{ ucfirst($product->status) }}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-info" onclick="editProduct({{ $product->id }})">
                                Edit
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteProduct({{ $product->id }})">
                                Delete
                            </button>
                        </td>
                    </tr>
                    @endforeach
                </tbody>
            </table>
            
            {{ $products->links() }}
        </div>
    </div>
</div>

<!-- Modal using jQuery -->
<div class="modal fade" id="productModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Product Form</h5>
                <button type="button" class="close" data-dismiss="modal">
                    <span>&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <!-- Form content -->
            </div>
        </div>
    </div>
</div>

@push('scripts')
<script src="/js/admin/products.js"></script>
@endpush
@endsection
```

### Migration Patterns (Laravel 9/10)

```php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('products', function (Blueprint $table) {
            $table->increments('id');
            $table->string('name', 255);
            $table->decimal('price', 10, 2)->default(0);
            $table->boolean('status')->default(true);
            $table->timestamps();
        });
    }
    
    public function down()
    {
        Schema::dropIfExists('products');
    }
};
```

### Factory Patterns

```php
use Illuminate\Database\Eloquent\Factories\Factory;

class ProductFactory extends Factory
{
    protected $model = Product::class;
    
    public function definition()
    {
        return [
            'name' => $this->faker->name,
            'price' => $this->faker->randomFloat(2, 10, 1000),
            'status' => $this->faker->boolean,
            'created_at' => now(),
            'updated_at' => now()
        ];
    }
}
```

### Testing with PHPUnit 9

```php
use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class ProductTest extends TestCase
{
    use RefreshDatabase;
    
    public function test_product_creation()
    {
        $product = Product::factory()->create([
            'name' => 'Test Product'
        ]);
        
        $this->assertDatabaseHas('products', [
            'id' => $product->id,
            'name' => 'Test Product'
        ]);
    }
    
    public function test_product_validation()
    {
        $response = $this->post('/api/products', []);
        
        $response->assertSessionHasErrors(['name']);
    }
}
```

### v13 Compatibility Layer

For code that needs to work across versions:

```php
class CompatibilityHelper
{
    public static function getLaravelVersion(): string
    {
        return app()->version();
    }
    
    public static function isVue3(): bool
    {
        return version_compare(self::getLaravelVersion(), '11.0', '>=');
    }
    
    public static function renderTableColumns(array $columns): array
    {
        if (self::isVue3()) {
            return self::formatVue3Columns($columns);
        }
        
        return self::formatLegacyColumns($columns);
    }
    
    private static function formatVue3Columns(array $columns): array
    {
        // Vue 3 column formatting
    }
    
    private static function formatLegacyColumns(array $columns): array
    {
        // Legacy jQuery column formatting
    }
}
```

## Upgrade Considerations

When preparing for v14 upgrade:

1. **Type Declarations**: Currently partial, prepare for full PHP 8.3 types
2. **jQuery Dependencies**: Plan to migrate to Vue 3 components
3. **Blade Templates**: Note legacy syntax that will need updates
4. **AntdAdmin**: v5 components will need v6 updates
5. **PHP Version**: Prepare for upgrade to PHP 8.3

### Migration Preparation

```php
// Preparation code for v14 upgrade
class PreUpgradeHelper
{
    public static function checkForV14Readiness()
    {
        $checks = [
            'php_version' => version_compare(phpversion(), '8.3', '>='),
            'laravel_version' => version_compare(app()->version(), '11.0', '>='),
            'jquery_usage' => self::checkjQueryUsage(),
            'blade_syntax' => self::checkBladeSyntax()
        ];
        
        return $checks;
    }
}
```

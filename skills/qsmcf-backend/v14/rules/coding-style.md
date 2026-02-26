> This file extends [../../_shared/references/coding-style.md](../../_shared/references/coding-style.md) with v14-specific patterns for Laravel 11 and PHP 8.3+.

# PHP 8.3+ Coding Standards for QSMCF v14

This document extends the common coding style with Laravel 11 and PHP 8.3+ specific patterns for modern PHP development.

## v14 Modern Standards

### Full Type Declarations

v14 supports PHP 8.3+ with comprehensive type declarations:

```php
// Strict type declarations
class UserService implements UserServiceInterface
{
    public function __construct(
        private readonly UserRepositoryInterface $userRepository,
        private readonly NotificationService $notificationService
    ) {}
    
    public function getUserById(int $id): ?User
    {
        return $this->userRepository->find($id);
    }
    
    public function getUsersByStatus(UserStatus $status): Collection<User>
    {
        return $this->userRepository->where('status', $status)->get();
    }
    
    public function createUser(array $data): User
    {
        return DB::transaction(function () use ($data) {
            $user = User::create($data);
            $this->notificationService->sendWelcomeEmail($user);
            return $user;
        });
    }
}
```

### Readonly Properties and Classes

```php
// Readonly DTO
readonly class UserProfileDTO
{
    public function __construct(
        public readonly int $id,
        public readonly string $name,
        public readonly string $email,
        private readonly string $passwordHash
    ) {}
    
    public function getEmailDomain(): string
    {
        return substr($this->email, strpos($this->email, '@') + 1);
    }
}

// Immutable service
class ImmutableUserService
{
    public function __construct(
        private readonly User $user,
        private readonly LoggerInterface $logger
    ) {}
    
    public function updateEmail(string $newEmail): self
    {
        $this->logger->info('Updating email', [
            'user_id' => $this->user->id,
            'old_email' => $this->user->email,
            'new_email' => $newEmail
        ]);
        
        // Return new instance with updated email
        return new self(
            user: $this->user->replicate()->fill(['email' => $newEmail]),
            logger: $this->logger
        );
    }
}
```

### Advanced Enum Features

```php
// Enum with methods and static properties
enum UserRole: string
{
    case ADMIN = 'admin';
    case MANAGER = 'manager';
    case USER = 'user';
    case GUEST = 'guest';
    
    // Static method
    public static function fromPermission(string $permission): self
    {
        return match($permission) {
            'create', 'edit', 'delete', 'view_all' => self::ADMIN,
            'create', 'edit', 'view' => self::MANAGER,
            'view' => self::USER,
            default => self::GUEST
        };
    }
    
    // Instance method
    public function canCreate(): bool
    {
        return in_array($this, [self::ADMIN, self::MANAGER]);
    }
    
    public function canDelete(): bool
    {
        return $this === self::ADMIN;
    }
    
    // Enum property with constant
    public const ADMIN_ROLES = [self::ADMIN, self::MANAGER];
    
    // Advanced formatting
    public function formatBadge(): string
    {
        return match($this) {
            self::ADMIN => '<span class="badge bg-danger">Admin</span>',
            self::MANAGER => '<span class="badge bg-warning">Manager</span>',
            self::USER => '<span class="badge bg-info">User</span>',
            self::GUEST => '<span class="badge bg-secondary">Guest</span>'
        };
    }
}
```

### New PHP 8.3+ Features

#### Disjunctive Normal Forms (DNF) Types
```php
// Union of intersections
class PaymentService
{
    public function processPayment(
        CreditCard|PayPal|BankTransfer $paymentMethod,
        User|Company $customer
    ): Transaction {
        // Payment processing logic
    }
}

// Using DNF for complex type hints
class NotificationService
{
    public function send(
        (Email|SMS) $channel,
        User|Company $recipient,
        string $message
    ): bool {
        return match($channel) {
            Email::class => $this->sendEmail($recipient, $message),
            SMS::class => $this->sendSms($recipient, $message)
        };
    }
}
```

### Laravel 11 Specific Features

#### New Route Registration
```php
use Illuminate\Support\Facades\Route;

// Modern route definition
Route::middleware(['auth', 'verified'])->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index'])
         ->name('dashboard');
    
    Route::resource('products', ProductController::class)
         ->except(['create', 'edit']);
});

// Route binding
Route::get('/users/{user:uuid}', [UserController::class, 'show'])
     ->where('user', '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}');
```

#### New Blade Directives
```blade
{{-- Modern blade features --}}
@vite('resources/css/app.css')
@json($config)

{{-- Conditional rendering --}}
@auth
    <nav>Authenticated user menu</nav>
@endauth

{{-- Loops with --}}
@forelse ($products as $product)
    <div class="product">{{ $product->name }}</div>
@empty
    <div>No products found</div>
@endforelse

{{-- Once directive --}}
@once
    <script src="https://cdn.example.com/tracking.js"></script>
@endonce

{{-- Use directive --}}
@use('App\Utils\Formatter')
<div>{{ Formatter::currency($price) }}</div>
```

#### Modern Blade Components
```blade
{{-- Form component --}}
<x-form method="POST" action="/users">
    <x-input label="Name" name="name" required />
    <x-input label="Email" type="email" name="email" required />
    <x-button type="submit" class="btn-primary">Save</x-button>
</x-form>

{{-- Modal component --}}
<x-modal id="userModal">
    <x-modal-header>
        <h5>User Details</h5>
    </x-modal-header>
    <x-modal-body>
        {{ $user->name }}
    </x-modal-body>
</x-modal>
```

### Vue 3 Composition API Integration

```vue
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { message, Modal, Table } from 'ant-design-vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const products = ref([])
const loading = ref(false)
const pagination = ref({
    current: 1,
    pageSize: 15,
    total: 0
})

// Computed property
const activeProducts = computed(() => 
    products.value.filter(p => p.status === 'active')
)

// Async function
const fetchProducts = async () => {
    loading.value = true
    try {
        const response = await fetch('/api/products', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        })
        
        const data = await response.json()
        products.value = data.data
        pagination.value.total = data.pagination.total
    } catch (error) {
        message.error('Failed to load products')
    } finally {
        loading.value = false
    }
}

// Watch for changes
watch(() => pagination.value.current, (newPage) => {
    fetchProducts()
})

// Lifecycle hook
onMounted(fetchProducts)

// Event handlers
const handleTableChange = (pag) => {
    pagination.value = pag
    fetchProducts()
}

const deleteProduct = async (id) => {
    Modal.confirm({
        title: 'Confirm',
        content: 'Are you sure you want to delete this product?',
        onOk: async () => {
            try {
                await fetch(`/api/products/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`
                    }
                })
                
                message.success('Product deleted')
                fetchProducts()
            } catch (error) {
                message.error('Failed to delete product')
            }
        }
    })
}
</script>

<template>
    <div>
        <Table
            :columns="columns"
            :data-source="products"
            :loading="loading"
            :pagination="pagination"
            @change="handleTableChange"
        />
    </div>
</template>
```

### Modern Testing Patterns

#### PHPUnit 10 with Attributes
```php
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class ProductTest extends TestCase
{
    #[Test]
    public function it_can_create_product()
    {
        $product = Product::factory()->create();
        
        $this->assertModelExists($product);
        $this->assertDatabaseHas('products', ['name' => $product->name]);
    }
    
    #[Test]
    #[DataProvider('productStatusProvider')]
    public function it_sets_correct_status(string $input, string $expected)
    {
        $product = Product::factory()->make(['status' => $input]);
        
        $this->assertEquals($expected, $product->status);
    }
    
    public static function productStatusProvider(): array
    {
        return [
            ['active', 'active'],
            ['inactive', 'inactive'],
            ['1', 'active'],
            ['0', 'inactive']
        ];
    }
}
```

#### PestPHP Tests
```php
// tests/Feature/ProductTest.php
test('can create product', function () {
    $product = Product::factory()->create();
    
    expect($product)
        ->toBeInstanceOf(Product::class)
        ->name->toBeString()
        ->price->toBeFloat();
});

describe('ProductService', function () {
    it('calculates tax correctly', function () {
        $service = new ProductService();
        $price = 100;
        
        expect($service->calculateTax($price))->toBe(8);
    });
    
    it('throws exception for negative price', function () {
        $service = new ProductService();
        
        expect(fn() => $service->calculateTax(-10))
            ->toThrow(InvalidArgumentException::class);
    });
});
```

### Database Updates

#### Laravel 11 Migration Syntax
```php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('products', function (Blueprint $table) {
            $table->ulid('id')->primary();
            $table->string('name');
            $table->decimal('price', 10, 2)->default(0);
            $table->enum('status', ['active', 'inactive'])->default('active');
            $table->json('metadata')->nullable();
            $table->timestamps();
            
            // New unique constraint syntax
            $table->unique('name');
            
            // Full-text search
            $table->fullText(['name', 'description']);
        });
    }
};
```

#### Enum Casts
```php
use Illuminate\Database\Eloquent\Casts\AsEnumCollection;

class Product extends Model
{
    protected $casts = [
        'status' => ProductStatus::class,
        'metadata' => 'json',
        'tags' => AsEnumCollection::of(Tag::class)
    ];
    
    // Accessors with type
    public function getIsAvailableAttribute(): bool
    {
        return $this->status === ProductStatus::ACTIVE && $this->stock > 0;
    }
}
```

### Performance Optimizations

#### Laravel 11 Optimizations
```php
// New query builder features
User::query()
    ->where('status', 'active')
    ->whereBetween('created_at', [$start, $end])
    ->lazy()  // Memory efficient
    ->each(fn($user) => $this->processUser($user));

// Chunked processing
Product::query()
    ->where('stock', '<', 10)
    ->chunkById(100, function ($products) {
        $products->each->update(['status' => 'out_of_stock']);
    });

// Aggregate optimizations
$stats = Product::query()
    ->selectRaw('COUNT(*) as total, AVG(price) as avg_price')
    ->where('status', 'active')
    ->first();
```

#### PHP 8.3 JIT Benefits
```php
// Performance critical code benefits from JIT
class CacheService
{
    /**
     * Get or set cache with performance optimization
     */
    public function remember(string $key, int $ttl, callable $callback): mixed
    {
        $value = $this->cache->get($key);
        
        if ($value === null) {
            $value = $callback();
            $this->cache->put($key, $value, $ttl);
        }
        
        return $value;
    }
    
    /**
     * Bulk cache operations
     */
    public function rememberMany(array $keys, int $ttl, callable $callback): array
    {
        $values = $this->cache->many($keys);
        $missing = [];
        
        foreach ($keys as $key) {
            if ($values[$key] === null) {
                $missing[] = $key;
            }
        }
        
        if ($missing) {
            $results = $callback($missing);
            foreach ($results as $key => $value) {
                $this->cache->put($key, $value, $ttl);
            }
        }
        
        return $values;
    }
}
```

### Modern Security Patterns

#### New Authentication Features
```php
use Illuminate\Support\Facades\Auth;
use Illuminate\Auth\AuthenticationException;

class ApiController extends Controller
{
    public function __construct()
    {
        $this->middleware('auth:api');
    }
    
    public function userProfile()
    {
        try {
            $user = Auth::userOrFail();
            return response()->json(['user' => $user]);
        } catch (AuthenticationException $e) {
            return response()->json(['error' => 'Unauthorized'], 401);
        }
    }
}
```

#### Rate Limiting Improvements
```php
// RouteServiceProvider
Route::middleware(['auth', 'throttle:api'])->group(function () {
    Route::get('/api/products', [ProductController::class, 'index']);
    Route::post('/api/products', [ProductController::class, 'store']);
});

// Custom throttle
Route::middleware(['throttle:10,1'])->group(function () {
    Route::post('/api/bulk-products', [ProductController::class, 'bulkStore']);
});
```

## v14 Modern Checklist

Before upgrading to v14:

- [ ] PHP version is 8.3+
- [ ] Laravel version is 11.0+
- [ ] All controllers use full type declarations
- [ ] Properties are marked readonly where appropriate
- [ ] Blade templates use modern syntax
- [ ] JavaScript code uses Vue 3 Composition API
- [ ] Tests use PHPUnit 10 or PestPHP
- [ ] Database schema uses new Laravel 11 features
- [ ] All dependencies are compatible with Laravel 11
- [ ] Performance optimizations are implemented

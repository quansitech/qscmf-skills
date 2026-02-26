> This file extends [../../../rules/common/development-standards.md](../../../rules/common/development-standards.md) with QSMCF-specific development standards.

# PHP 8.2+ Development Standards for QSMCF

This document extends the common development standards with PHP 8.2+ specific patterns and QSMCF framework conventions.

## PHP 8.2+ Requirements

### Required PHP Version
- Minimum PHP 8.2.0
- Recommended PHP 8.3+ for new projects
- PHP 8.1+ for legacy support (v13)

### Composer Dependencies

```json
{
    "require": {
        "php": "^8.2.0",
        "laravel/framework": "^11.0",
        "tiderjian/qsmcf-core": "^3.0"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.0",
        "mockery/mockery": "^1.5",
        "pestphp/pest": "^2.0"
    }
}
```

## Project Structure

### Standard Directory Structure

```
app/
├── Admin/
│   └── Controller/
│       ├── UserController.php
│       ├── ProductController.php
├── Api/
│   └── Controller/
│       ├── UserApiController.php
│       ├── ProductApiController.php
├── Common/
│   ├── ListBuilder/
│   │   ├── ProductListBuilder.php
│   │   └── UserListBuilder.php
│   └── Model/
│       ├── User.php
│       ├── Product.php
│       └── GyListModel.php
├── Jobs/
├── Mail/
├── Services/
│   ├── ProductService.php
│   └── UserService.php
├── Traits/
└── Providers/
```

### Code Organization Rules

1. **Small Files**: Keep individual files under 400 lines
2. **Clear Purpose**: Each file should have a single responsibility
3. **Directory Organization**: Organize by feature/domain, not by type
4. **Consistent Naming**: Use clear, descriptive names

## Coding Standards

### PSR-12 Compliance

```php
<?php

namespace App\Common\Model;

use Gy_Library\GyListModel;
use Illuminate\Database\Eloquent\SoftDeletes;

class User extends GyListModel
{
    use SoftDeletes;

    protected $fillable = [
        'name',
        'email',
        'password',
        'status',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
        'status' => 'string',
    ];

    public function posts()
    {
        return $this->hasMany(Post::class);
    }

    public function isActive(): bool
    {
        return $this->status === 'active';
    }

    public function scopeActive($query)
    {
        return $query->where('status', 'active');
    }
}
```

### Type Declarations

```php
// All methods must have explicit return types
public function getUserById(int $id): ?User
{
    return $this->find($id);
}

// Use union types where appropriate
public function getStatus(): int|string
{
    return $this->status;
}

// Use nullable for optional parameters
public function updateProfile(string $name, ?string $email = null): void
{
    $this->name = $name;
    
    if ($email) {
        $this->email = $email;
    }
    
    $this->save();
}
```

### Constructor Property Promotion

```php
// Simple DTO with promoted properties
readonly class UserProfile
{
    public function __construct(
        public int $id,
        public string $name,
        public string $email,
        private string $password
    ) {}
}

// Service with promoted properties
class UserService
{
    public function __construct(
        private UserRepository $userRepository,
        private MailService $mailService,
        private LoggerInterface $logger
    ) {}

    public function register(array $data): User
    {
        $user = $this->userRepository->create($data);
        
        $this->logger->info('User registered', ['user_id' => $user->id]);
        $this->mailService->sendWelcomeEmail($user);
        
        return $user;
    }
}
```

### Enums Usage

```php
enum UserStatus: string
{
    case ACTIVE = 'active';
    case INACTIVE = 'inactive';
    case SUSPENDED = 'suspended';

    public function label(): string
    {
        return match($this) {
            self::ACTIVE => 'Active',
            self::INACTIVE => 'Inactive',
            self::SUSPENDED => 'Suspended'
        };
    }

    public function color(): string
    {
        return match($this) {
            self::ACTIVE => 'green',
            self::INACTIVE => 'gray',
            self::SUSPENDED => 'red'
        };
    }
}

enum Permission: string
{
    case CREATE = 'create';
    case READ = 'read';
    case UPDATE = 'update';
    case DELETE = 'delete';
}
```

### Attributes Usage

```php
#[ORM\Entity]
#[Table(name: 'users')]
class User extends Model
{
    #[ORM\Id]
    #[ORM\Column(type: 'integer')]
    #[ORM\GeneratedValue]
    private int $id;

    #[ORM\Column(type: 'string', length: 100)]
    #[Required]
    #[MaxLength(100)]
    private string $name;

    #[ORM\Column(type: 'string', unique: true)]
    #[Email]
    private string $email;

    #[ORM\Column(type: 'string')]
    #[Required]
    private string $password;

    #[ORM\Column(type: 'string')]
    #[EnumType(UserStatus::class)]
    #[Default(UserStatus::ACTIVE)]
    private UserStatus $status;
}
```

### Modern PHP Features

#### Arrow Functions
```php
// Instead of
$users = array_map(function ($user) {
    return $user->name;
}, $users);

// Use
$names = array_map(fn($user) => $user->name, $users);
```

#### Match Expressions
```php
// Instead of
switch ($status) {
    case 'active':
        $label = 'Active';
        break;
    case 'inactive':
        $label = 'Inactive';
        break;
    default:
        $label = 'Unknown';
        break;
}

// Use
$label = match($status) {
    'active' => 'Active',
    'inactive' => 'Inactive',
    default => 'Unknown'
};
```

#### Readonly Properties
```php
class UserProfile
{
    public function __construct(
        public readonly int $id,
        public readonly string $name,
        public readonly string $email,
        private string $password
    ) {}

    public function updateEmail(string $email): self
    {
        return new self(
            id: $this->id,
            name: $this->name,
            email: $email,
            password: $this->password
        );
    }
}
```

## Database Standards

### Migration Standards

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
            $table->string('name', 255)->comment('产品名称');
            $table->decimal('price', 10, 2)->comment('价格');
            $table->integer('stock')->default(0)->comment('库存');
            $table->string('status')->default('active')->comment('状态');
            $table->foreignId('category_id')->constrained()->comment('分类ID');
            $table->timestamps();
            $table->softDeletes();
            
            // Add indexes
            $table->index('status');
            $table->index('category_id');
            $table->index(['status', 'stock']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
```

### Model Standards

```php
use Gy_Library\DBCont;
use Illuminate\Database\Eloquent\SoftDeletes;

class Product extends GyListModel
{
    use SoftDeletes;

    protected $table = 'products';
    protected $primaryKey = 'id';
    
    protected $fillable = [
        'name',
        'price',
        'stock',
        'status',
        'category_id',
    ];

    protected $casts = [
        'price' => 'decimal:2',
        'stock' => 'integer',
        'status' => 'string',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    // Constants
    public const STATUS_ACTIVE = 'active';
    public const STATUS_INACTIVE = 'inactive';
    
    // Relationships
    public function category()
    {
        return $this->belongsTo(Category::class);
    }
    
    // Scopes
    public function scopeActive($query)
    {
        return $query->where('status', self::STATUS_ACTIVE);
    }
    
    // Accessors
    public function getFormattedPriceAttribute(): string
    {
        return '¥' . number_format($this->price, 2);
    }
}
```

## Controller Standards

### API Controller Standards

```php
use App\Common\Model\Product;
use App\Http\Requests\StoreProductRequest;
use App\Http\Resources\ProductResource;
use Gy_Library\DBCont;
use Illuminate\Http\Request;

class ProductApiController extends RestController
{
    protected $model = Product::class;
    protected $resourceClass = ProductResource::class;

    public function index(Request $request)
    {
        $query = $this->model::query();
        
        // Search
        if ($request->has('search')) {
            $query->where('name', 'like', "%{$request->search}%");
        }
        
        // Filter
        if ($request->has('status')) {
            $query->where('status', $request->status);
        }
        
        // Pagination
        return $query->paginate(15);
    }

    public function store(StoreProductRequest $request)
    {
        DB::beginTransaction();
        
        try {
            $product = $this->model::create($request->validated());
            DB::commit();
            
            return $this->successResponse($product, 'Product created successfully');
        } catch (\Exception $e) {
            DB::rollBack();
            Log::error('Product creation failed', ['error' => $e->getMessage()]);
            
            return $this->errorResponse('Failed to create product', 500);
        }
    }

    public function show($id)
    {
        $product = $this->model::findOrFail($id);
        
        return $this->successResponse($product);
    }

    public function update(StoreProductRequest $request, $id)
    {
        $product = $this->model::findOrFail($id);
        
        DB::beginTransaction();
        
        try {
            $product->update($request->validated());
            DB::commit();
            
            return $this->successResponse($product, 'Product updated successfully');
        } catch (\Exception $e) {
            DB::rollBack();
            
            return $this->errorResponse('Failed to update product', 500);
        }
    }

    public function destroy($id)
    {
        $product = $this->model::findOrFail($id);
        
        DB::beginTransaction();
        
        try {
            $product->delete();
            DB::commit();
            
            return $this->successResponse(null, 'Product deleted successfully');
        } catch (\Exception $e) {
            DB::rollBack();
            
            return $this->errorResponse('Failed to delete product', 500);
        }
    }
}
```

### Admin Controller Standards

```php
use App\Common\Model\Product;
use App\Common\ListBuilder\ProductListBuilder;
use Gy_Library\DBCont;

class ProductController extends QsListController
{
    protected $model = Product::class;
    protected $listBuilderClass = ProductListBuilder::class;

    protected function getListFields(): array
    {
        return [
            'id' => ['title' => 'ID', 'width' => 80],
            'name' => ['title' => 'Name', 'minWidth' => 120],
            'price' => ['title' => 'Price', 'type' => 'money', 'width' => 120],
            'stock' => ['title' => 'Stock', 'width' => 100],
            'status' => [
                'title' => 'Status',
                'type' => 'select',
                'options' => [
                    Product::STATUS_ACTIVE => 'Active',
                    Product::STATUS_INACTIVE => 'Inactive'
                ]
            ],
            'created_at' => ['title' => 'Created', 'width' => 160, 'sorter' => true]
        ];
    }

    protected function getFormFields(): array
    {
        return [
            'name' => [
                'label' => 'Product Name',
                'type' => 'text',
                'rules' => 'required|string|max:255'
            ],
            'price' => [
                'label' => 'Price',
                'type' => 'number',
                'rules' => 'required|numeric|min:0'
            ],
            'stock' => [
                'label' => 'Stock',
                'type' => 'number',
                'rules' => 'required|integer|min:0'
            ],
            'status' => [
                'label' => 'Status',
                'type' => 'select',
                'options' => [
                    Product::STATUS_ACTIVE => 'Active',
                    Product::STATUS_INACTIVE => 'Inactive'
                ]
            ]
        ];
    }
}
```

## Service Layer Standards

### Service Pattern

```php
interface ProductServiceInterface
{
    public function create(array $data): Product;
    public function update(Product $product, array $data): Product;
    public function delete(Product $product): bool;
    public function getLowStockProducts(int $threshold = 10): Collection;
}

class ProductService implements ProductServiceInterface
{
    public function __construct(
        private ProductRepository $productRepository,
        private InventoryService $inventoryService,
        private NotificationService $notificationService
    ) {}

    public function create(array $data): Product
    {
        // Business logic
        if ($data['price'] < 0) {
            throw new \InvalidArgumentException('Price cannot be negative');
        }

        // Create product
        $product = $this->productRepository->create($data);

        // Update inventory
        $this->inventoryService->createInventoryRecord($product, 'create', $data['stock'] ?? 0);

        // Notify
        $this->notificationService->notifyAdmin('New product created: ' . $product->name);

        return $product;
    }

    public function getLowStockProducts(int $threshold = 10): Collection
    {
        return $this->productRepository->where('stock', '<=', $threshold)->get();
    }
}
```

### Repository Pattern

```php
interface ProductRepositoryInterface
{
    public function find(int $id): ?Product;
    public function all(): Collection;
    public function create(array $data): Product;
    public function update(Product $product, array $data): Product;
    public function delete(Product $product): bool;
}

class ProductRepository implements ProductRepositoryInterface
{
    public function __construct(
        private Product $model,
        private Cache $cache
    ) {}

    public function find(int $id): ?Product
    {
        return $this->cache->remember("product:{$id}", 3600, function () use ($id) {
            return $this->model->find($id);
        });
    }

    public function all(): Collection
    {
        return $this->model->orderBy('created_at', 'desc')->get();
    }

    public function create(array $data): Product
    {
        return $this->model->create($data);
    }

    public function update(Product $product, array $data): Product
    {
        $product->update($data);
        $this->cache->tags(['products'])->flush();
        
        return $product;
    }

    public function delete(Product $product): bool
    {
        return $product->delete();
    }
}
```

## Testing Standards

### Unit Testing

```php
use App\Common\Model\Product;
use App\Services\ProductService;
use PHPUnit\Framework\MockObject\MockObject;

class ProductServiceTest extends TestCase
{
    private ProductService $service;
    private ProductRepositoryInterface|MockObject $repository;
    private InventoryService|MockObject $inventoryService;
    private NotificationService|MockObject $notificationService;

    protected function setUp(): void
    {
        parent::setUp();
        
        $this->repository = $this->createMock(ProductRepositoryInterface::class);
        $this->inventoryService = $this->createMock(InventoryService::class);
        $this->notificationService = $this->createMock(NotificationService::class);
        
        $this->service = new ProductService(
            $this->repository,
            $this->inventoryService,
            $this->notificationService
        );
    }

    public function test_create_product(): void
    {
        // Arrange
        $productData = [
            'name' => 'Test Product',
            'price' => 99.99,
            'stock' => 10
        ];

        $this->repository->expects($this->once())
            ->method('create')
            ->with($productData)
            ->willReturn(new Product($productData));

        $this->inventoryService->expects($this->once())
            ->method('createInventoryRecord');

        $this->notificationService->expects($this->once())
            ->method('notifyAdmin');

        // Act
        $result = $this->service->create($productData);

        // Assert
        $this->assertInstanceOf(Product::class, $result);
        $this->assertEquals('Test Product', $result->name);
    }

    public function test_create_product_with_negative_price(): void
    {
        $this->expectException(\InvalidArgumentException::class);
        $this->expectExceptionMessage('Price cannot be negative');

        $this->service->create([
            'name' => 'Test Product',
            'price' => -10,
            'stock' => 10
        ]);
    }
}
```

### Feature Testing

```php
use App\Common\Model\Product;
use App\Services\ProductService;
use Tests\TestCase;

class ProductFeatureTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();
        $this->actingAs(User::factory()->create());
    }

    public function test_can_create_product(): void
    {
        $productData = [
            'name' => 'Test Product',
            'price' => 99.99,
            'stock' => 10
        ];

        $response = $this->postJson('/api/products', $productData);

        $response->assertStatus(201)
            ->assertJsonFragment(['name' => 'Test Product']);

        $this->assertDatabaseHas('products', ['name' => 'Test Product']);
    }

    public function test_can_update_product(): void
    {
        $product = Product::factory()->create();
        $updateData = ['name' => 'Updated Product'];

        $response = $this->putJson("/api/products/{$product->id}", $updateData);

        $response->assertStatus(200)
            ->assertJsonFragment(['name' => 'Updated Product']);

        $this->assertDatabaseHas('products', ['name' => 'Updated Product']);
    }
}
```

### Pest Testing

```php
// Example of Pest test
uses(Tests\TestCase::class);
use App\Common\Model\Product;
use App\Services\ProductService;

test('can create product', function () {
    $service = new ProductService(/* dependencies */);
    
    $product = $service->create([
        'name' => 'Test Product',
        'price' => 99.99,
        'stock' => 10
    ]);
    
    expect($product)->toBeInstanceOf(Product::class)
        ->and($product->name)->toBe('Test Product');
});

test('cannot create product with negative price', function () {
    $service = new ProductService(/* dependencies */);
    
    expect(fn() => $service->create([
        'name' => 'Test Product',
        'price' => -10,
        'stock' => 10
    ))->toThrow(\InvalidArgumentException::class);
});
```

## Security Standards

### Input Validation

```php
use Illuminate\Foundation\Http\FormRequest;

class StoreProductRequest extends FormRequest
{
    public function authorize(): bool
    {
        return auth()->check();
    }

    public function rules(): array
    {
        return [
            'name' => 'required|string|max:255',
            'price' => 'required|numeric|min:0|max:999999.99',
            'stock' => 'required|integer|min:0|max:999999',
            'category_id' => 'required|exists:categories,id',
            'image' => 'nullable|image|max:2048|mimes:jpeg,png,jpg,gif',
        ];
    }

    public function messages(): array
    {
        return [
            'name.required' => 'Product name is required',
            'price.min' => 'Price must be greater than 0',
            'stock.max' => 'Stock cannot exceed 999999',
        ];
    }
}
```

### Authentication and Authorization

```php
use Illuminate\Auth\Access\HandlesAuthorization;

class ProductPolicy
{
    use HandlesAuthorization;

    public function view(User $user, Product $product): bool
    {
        return $user->id === $product->user_id || $user->isAdmin();
    }

    public function create(User $user): bool
    {
        return $user->can('create-product');
    }

    public function update(User $user, Product $product): bool
    {
        return $user->id === $product->user_id || $user->isAdmin();
    }

    public function delete(User $user, Product $product): bool
    {
        return $user->id === $product->user_id || $user->isAdmin();
    }
}

// Usage in controller
class ProductApiController extends Controller
{
    public function __construct()
    {
        $this->authorizeResource(Product::class, 'product');
    }
}
```

## Performance Standards

### Query Optimization

```php
// Bad - N+1 query problem
$users = User::all();
foreach ($users as $user) {
    $posts = $user->posts;
    // Process posts
}

// Good - Eager loading
$users = User::with('posts')->get();
foreach ($users as $user) {
    $posts = $user->posts;
    // Process posts
}

// Good - Specific columns
$users = User::select('id', 'name')->with(['posts' => function ($query) {
    $query->select('id', 'user_id', 'title');
}])->get();
```

### Caching

```php
use Illuminate\Support\Facades\Cache;

class ProductService
{
    public function getProduct(int $id): Product
    {
        return Cache::remember("product:{$id}", 3600, function () use ($id) {
            return Product::find($id);
        });
    }

    public function getActiveProducts(): Collection
    {
        return Cache::remember('active:products', 3600, function () {
            return Product::active()->get();
        });
    }

    public function clearProductCache(int $id): void
    {
        Cache::forget("product:{$id}");
        Cache::tags(['products'])->flush();
    }
}
```

## Documentation Standards

### PHPDoc Standards

```php
/**
 * Product Service class for managing product operations.
 * 
 * This service handles product creation, update, deletion, and provides
 * business logic for product-related operations.
 */
class ProductService implements ProductServiceInterface
{
    /**
     * Create a new product.
     *
     * @param array $data The product data to create
     * @return Product The created product
     * @throws InvalidArgumentException If price is negative
     * @throws \Exception If creation fails
     */
    public function create(array $data): Product
    {
        // Implementation
    }

    /**
     * Get products with low stock.
     *
     * @param int $threshold The stock threshold for "low stock"
     * @return Collection Collection of products with low stock
     */
    public function getLowStockProducts(int $threshold = 10): Collection
    {
        // Implementation
    }
}
```

### API Documentation

```php
/**
 * @OA\Info(
 *     title="QSMCF API",
 *     version="1.0.0",
 *     description="QSMCF Management API Documentation"
 * )
 */

/**
 * @OA\Get(
 *     path="/api/products",
 *     summary="Get list of products",
 *     tags={"Products"},
 *     security={{"bearerAuth": {}}},
 *     @OA\Parameter(
 *         name="page",
 *         in="query",
 *         description="Page number",
 *         @OA\Schema(type="integer", default=1)
 *     ),
 *     @OA\Response(
 *         response=200,
 *         description="Successful operation",
 *         @OA\JsonContent(
 *             type="object",
 *             @OA\Property(property="data", type="array", @OA\Items(ref="#/components/schemas/Product"))
 *         )
 *     )
 * )
 */
public function index(): LengthAwarePaginator
{
    return Product::paginate(15);
}
```

## Best Practices Checklist

### Before Committing Code

- [ ] All code follows PSR-12 standards
- [ ] Type declarations are used on all methods
- [ ] Input validation is implemented
- [ ] Error handling is comprehensive
- [ ] Unit tests are written
- [ ] Feature tests are written
- [ ] Code is documented with PHPDoc
- [ ] Caching is implemented for frequently accessed data
- [ ] Database queries are optimized
- [ ] Security measures are in place
- [ ] Code follows the single responsibility principle

### Performance Checklist

- [ ] Use eager loading to avoid N+1 queries
- [ ] Implement proper caching strategies
- [ ] Use pagination for large datasets
- [ ] Add database indexes for frequently queried columns
- [ ] Use queue jobs for time-consuming operations
- [ ] Optimize images and other assets
- [ ] Use CDN for static assets
- [ ] Monitor and optimize query performance
- [ ] Implement proper logging for debugging
- [ ] Use compression for API responses

### Security Checklist

- [ ] All user input is validated
- [ ] SQL injection is prevented
- [ ] XSS protection is implemented
- [ ] CSRF protection is enabled
- [ ] Authentication and authorization are properly implemented
- [ ] Rate limiting is applied to API endpoints
- [ ] Environment variables are properly secured
- [ ] Sensitive data is encrypted
- [ ] Regular security audits are performed
- [ ] Dependencies are up-to-date and secure

> This file extends [../../_shared/references/development-standards.md](../../_shared/references/development-standards.md) with v14-specific patterns for Laravel 11 and PHP 8.3+.

# Laravel 11 Development Standards for QSMCF v14

This document provides version-specific development standards for QSMCF v14, built on Laravel 11 with PHP 8.3+ support and modern features.

## v14 Modern Configuration

### Laravel 11 Application Structure

```
app/
├── Http/
│   ├── Controllers/
│   │   ├── Admin/
│   │   │   ├── ProductController.php
│   │   │   └── UserController.php
│   │   └── Api/
│   │       ├── ProductApiController.php
│   │       └── UserApiController.php
│   ├── Middleware/
│   └── Kernel.php
├── Models/
├── Repositories/
├── Services/
├── Data/
│   ├── Products/Product.php
│   ├── Users/User.php
│   └── Enums/
├── Support/
│   ├── Traits/
│   └── Enums/
├── Database/
│   ├── Factories/
│   ├── Migrations/
│   └── Seeders/
├── Resources/
│   ├── js/
│   │   ├── components/
│   │   ├── composables/
│   │   └── stores/
│   ├── views/
│   └── lang/
├── routes/
│   ├── api.php
│   ├── web.php
│   └── admin.php
├── config/
├── public/
└── tests/
```

### Laravel 11 Modern Configuration

#### Tailwind CSS Configuration
```php
// config/tailwind.php
return [
    'safety' => [
        'safelist' => [
            'btn-primary',
            'btn-danger',
            'form-control',
            'table-striped',
        ],
    ],
];
```

#### Laravel 11 Service Providers
```php
// app/Providers/AppServiceProvider.php
namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\View;
use App\Models\Category;
use App\Data\Enums\ProductStatus;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        // Bind repositories
        $this->app->bind(
            ProductRepositoryInterface::class,
            ProductRepository::class
        );
    }

    public function boot(): void
    {
        // Share categories with all views
        View::share('categories', Category::active()->get());
        
        // Define custom validation rule
        \Validator::extend('unique_with', function ($attribute, $value, $parameters, $validator) {
            $table = $parameters[0];
            $exceptId = $parameters[1] ?? null;
            
            return !\DB::table($table)
                      ->where($attribute, $value)
                      ->where('id', '!=', $exceptId)
                      ->exists();
        });
    }
}
```

### Modern Authentication Guards

```php
// config/auth.php
return [
    'defaults' => [
        'guard' => 'web',
        'password' => 'users',
    ],

    'guards' => [
        'web' => [
            'driver' => 'session',
            'provider' => 'users',
        ],
        'api' => [
            'driver' => 'token',
            'provider' => 'users',
            'hash' => false,
        ],
        'admin' => [
            'driver' => 'session',
            'provider' => 'admins',
        ],
    ],

    'providers' => [
        'users' => [
            'driver' => 'eloquent',
            'model' => App\Data\Users\User::class,
        ],
        'admins' => [
            'driver' => 'eloquent',
            'model' => App\Data\Admins\Admin::class,
        ],
    ],
];
```

## v14 Modern Development Patterns

### Controllers with Full Type Declarations

#### Admin Controller with PHP 8.3+
```php
namespace App\Http\Controllers\Admin;

use App\Common\Controllers\BaseAdminController;
use App\Data\Products\Product;
use App\Common\ListBuilder\ProductListBuilder;
use App\Http\Requests\StoreProductRequest;
use App\Http\Requests\UpdateProductRequest;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class ProductController extends BaseAdminController
{
    protected string $model = Product::class;
    
    public function index(Request $request): \Illuminate\View\View
    {
        $listBuilder = new ProductListBuilder($this, $request);
        $data = $listBuilder->getResults();
        
        return view('admin.products.index', ['data' => $data]);
    }
    
    public function store(StoreProductRequest $request): \Illuminate\Http\RedirectResponse
    {
        try {
            DB::beginTransaction();
            
            $product = Product::create($request->validated());
            
            // Handle image upload
            if ($request->hasFile('image')) {
                $image = $request->file('image');
                $path = $image->store('products', 'public');
                $product->image = $path;
                $product->save();
            }
            
            DB::commit();
            
            return redirect()
                ->route('admin.products.index')
                ->with('success', 'Product created successfully');
                
        } catch (\Exception $e) {
            DB::rollBack();
            
            return redirect()
                ->back()
                ->withInput()
                ->with('error', 'Error creating product: ' . $e->getMessage());
        }
    }
    
    public function update(UpdateProductRequest $request, Product $product): \Illuminate\Http\RedirectResponse
    {
        try {
            DB::beginTransaction();
            
            $product->update($request->validated());
            
            // Handle image update
            if ($request->hasFile('image')) {
                // Delete old image
                if ($product->image) {
                    Storage::disk('public')->delete($product->image);
                }
                
                // Upload new image
                $image = $request->file('image');
                $path = $image->store('products', 'public');
                $product->image = $path;
                $product->save();
            }
            
            DB::commit();
            
            return redirect()
                ->route('admin.products.index')
                ->with('success', 'Product updated successfully');
                
        } catch (\Exception $e) {
            DB::rollBack();
            
            return redirect()
                ->back()
                ->withInput()
                ->with('error', 'Error updating product: ' . $e->getMessage());
        }
    }
}
```

#### API Controller with Modern Features
```php
namespace App\Http\Controllers\Api;

use App\Common\Controllers\BaseApiController;
use App\Data\Products\Product;
use App\Http\Resources\ProductResource;
use App\Data\Enums\ProductStatus;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Cache;

class ProductApiController extends BaseApiController
{
    protected string $model = Product::class;
    protected string $resourceClass = ProductResource::class;
    
    public function index(Request $request): \Illuminate\Http\JsonResponse
    {
        $cacheKey = 'products:' . md5($request->fullUrl());
        
        return Cache::remember($cacheKey, 3600, function () use ($request) {
            $query = $this->model::query();
            
            // Apply filters
            if ($request->has('category_id')) {
                $query->where('category_id', $request->category_id);
            }
            
            if ($request->has('status')) {
                $query->where('status', ProductStatus::from($request->status));
            }
            
            if ($request->has('search')) {
                $query->where(function($q) use ($request) {
                    $q->where('name', 'like', "%{$request->search}%")
                      ->orWhere('description', 'like', "%{$request->search}%");
                });
            }
            
            // Apply sorting
            if ($request->has('sort')) {
                $sort = $request->sort;
                $order = $request->order ?? 'asc';
                $query->orderBy($sort, $order);
            }
            
            // Paginate
            $perPage = $request->input('per_page', 15);
            $products = $query->paginate($perPage);
            
            return $this->successResponse(
                ProductResource::collection($products)
            );
        });
    }
    
    public function featured(): \Illuminate\Http\JsonResponse
    {
        $products = Cache::remember('featured:products', 3600, function () {
            return $this->model::where('featured', true)
                             ->where('status', ProductStatus::ACTIVE)
                             ->take(10)
                             ->get();
        });
        
        return $this->successResponse(
            ProductResource::collection($products)
        );
    }
    
    public function bulkUpdate(Request $request): \Illuminate\Http\JsonResponse
    {
        $validated = $request->validate([
            'ids' => 'required|array|min:1',
            'ids.*' => 'integer|exists:products,id',
            'status' => 'required|string|in:active,inactive'
        ]);
        
        $updatedCount = $this->model::whereIn('id', $validated['ids'])
                                   ->update(['status' => $validated['status']]);
        
        // Clear cache
        Cache::tags(['products'])->flush();
        
        return $this->successResponse(
            null,
            "Successfully updated {$updatedCount} products",
            200,
            ['updated_count' => $updatedCount]
        );
    }
}
```

### Modern Vue 3 Components

#### Product Table Component
```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { Table, Tag, Button, Modal, message } from 'ant-design-vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const products = ref([])
const pagination = ref({
    current: 1,
    pageSize: 15,
    total: 0
})
const selectedRowKeys = ref([])
const bulkModalVisible = ref(false)

// Columns definition
const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
    width: 80,
    fixed: 'left'
  },
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
    width: 150,
    ellipsis: true,
    tooltip: true
  },
  {
    title: 'Category',
    dataIndex: ['category', 'name'],
    key: 'category',
    width: 120,
    customRender: ({ text }) => h(Tag, { color: 'blue' }, text || '-')
  },
  {
    title: 'Price',
    dataIndex: 'price',
    key: 'price',
    width: 120,
    align: 'right',
    customRender: ({ text }) => h('span', '¥' + text.toFixed(2))
  },
  {
    title: 'Stock',
    dataIndex: 'stock',
    key: 'stock',
    width: 100,
    align: 'right',
    sorter: true
  },
  {
    title: 'Status',
    dataIndex: 'status',
    key: 'status',
    width: 100,
    customRender: ({ text }) => {
      const colors = {
        active: 'green',
        inactive: 'red',
        out_of_stock: 'orange'
      }
      return h(Tag, { color: colors[text] || 'default' }, text)
    }
  },
  {
    title: 'Created',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 160,
    customRender: ({ text }) => new Date(text).toLocaleString()
  },
  {
    title: 'Actions',
    key: 'actions',
    width: 150,
    fixed: 'right',
    customRender: ({ record }) => [
      h(Button, {
        type: 'link',
        onClick: () => editProduct(record.id)
      }, 'Edit'),
      h(Button, {
        type: 'link',
        danger: true,
        onClick: () => deleteProduct(record.id)
      }, 'Delete')
    ]
  }
]

// Computed properties
const hasSelected = computed(() => selectedRowKeys.value.length > 0)
const selectedProducts = computed(() => 
  products.value.filter(p => selectedRowKeys.value.includes(p.id))
)

// Data fetching
const fetchProducts = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: pagination.value.current,
      per_page: pagination.value.pageSize
    })
    
    const response = await fetch(`/api/products?${params}`, {
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

// CRUD operations
const editProduct = (id) => {
  router.push(`/admin/products/${id}/edit`)
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

// Bulk actions
const showBulkModal = () => {
  bulkModalVisible.value = true
}

const executeBulkAction = async (action) => {
  if (!action) return
  
  try {
    await fetch('/api/products/bulk', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        ids: selectedRowKeys.value,
        action: action
      })
    })
    
    message.success(`Bulk ${action} completed`)
    bulkModalVisible.value = false
    selectedRowKeys.value = []
    fetchProducts()
  } catch (error) {
    message.error('Bulk operation failed')
  }
}

// Event handlers
const handleTableChange = (pag) => {
  pagination.value = pag
  fetchProducts()
}

const onSelectChange = (selectedKeys) => {
  selectedRowKeys.value = selectedKeys
}

// Lifecycle
onMounted(fetchProducts)
</script>

<template>
  <div class="products-container">
    <!-- Actions -->
    <div class="actions mb-4">
      <button 
        v-if="hasSelected"
        class="btn btn-primary me-2"
        @click="showBulkModal"
      >
        Bulk Actions ({{ selectedProducts.length }})
      </button>
      <button class="btn btn-success" @click="router.push('/admin/products/create')">
        <i class="fas fa-plus"></i> Add Product
      </button>
    </div>
    
    <!-- Data Table -->
    <Table
      :columns="columns"
      :data-source="products"
      :loading="loading"
      :pagination="pagination"
      :row-selection="{
        selectedRowKeys,
        onChange: onSelectChange
      }"
      @change="handleTableChange"
      row-key="id"
      size="middle"
    />
    
    <!-- Bulk Actions Modal -->
    <Modal
      v-model:open="bulkModalVisible"
      title="Bulk Actions"
      :ok-button-props="{ loading }"
      @ok="executeBulkAction('activate')"
    >
      <p>Selected {{ selectedProducts.length }} products</p>
      <div class="mb-3">
        <Button 
          type="primary" 
          @click="executeBulkAction('activate')"
          :disabled="!hasSelected"
        >
          Activate Selected
        </Button>
        <Button 
          type="default" 
          @click="executeBulkAction('deactivate')"
          :disabled="!hasSelected"
          class="ms-2"
        >
          Deactivate Selected
        </Button>
        <Button 
          type="danger" 
          @click="executeBulkAction('delete')"
          :disabled="!hasSelected"
          class="ms-2"
        >
          Delete Selected
        </Button>
      </div>
    </Modal>
  </div>
</template>

<style scoped>
.products-container {
  padding: 20px;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.ant-table {
  background: white;
}
</style>
```

### Laravel 11 Migrations

#### Modern Migration Syntax
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
            $table->string('name', 255)->comment('Product name');
            $table->text('description')->nullable()->comment('Product description');
            $table->decimal('price', 10, 2)->default(0)->comment('Product price');
            $table->decimal('discount_price', 10, 2)->nullable()->comment('Discount price');
            $table->integer('stock')->default(0)->comment('Stock quantity');
            $table->json('metadata')->nullable()->comment('Additional metadata');
            $table->foreignUlid('category_id')
                  ->references('id')
                  ->on('categories')
                  ->nullOnDelete();
            $table->string('image')->nullable()->comment('Main product image');
            $table->json('gallery')->nullable()->comment('Product gallery images');
            $table->timestamps();
            $table->softDeletes();
            
            // Indexes
            $table->index('name');
            $table->index('status');
            $table->index(['category_id', 'status']);
            $table->fullText(['name', 'description']);
            
            // Unique constraints
            $table->unique(['name', 'category_id']);
        });
    }
    
    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
```

#### Laravel 11 Model with Enums
```php
namespace App\Data\Products;

use App\Data\Enums\ProductStatus;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Database\Eloquent\Casts\AsArrayObject;

class Product extends Model
{
    use SoftDeletes;
    
    protected string $table = 'products';
    protected string $primaryKey = 'id';
    protected bool $incrementing = false;
    
    protected array $fillable = [
        'name', 'description', 'price', 'discount_price', 'stock',
        'category_id', 'image', 'gallery', 'metadata'
    ];
    
    protected $casts = [
        'price' => 'decimal:2',
        'discount_price' => 'decimal:2',
        'stock' => 'integer',
        'metadata' => AsArrayObject::class,
        'gallery' => 'array',
        'status' => ProductStatus::class,
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
        'deleted_at' => 'datetime'
    ];
    
    // Relationships
    public function category()
    {
        return $this->belongsTo(Category::class);
    }
    
    // Accessors
    public function getFormattedPriceAttribute(): string
    {
        return '¥' . number_format($this->price, 2);
    }
    
    public function getFormattedDiscountPriceAttribute(): string
    {
        if ($this->discount_price) {
            return '¥' . number_format($this->discount_price, 2);
        }
        return '';
    }
    
    public function getHasDiscountAttribute(): bool
    {
        return $this->discount_price && $this->discount_price < $this->price;
    }
    
    // Scopes
    public function scopeActive($query)
    {
        return $query->where('status', ProductStatus::ACTIVE);
    }
    
    public function scopeFeatured($query)
    {
        return $query->where('featured', true);
    }
    
    public function scopeOutOfStock($query)
    {
        return $query->where('stock', 0);
    }
    
    // Business methods
    public function isAvailable(): bool
    {
        return $this->status === ProductStatus::ACTIVE && $this->stock > 0;
    }
    
    public function getStockStatus(): string
    {
        if ($this->stock === 0) {
            return 'out_of_stock';
        }
        
        if ($this->stock < 10) {
            return 'low_stock';
        }
        
        return 'in_stock';
    }
}
```

### Modern Testing with PHPUnit 10

#### Feature Test with Attributes
```php
namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Data\Products\Product;
use App\Data\Categories\Category;
use App\Data\Enums\ProductStatus;
use PHPUnit\Framework\Attributes\Test;

class ProductTest extends TestCase
{
    use RefreshDatabase;
    
    #[Test]
    public function it_can_create_product()
    {
        $category = Category::factory()->create();
        
        $productData = [
            'name' => 'Test Product',
            'description' => 'Test Description',
            'price' => 99.99,
            'stock' => 10,
            'category_id' => $category->id
        ];
        
        $response = $this->post('/admin/products', $productData);
        
        $response->assertRedirect('/admin/products');
        $this->assertDatabaseHas('products', $productData);
        
        // Verify cast values
        $product = Product::where('name', 'Test Product')->first();
        $this->assertEquals(99.99, $product->price);
        $this->assertEquals(10, $product->stock);
    }
    
    #[Test]
    public function it_can_update_product()
    {
        $product = Product::factory()->create();
        $updatedData = [
            'name' => 'Updated Product Name',
            'price' => 149.99
        ];
        
        $response = $this->put("/admin/products/{$product->id}", $updatedData);
        
        $response->assertRedirect('/admin/products');
        $this->assertDatabaseHas('products', $updatedData);
    }
    
    #[Test]
    public function it_can_delete_product()
    {
        $product = Product::factory()->create();
        
        $response = $this->delete("/admin/products/{$product->id}");
        
        $response->assertRedirect('/admin/products');
        $this->assertSoftDeleted($product);
    }
    
    #[Test]
    public function it_validates_product_creation()
    {
        $response = $this->post('/admin/products', [
            'name' => '',
            'price' => -10
        ]);
        
        $response->assertSessionHasErrors(['name', 'price']);
    }
    
    #[Test]
    public function it_casts_status_enum_correctly()
    {
        $product = Product::factory()->create([
            'status' => 'inactive'
        ]);
        
        $this->assertEquals(ProductStatus::INACTIVE, $product->status);
        $this->assertFalse($product->isAvailable());
    }
}
```

#### API Test with Modern Patterns
```php
namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Data\Products\Product;
use App\Data\Enums\ProductStatus;
use PHPUnit\Framework\Attributes\Test;
use PHPUnit\Framework\Attributes\DataProvider;

class ProductApiTest extends TestCase
{
    use RefreshDatabase;
    
    #[Test]
    public function it_returns_paginated_product_list()
    {
        Product::factory(5)->create();
        
        $response = $this->get('/api/products');
        
        $response->assertStatus(200)
                ->assertJsonStructure([
                    'success',
                    'data' => [
                        '*' => ['id', 'name', 'price']
                    ],
                    'pagination'
                ]);
    }
    
    #[Test]
    public function it_searches_products()
    {
        Product::factory()->create(['name' => 'Test Product']);
        Product::factory()->create(['name' => 'Another Product']);
        
        $response = $this->get('/api/products?search=Test');
        
        $response->assertStatus(200)
                ->assertJsonCount(1, 'data');
    }
    
    #[Test]
    public function it_filters_products_by_status()
    {
        Product::factory()->create(['status' => 'active']);
        Product::factory()->create(['status' => 'inactive']);
        
        $response = $this->get('/api/products?status=active');
        
        $response->assertStatus(200)
                ->assertJsonCount(1, 'data');
        
        // Verify cast enum
        $data = $response->json('data');
        $this->assertEquals(ProductStatus::ACTIVE, $data[0]['status']);
    }
    
    #[Test]
    public function it_creates_product()
    {
        $productData = [
            'name' => 'New Product',
            'price' => 99.99,
            'stock' => 10,
            'status' => 'active'
        ];
        
        $response = $this->post('/api/products', $productData);
        
        $response->assertStatus(201)
                ->assertJsonFragment(['name' => 'New Product']);
        
        $this->assertDatabaseHas('products', $productData);
    }
    
    #[Test]
    #[DataProvider('productStatusProvider')]
    public function it_validates_status_enum(string $input, ProductStatus $expected)
    {
        $product = Product::factory()->create(['status' => $input]);
        
        $this->assertEquals($expected, $product->status);
    }
    
    public static function productStatusProvider(): array
    {
        return [
            ['active', ProductStatus::ACTIVE],
            ['inactive', ProductStatus::INACTIVE]
        ];
    }
}
```

### Modern Performance Patterns

#### Query Optimization with Laravel 11
```php
class ProductController extends Controller
{
    public function index(Request $request): \Illuminate\Http\JsonResponse
    {
        return Cache::tags(['products'])->remember('products:index:' . $request->fullUrl(), 3600, function () use ($request) {
            $query = Product::query()
                           ->select(['id', 'name', 'price', 'category_id', 'status', 'created_at'])
                           ->with(['category:id,name'])
                           ->where('status', ProductStatus::ACTIVE);
            
            // Add search with full-text
            if ($request->search) {
                $query->whereFullText(['name', 'description'], $request->search);
            }
            
            // Add filters
            if ($request->category_id) {
                $query->where('category_id', $request->category_id);
            }
            
            // Add ordering
            if ($request->sort) {
                $query->orderBy($request->sort, $request->order ?? 'asc');
            }
            
            return $query->paginate($request->per_page ?? 15);
        });
    }
}
```

#### Modern Caching Strategy
```php
class ProductCacheService
{
    private const CACHE_TAGS = ['products'];
    private const CACHE_TTL = 3600; // 1 hour
    
    public function __construct(
        private \Illuminate\Contracts\Cache\Repository $cache
    ) {}
    
    public function getProduct(int $id): ?Product
    {
        return $this->cache->tags(self::CACHE_TAGS)
                          ->remember("product:{$id}", self::CACHE_TTL, function () use ($id) {
            return Product::find($id);
        });
    }
    
    public function getFeaturedProducts(): Collection
    {
        return $this->cache->tags(self::CACHE_TAGS)
                          ->remember('featured:products', self::CACHE_TTL, function () {
            return Product::where('featured', true)
                         ->where('status', ProductStatus::ACTIVE)
                         ->with(['category:id,name'])
                         ->take(10)
                         ->get();
        });
    }
    
    public function getProductsByCategory(int $categoryId): Collection
    {
        $cacheKey = "category:{$categoryId}:products";
        
        return $this->cache->tags(self::CACHE_TAGS)
                          ->remember($cacheKey, self::CACHE_TTL, function () use ($categoryId) {
            return Product::where('category_id', $categoryId)
                         ->where('status', ProductStatus::ACTIVE)
                         ->orderBy('created_at', 'desc')
                         ->get();
        });
    }
    
    public function clearProductCache(?int $productId = null): void
    {
        if ($productId) {
            $this->cache->tags(self::CACHE_TAGS)->forget("product:{$productId}");
        } else {
            $this->cache->tags(self::CACHE_TAGS)->flush();
        }
    }
    
    public function clearAllProductCaches(): void
    {
        $this->cache->tags(self::CACHE_TAGS)->flush();
    }
}
```

### Modern Security Patterns

#### Laravel 11 Authentication
```php
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Auth\AuthenticationException;

class ApiAuthController extends Controller
{
    public function __construct()
    {
        $this->middleware('auth:api')->except(['login', 'refresh']);
    }
    
    public function me(Request $request): \Illuminate\Http\JsonResponse
    {
        try {
            $user = Auth::userOrFail();
            return response()->json([
                'success' => true,
                'data' => $user
            ]);
        } catch (AuthenticationException $e) {
            return response()->json([
                'success' => false,
                'message' => 'Unauthenticated'
            ], 401);
        }
    }
    
    public function login(Request $request): \Illuminate\Http\JsonResponse
    {
        $credentials = $request->validate([
            'email' => 'required|email',
            'password' => 'required|string',
        ]);
        
        if (!$token = Auth::attempt($credentials)) {
            return response()->json([
                'success' => false,
                'message' => 'Invalid credentials'
            ], 401);
        }
        
        return response()->json([
            'success' => true,
            'data' => [
                'access_token' => $token,
                'token_type' => 'bearer',
                'expires_in' => auth()->factory()->getTTL() * 60
            ]
        ]);
    }
}
```

#### Modern Rate Limiting
```php
// RouteServiceProvider.php
Route::middleware(['auth', 'throttle:api'])->group(function () {
    Route::get('/api/products', [ProductController::class, 'index']);
    Route::post('/api/products', [ProductController::class, 'store']);
    Route::put('/api/products/{product}', [ProductController::class, 'update']);
});

// Custom throttle configuration
Route::middleware(['throttle:10,1'])->group(function () {
    Route::post('/api/bulk/products', [ProductController::class, 'bulkStore']);
    Route::post('/api/products/import', [ProductController::class, 'import']);
});
```

## v14 Modern Checklist

When developing with Laravel 11:

- [ ] Use PHP 8.3+ with full type declarations
- [ ] Implement readonly properties where appropriate
- [ ] Use modern Laravel 11 features (ULID, new casts)
- [ ] Implement Vue 3 composition API components
- [ ] Use PHPUnit 10 with attributes
- [ ] Implement modern caching with tags
- [ ] Use enum casts for status fields
- [ ] Implement proper rate limiting
- [ ] Use Tailwind CSS for styling
- [ ] Follow modern testing patterns
- [ ] Implement proper error handling
- [ ] Use dependency injection
- [ ] Implement repository pattern
- [ ] Use modern migration syntax

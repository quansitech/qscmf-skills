> This file extends [../../../rules/common/patterns.md](../../../rules/common/patterns.md) with QSMCF-specific model patterns.

# GyListModel Patterns for QSMCF

This document provides comprehensive patterns for developing models in QSMCF using the `GyListModel` base class with enhanced features and modern PHP practices.

## GyListModel with Modern Features

### Enhanced GyListModel Implementation

```php
use Gy_Library\DBCont;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Database\Eloquent\Builder;

class Product extends GyListModel
{
    use SoftDeletes;
    
    protected $table = 'products';
    protected $primaryKey = 'id';
    
    protected $fillable = [
        'name', 
        'description', 
        'price', 
        'stock', 
        'status',
        'category_id',
        'supplier_id',
        'image_url',
        'metadata'
    ];
    
    protected $casts = [
        'price' => 'decimal:2',
        'stock' => 'integer',
        'status' => 'string',
        'metadata' => 'array',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
        'deleted_at' => 'datetime'
    ];
    
    // Constants for status
    public const STATUS_ACTIVE = 'active';
    public const STATUS_INACTIVE = 'inactive';
    public const STATUS_OUT_OF_STOCK = 'out_of_stock';
    
    // Scopes
    public function scopeActive(Builder $query): Builder
    {
        return $query->where('status', self::STATUS_ACTIVE);
    }
    
    public function scopeInStock(Builder $query): Builder
    {
        return $query->where('stock', '>', 0);
    }
    
    public function scopeByCategory(Builder $query, int $categoryId): Builder
    {
        return $query->where('category_id', $categoryId);
    }
    
    // Relationships
    public function category()
    {
        return $this->belongsTo(Category::class, 'category_id');
    }
    
    public function supplier()
    {
        return $this->belongsTo(Supplier::class, 'supplier_id');
    }
    
    public function reviews()
    {
        return $this->hasMany(Review::class);
    }
    
    public function orderItems()
    {
        return $this->hasMany(OrderItem::class);
    }
    
    // Accessors
    public function getFormattedPriceAttribute(): string
    {
        return '¥' . number_format($this->price, 2);
    }
    
    public function getStockStatusAttribute(): string
    {
        if ($this->stock === 0) {
            return 'out_of_stock';
        }
        
        if ($this->stock < 10) {
            return 'low_stock';
        }
        
        return 'in_stock';
    }
    
    public function getImageUrlAttribute(?string $value): ?string
    {
        return $value ? asset('storage/' . $value) : null;
    }
    
    // Mutators
    public function setPriceAttribute($value): void
    {
        $this->attributes['price'] = (float) $value;
    }
    
    public function setStockAttribute($value): void
    {
        $this->attributes['stock'] = max(0, (int) $value);
    }
    
    // Custom methods
    public function isAvailable(): bool
    {
        return $this->status === self::STATUS_ACTIVE && $this->stock > 0;
    }
    
    public function getRating(): float
    {
        if ($this->reviews()->count() === 0) {
            return 0;
        }
        
        return $this->reviews()->avg('rating');
    }
    
    public function updateStock(int $quantity): void
    {
        $this->stock += $quantity;
        $this->save();
    }
    
    public function canBeDeleted(): bool
    {
        // Check if product has been ordered
        if ($this->orderItems()->exists()) {
            return false;
        }
        
        // Check if product has pending reviews
        if ($this->reviews()->where('status', 'pending')->exists()) {
            return false;
        }
        
        return true;
    }
    
    // Static methods for common operations
    public static function getActiveProducts(): Collection
    {
        return self::active()->inStock()->get();
    }
    
    public static function getTopSelling(int $limit = 10): Collection
    {
        return self::withCount('orderItems')
                   ->orderBy('order_items_count', 'desc')
                   ->take($limit)
                   ->get();
    }
    
    // GyListModel specific methods
    protected function getListFields(): array
    {
        return [
            'id' => ['title' => 'ID', 'width' => 80, 'fixed' => 'left'],
            'name' => ['title' => 'Name', 'minWidth' => 120, 'searchable' => true],
            'category.name' => ['title' => 'Category', 'width' => 100],
            'price' => ['title' => 'Price', 'type' => 'money', 'width' => 120],
            'stock' => ['title' => 'Stock', 'width' => 100, 'sortable' => true],
            'status' => [
                'title' => 'Status', 
                'width' => 100,
                'type' => 'select',
                'options' => [
                    self::STATUS_ACTIVE => 'Active',
                    self::STATUS_INACTIVE => 'Inactive',
                    self::STATUS_OUT_OF_STOCK => 'Out of Stock'
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
                'rules' => 'required|string|max:255',
                'placeholder' => 'Enter product name'
            ],
            'description' => [
                'label' => 'Description',
                'type' => 'textarea',
                'rules' => 'nullable|string',
                'rows' => 4
            ],
            'price' => [
                'label' => 'Price',
                'type' => 'number',
                'rules' => 'required|numeric|min:0',
                'step' => '0.01',
                'prefix' => '¥'
            ],
            'stock' => [
                'label' => 'Stock Quantity',
                'type' => 'number',
                'rules' => 'required|integer|min:0',
                'placeholder' => 'Enter stock quantity'
            ],
            'category_id' => [
                'label' => 'Category',
                'type' => 'select',
                'rules' => 'required|exists:categories,id',
                'options' => Category::pluck('name', 'id')->toArray(),
                'placeholder' => 'Select category'
            ],
            'supplier_id' => [
                'label' => 'Supplier',
                'type' => 'select',
                'rules' => 'nullable|exists:suppliers,id',
                'options' => Supplier::pluck('name', 'id')->toArray(),
                'placeholder' => 'Select supplier'
            ],
            'status' => [
                'label' => 'Status',
                'type' => 'radio',
                'rules' => 'required|string',
                'options' => [
                    self::STATUS_ACTIVE => 'Active',
                    self::STATUS_INACTIVE => 'Inactive'
                ],
                'default' => self::STATUS_ACTIVE
            ],
            'image_url' => [
                'label' => 'Product Image',
                'type' => 'image',
                'rules' => 'nullable|image|max:2048',
                'help' => 'Upload product image (max 2MB)'
            ],
            'metadata' => [
                'label' => 'Additional Info',
                'type' => 'json',
                'rules' => 'nullable|array',
                'help' => 'JSON format additional product information'
            ]
        ];
    }
    
    protected function getValidationRules(): array
    {
        return [
            'create' => [
                'name' => 'required|string|max:255',
                'price' => 'required|numeric|min:0',
                'stock' => 'required|integer|min:0',
                'category_id' => 'required|exists:categories,id',
                'status' => 'required|in:' . implode(',', [self::STATUS_ACTIVE, self::STATUS_INACTIVE])
            ],
            'update' => [
                'name' => 'sometimes|required|string|max:255',
                'price' => 'sometimes|required|numeric|min:0',
                'stock' => 'sometimes|required|integer|min:0',
                'status' => 'sometimes|required|in:' . implode(',', [self::STATUS_ACTIVE, self::STATUS_INACTIVE])
            ]
        ];
    }
    
    protected function customizeQuery(Builder $query): Builder
    {
        // Eager load relationships
        $query->with(['category', 'supplier']);
        
        // Apply search
        if (request()->has('search')) {
            $search = request()->search;
            $query->where(function($q) use ($search) {
                $q->where('name', 'like', "%{$search}%")
                  ->orWhere('description', 'like', "%{$search}%");
            });
        }
        
        // Apply status filter
        if (request()->has('status')) {
            $query->where('status', request()->status);
        }
        
        // Apply category filter
        if (request()->has('category_id')) {
            $query->where('category_id', request()->category_id);
        }
        
        // Sort by creation date by default
        $query->orderBy('created_at', 'desc');
        
        return $query;
    }
    
    protected function afterSave(array $data): void
    {
        // Log product creation/update
        Log::info('Product saved', [
            'product_id' => $this->id,
            'user_id' => auth()->id(),
            'action' => $this->wasRecentlyCreated ? 'created' : 'updated'
        ]);
        
        // Clear cache if needed
        Cache::tags(['products'])->flush();
    }
    
    protected function afterDelete(): void
    {
        // Delete related images
        if ($this->image_url) {
            Storage::delete($this->image_url);
        }
        
        // Log deletion
        Log::info('Product deleted', [
            'product_id' => $this->id,
            'user_id' => auth()->id()
        ]);
    }
}
```

## Repository Pattern Integration

### ProductRepository with GyListModel

```php
interface ProductRepositoryInterface
{
    public function find(int $id): ?Product;
    public function all(): Collection;
    public function paginate(int $perPage = 15): LengthAwarePaginator;
    public function create(array $data): Product;
    public function update(Product $product, array $data): Product;
    public function delete(Product $product): bool;
    public function search(string $query): Collection;
    public function getActiveProducts(): Collection;
    public function getProductsByCategory(int $categoryId): Collection;
}

class ProductRepository implements ProductRepositoryInterface
{
    protected $model;
    
    public function __construct(Product $model)
    {
        $this->model = $model;
    }
    
    public function find(int $id): ?Product
    {
        return Cache::remember("product:{$id}", now()->addHours(6), function () use ($id) {
            return $this->model->with(['category', 'supplier'])->find($id);
        });
    }
    
    public function all(): Collection
    {
        return $this->model->orderBy('created_at', 'desc')->get();
    }
    
    public function paginate(int $perPage = 15): LengthAwarePaginator
    {
        return $this->model->with(['category', 'supplier'])
                          ->orderBy('created_at', 'desc')
                          ->paginate($perPage);
    }
    
    public function create(array $data): Product
    {
        $product = $this->model->create($data);
        
        // Sync relationships
        if (isset($data['category_id'])) {
            $product->category()->associate($data['category_id']);
        }
        
        if (isset($data['supplier_id'])) {
            $product->supplier()->associate($data['supplier_id']);
        }
        
        $product->save();
        
        return $product;
    }
    
    public function update(Product $product, array $data): Product
    {
        $product->update($data);
        
        // Update relationships
        if (isset($data['category_id'])) {
            $product->category()->associate($data['category_id']);
        }
        
        if (isset($data['supplier_id'])) {
            $product->supplier()->associate($data['supplier_id']);
        }
        
        $product->save();
        
        return $product;
    }
    
    public function delete(Product $product): bool
    {
        if (!$product->canBeDeleted()) {
            throw new \Exception('Cannot delete product with orders or pending reviews');
        }
        
        return $product->delete();
    }
    
    public function search(string $query): Collection
    {
        return $this->model->where('name', 'like', "%{$query}%")
                          ->orWhere('description', 'like', "%{$query}%")
                          ->get();
    }
    
    public function getActiveProducts(): Collection
    {
        return Cache::remember('active:products', now()->addHours(1), function () {
            return $this->model->active()->inStock()->get();
        });
    }
    
    public function getProductsByCategory(int $categoryId): Collection
    {
        return $this->model->byCategory($categoryId)->get();
    }
}
```

## Model Validation and Business Rules

### Enhanced Validation Rules

```php
class Product extends GyListModel
{
    protected $rules = [
        'name' => 'required|string|max:255|unique:products,name',
        'price' => 'required|numeric|min:0|max:999999.99',
        'stock' => 'required|integer|min:0|max:999999',
        'category_id' => 'required|exists:categories,id',
        'supplier_id' => 'nullable|exists:suppliers,id',
        'status' => 'required|string|in:active,inactive,out_of_stock',
        'image_url' => 'nullable|image|max:2048|mimes:jpeg,png,jpg,gif'
    ];
    
    protected $messages = [
        'name.required' => 'Product name is required',
        'name.unique' => 'Product name already exists',
        'price.required' => 'Price is required',
        'price.min' => 'Price must be greater than 0',
        'stock.required' => 'Stock quantity is required',
        'category_id.required' => 'Category is required',
        'status.required' => 'Status is required'
    ];
    
    // Model-level business rules
    protected function validateStock(int $quantity): bool
    {
        // Check if stock is sufficient
        if ($quantity > $this->stock) {
            throw new \Exception('Insufficient stock available');
        }
        
        return true;
    }
    
    protected function validatePrice(float $price): bool
    {
        // Check if price is reasonable
        if ($price < 0.01) {
            throw new \Exception('Price must be at least 0.01');
        }
        
        if ($price > 999999.99) {
            throw new \Exception('Price cannot exceed 999999.99');
        }
        
        return true;
    }
    
    protected function validateStatus(string $status): bool
    {
        $allowedStatuses = [self::STATUS_ACTIVE, self::STATUS_INACTIVE, self::STATUS_OUT_OF_STOCK];
        
        if (!in_array($status, $allowedStatuses)) {
            throw new \Exception('Invalid status provided');
        }
        
        return true;
    }
}
```

### Model Events

```php
class Product extends GyListModel
{
    // Register model events
    protected static function boot()
    {
        parent::boot();
        
        // When creating a product
        static::creating(function ($product) {
            // Set default status if not provided
            if (!$product->status) {
                $product->status = self::STATUS_ACTIVE;
            }
            
            // Set user ID if authenticated
            if (auth()->check()) {
                $product->created_by = auth()->id();
                $product->updated_by = auth()->id();
            }
        });
        
        // When updating a product
        static::updating(function ($product) {
            // Update updated_by if authenticated
            if (auth()->check()) {
                $product->updated_by = auth()->id();
            }
            
            // Check if stock changes affect status
            if ($product->isDirty('stock')) {
                if ($product->stock === 0) {
                    $product->status = self::STATUS_OUT_OF_STOCK;
                } elseif ($product->stock > 0 && $product->status === self::STATUS_OUT_OF_STOCK) {
                    $product->status = self::STATUS_ACTIVE;
                }
            }
        });
        
        // When deleting a product
        static::deleting(function ($product) {
            // Soft delete children
            $product->reviews()->delete();
            $product->orderItems()->delete();
        });
    }
}
```

## Testing Models

### Model Unit Testing

```php
class ProductTest extends TestCase
{
    use RefreshDatabase;
    
    protected $product;
    protected $category;
    
    protected function setUp(): void
    {
        parent::setUp();
        $this->category = Category::factory()->create();
        $this->product = Product::factory()->create(['category_id' => $this->category->id]);
    }
    
    public function test_product_belongs_to_category()
    {
        $this->assertInstanceOf(Category::class, $this->product->category);
        $this->assertEquals($this->category->id, $this->product->category_id);
    }
    
    public function test_product_has_formatted_price_accessor()
    {
        $this->product->price = 99.99;
        $this->assertEquals('¥99.99', $this->product->formatted_price);
    }
    
    public function test_product_scope_active()
    {
        Product::factory()->create(['status' => 'inactive']);
        $activeProducts = Product::active()->get();
        
        $this->assertCount(1, $activeProducts);
        $this->assertEquals('active', $activeProducts->first()->status);
    }
    
    public function test_product_is_available_method()
    {
        $activeProduct = Product::factory()->create([
            'status' => 'active',
            'stock' => 10
        ]);
        
        $inactiveProduct = Product::factory()->create([
            'status' => 'inactive'
        ]);
        
        $outOfStockProduct = Product::factory()->create([
            'status' => 'active',
            'stock' => 0
        ]);
        
        $this->assertTrue($activeProduct->isAvailable());
        $this->assertFalse($inactiveProduct->isAvailable());
        $this->assertFalse($outOfStockProduct->isAvailable());
    }
    
    public function test_product_validation()
    {
        // Test valid product
        $validProduct = Product::factory()->make();
        $this->assertTrue($validProduct->validate());
        
        // Test invalid product (no name)
        $invalidProduct = Product::factory()->make(['name' => null]);
        $this->assertFalse($invalidProduct->validate());
    }
}
```

### Feature Testing

```php
class ProductModelTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        $this->actingAs(User::factory()->create());
    }
    
    public function test_can_create_product()
    {
        $category = Category::factory()->create();
        
        $productData = [
            'name' => 'Test Product',
            'price' => 99.99,
            'stock' => 50,
            'category_id' => $category->id,
            'status' => Product::STATUS_ACTIVE
        ];
        
        $product = Product::create($productData);
        
        $this->assertDatabaseHas('products', $productData);
        $this->assertEquals('Test Product', $product->name);
        $this->assertEquals($category->id, $product->category_id);
    }
    
    public function test_can_update_product_stock()
    {
        $product = Product::factory()->create(['stock' => 10]);
        
        $product->updateStock(-5);
        
        $this->assertEquals(5, $product->fresh()->stock);
    }
    
    public function test_product_rating_calculation()
    {
        $product = Product::factory()->create();
        
        // Add reviews
        Review::factory()->create([
            'product_id' => $product->id,
            'rating' => 5
        ]);
        Review::factory()->create([
            'product_id' => $product->id,
            'rating' => 3
        ]);
        
        $this->assertEquals(4.0, $product->getRating());
    }
    
    public function test_caching_of_active_products()
    {
        Product::factory()->create(['status' => Product::STATUS_ACTIVE]);
        Product::factory()->create(['status' => Product::STATUS_INACTIVE]);
        
        $activeProducts = Product::getActiveProducts();
        
        $this->assertCount(1, $activeProducts);
        $this->assertEquals('active', $activeProducts->first()->status);
    }
}
```

## Performance Optimization

### Model Performance Patterns

```php
class Product extends GyListModel
{
    // Select specific columns for list queries
    protected $listColumns = [
        'id', 'name', 'price', 'stock', 
        'category_id', 'status', 'created_at'
    ];
    
    // Default order
    protected $defaultOrder = ['created_at' => 'desc'];
    
    // Indexes
    protected function getIndexes(): array
    {
        return [
            ['columns' => ['category_id', 'status']],
            ['columns' => ['status', 'stock']],
            ['columns' => ['name'], 'type' => 'fulltext']
        ];
    }
    
    // Efficient pagination
    public function getPaginatedList(int $perPage = 15): LengthAwarePaginator
    {
        return $this->query()
            ->select($this->listColumns)
            ->with(['category:id,name'])
            ->when(request()->has('search'), function ($query) {
                $query->where(function($q) {
                    $q->where('name', 'like', '%' . request()->search . '%')
                      ->orWhere('description', 'like', '%' . request()->search . '%');
                });
            })
            ->when(request()->has('category_id'), function ($query) {
                $query->where('category_id', request()->category_id);
            })
            ->orderBy($this->defaultOrder['column'], $this->defaultOrder['direction'])
            ->paginate($perPage);
    }
    
    // Bulk operations
    public function bulkUpdateStatus(array $ids, string $status): int
    {
        return $this->whereIn('id', $ids)
                   ->update(['status' => $status]);
    }
    
    public function bulkUpdateStock(array $idStockPairs): int
    {
        $ids = array_keys($idStockPairs);
        $stockValues = array_values($idStockPairs);
        
        return $this->whereIn('id', $ids)
                   ->update(['stock' => $stockValues]);
    }
}
```

### Caching Strategies

```php
class Product extends GyListModel
{
    // Cache configuration
    protected $cacheTags = ['products'];
    protected $cacheTTL = 3600; // 1 hour
    
    // Cached relationships
    public function getCategoryCached()
    {
        return Cache::remember(
            "category:{$this->category_id}",
            $this->cacheTTL,
            function () {
                return $this->category;
            }
        );
    }
    
    // Clear cache on updates
    public function save(array $options = [])
    {
        $result = parent::save($options);
        
        if ($result) {
            Cache::tags($this->cacheTags)->flush();
        }
        
        return $result;
    }
    
    // Cached popular products
    public static function getPopularProducts(int $limit = 10): Collection
    {
        return Cache::remember(
            'popular:products:' . $limit,
            now()->addHours(1),
            function () use ($limit) {
                return Product::withCount('orderItems')
                           ->orderBy('order_items_count', 'desc')
                           ->limit($limit)
                           ->get();
            }
        );
    }
}
```

## Advanced Model Patterns

### Polymorphic Relationships

```php
class Image extends GyListModel
{
    public function imageable()
    {
        return $this->morphTo();
    }
}

class Product extends GyListModel
{
    public function images()
    {
        return $this->morphMany(Image::class, 'imageable');
    }
}

// Usage
$product = Product::find(1);
$image = new Image(['url' => 'path/to/image.jpg']);
$product->images()->save($image);
```

### Multi-tenant Models

```php
class Product extends GyListModel
{
    protected $tenantColumn = 'tenant_id';
    
    public function tenant()
    {
        return $this->belongsTo(Tenant::class, 'tenant_id');
    }
    
    public static function boot()
    {
        parent::boot();
        
        // Automatically set tenant
        static::creating(function ($product) {
            if (app()->has('tenant')) {
                $product->tenant_id = app('tenant')->id;
            }
        });
        
        // Only show products for current tenant
        static::addGlobalScope('tenant', function ($query) {
            if (app()->has('tenant')) {
                $query->where('tenant_id', app('tenant')->id);
            }
        });
    }
}
```

### Versionable Models

```php
class ProductVersion extends GyListModel
{
    protected $fillable = [
        'product_id', 'version', 'data', 'change_description'
    ];
    
    public function product()
    {
        return $this->belongsTo(Product::class);
    }
}

class Product extends GyListModel
{
    protected $fillable = [
        'name', 'description', 'price', 'data'
    ];
    
    public function versions()
    {
        return $this->hasMany(ProductVersion::class);
    }
    
    public function newVersion(string $changeDescription = ''): ProductVersion
    {
        $version = $this->versions()->create([
            'version' => $this->versions()->count() + 1,
            'data' => $this->toArray(),
            'change_description' => $changeDescription
        ]);
        
        return $version;
    }
}
```

## Best Practices

1. **Use type hints** - Be explicit about return types
2. **Follow naming conventions** - Use snake_case for attributes
3. **Implement proper validation** - Use Laravel validation rules
4. **Use soft deletes** - For recoverable data
5. **Cache frequently accessed data** - Improve performance
6. **Use scopes** - For common query patterns
7. **Implement accessors/mutators** - For computed properties
8. **Use repository pattern** - For complex business logic
9. **Model events** - For side effects
10. **Test thoroughly** - Ensure model behavior is correct

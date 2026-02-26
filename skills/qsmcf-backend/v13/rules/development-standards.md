> This file extends [../../_shared/references/development-standards.md](../../_shared/references/development-standards.md) with v13-specific patterns for Laravel 9/10 and PHP 8.1+.

# Laravel 9/10 Development Standards for QSMCF v13

This document provides version-specific development standards for QSMCF v13, built on Laravel 9/10 with PHP 8.1+ support.

## v13 Specific Configuration

### Laravel 9/10 Application Structure

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
│   └── Middleware/
├── Models/
│   ├── Product.php
│   └── User.php
├── Repositories/
├── Services/
└── Providers/
├── database/
│   ├── migrations/
│   └── seeds/
├── resources/
│   ├── views/
│   │   ├── admin/
│   │   └── api/
│   └── lang/
├── routes/
│   ├── api.php
│   ├── web.php
│   └── admin.php
├── config/
├── public/
└── tests/
```

### Laravel 9/10 Service Providers

```php
// app/Providers/AppServiceProvider.php
namespace App\Providers;

use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\View;
use App\Models\Category;

class AppServiceProvider extends ServiceProvider
{
    public function register()
    {
        //
    }

    public function boot()
    {
        // Share categories with all views
        View::share('categories', Category::active()->get());
        
        // Custom validation rule
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

### Laravel 9/10 Authentication Guards

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
        'admin' => [
            'driver' => 'session',
            'provider' => 'admins',
        ],
        'api' => [
            'driver' => 'token',
            'provider' => 'users',
            'hash' => false,
        ],
    ],

    'providers' => [
        'users' => [
            'driver' => 'eloquent',
            'model' => App\Models\User::class,
        ],
        'admins' => [
            'driver' => 'eloquent',
            'model' => App\Models\Admin::class,
        ],
    ],
];
```

## v13 Development Patterns

### Controllers with Laravel 9/10 Features

#### Admin Controller with Type Hints (Partial)
```php
namespace App\Http\Controllers\Admin;

use App\Http\Controllers\BaseAdminController;
use App\Models\Product;
use App\ListBuilders\ProductListBuilder;
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
    
    public function update(UpdateProductRequest $request, $id)
    {
        $product = Product::findOrFail($id);
        
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

#### API Controller with Laravel 9/10 Features
```php
namespace App\Http\Controllers\Api;

use App\Http\Controllers\BaseApiController;
use App\Models\Product;
use App\Http\Resources\ProductResource;
use Illuminate\Http\Request;

class ProductApiController extends BaseApiController
{
    protected $model = Product::class;
    protected $resourceClass = ProductResource::class;
    
    // Partial type declarations
    public function index(Request $request)
    {
        $query = $this->model::query();
        
        // Apply filters
        if ($request->has('category_id')) {
            $query->where('category_id', $request->category_id);
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
        
        return ProductResource::collection($products);
    }
    
    // Feature collections
    public function featured()
    {
        $products = Product::where('featured', true)
                          ->where('status', 'active')
                          ->take(10)
                          ->get();
        
        return ProductResource::collection($products);
    }
    
    // Bulk operations
    public function bulkUpdate(Request $request)
    {
        $validated = $request->validate([
            'ids' => 'required|array',
            'ids.*' => 'integer|exists:products,id',
            'status' => 'required|string|in:active,inactive'
        ]);
        
        Product::whereIn('id', $validated['ids'])
              ->update(['status' => $validated['status']]);
        
        return response()->json([
            'success' => true,
            'message' => 'Products updated successfully',
            'updated' => count($validated['ids'])
        ]);
    }
}
```

### Laravel 9/10 Blade Templates

#### Admin Template with jQuery
```blade
@extends('layouts.admin')

@section('content')
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4 class="card-title mb-0">Products Management</h4>
                    <button class="btn btn-primary" onclick="showCreateModal()">
                        <i class="fa fa-plus"></i> Add Product
                    </button>
                </div>
                
                <div class="card-body">
                    <!-- Search and Filter -->
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <div class="input-group">
                                <input type="text" class="form-control" id="searchInput" 
                                       placeholder="Search products...">
                                <div class="input-group-append">
                                    <button class="btn btn-outline-secondary" type="button" 
                                            onclick="searchProducts()">
                                        <i class="fa fa-search"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <select class="form-control" id="categoryFilter" 
                                    onchange="filterByCategory()">
                                <option value="">All Categories</option>
                                @foreach($categories as $category)
                                <option value="{{ $category->id }}">{{ $category->name }}</option>
                                @endforeach
                            </select>
                        </div>
                        <div class="col-md-3">
                            <select class="form-control" id="statusFilter" 
                                    onchange="filterByStatus()">
                                <option value="">All Status</option>
                                <option value="active">Active</option>
                                <option value="inactive">Inactive</option>
                            </select>
                        </div>
                        <div class="col-md-2">
                            <button class="btn btn-success btn-block" 
                                    onclick="exportProducts()">
                                <i class="fa fa-download"></i> Export
                            </button>
                        </div>
                    </div>
                    
                    <!-- Data Table -->
                    <div class="table-responsive">
                        <table class="table table-striped table-hover" id="productsTable">
                            <thead>
                                <tr>
                                    <th width="50">
                                        <input type="checkbox" id="selectAll" 
                                               onchange="toggleSelectAll()">
                                    </th>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Category</th>
                                    <th>Price</th>
                                    <th>Stock</th>
                                    <th>Status</th>
                                    <th width="200">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($products as $product)
                                <tr>
                                    <td>
                                        <input type="checkbox" name="product_ids[]" 
                                               value="{{ $product->id }}">
                                    </td>
                                    <td>{{ $product->id }}</td>
                                    <td>{{ $product->name }}</td>
                                    <td>{{ $product->category->name ?? '-' }}</td>
                                    <td>¥{{ number_format($product->price, 2) }}</td>
                                    <td>{{ $product->stock }}</td>
                                    <td>
                                        <span class="badge {{ $product->status == 'active' ? 'bg-success' : 'bg-secondary' }}">
                                            {{ ucfirst($product->status) }}
                                        </span>
                                    </td>
                                    <td>
                                        <button class="btn btn-sm btn-info" 
                                                onclick="editProduct({{ $product->id }})">
                                            <i class="fa fa-edit"></i>
                                        </button>
                                        <button class="btn btn-sm btn-danger" 
                                                onclick="deleteProduct({{ $product->id }})">
                                            <i class="fa fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Pagination -->
                    {{ $products->links() }}
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Product Modal -->
<div class="modal fade" id="productModal" tabindex="-1" role="dialog">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="modalTitle">Add Product</h5>
                <button type="button" class="close" data-dismiss="modal">
                    <span>&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <form id="productForm" enctype="multipart/form-data">
                    @csrf
                    <input type="hidden" id="productId" name="id">
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="name">Product Name</label>
                                <input type="text" class="form-control" id="name" 
                                       name="name" required>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="category_id">Category</label>
                                <select class="form-control" id="category_id" 
                                        name="category_id" required>
                                    <option value="">Select Category</option>
                                    @foreach($categories as $category)
                                    <option value="{{ $category->id }}">{{ $category->name }}</option>
                                    @endforeach
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-group">
                                <label for="price">Price</label>
                                <input type="number" class="form-control" id="price" 
                                       name="price" step="0.01" min="0" required>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-group">
                                <label for="stock">Stock</label>
                                <input type="number" class="form-control" id="stock" 
                                       name="stock" min="0" required>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-group">
                                <label for="status">Status</label>
                                <select class="form-control" id="status" name="status" required>
                                    <option value="active">Active</option>
                                    <option value="inactive">Inactive</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="description">Description</label>
                        <textarea class="form-control" id="description" name="description" 
                                  rows="4"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="image">Product Image</label>
                        <input type="file" class="form-control-file" id="image" 
                               name="image" accept="image/*">
                        <small class="form-text text-muted">
                            Allowed formats: JPG, PNG, GIF. Max size: 2MB.
                        </small>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">
                    Cancel
                </button>
                <button type="button" class="btn btn-primary" onclick="saveProduct()">
                    Save
                </button>
            </div>
        </div>
    </div>
</div>

<!-- Bulk Actions Modal -->
<div class="modal fade" id="bulkModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Bulk Actions</h5>
                <button type="button" class="close" data-dismiss="modal">
                    <span>&times;</span>
                </button>
            </div>
            <div class="modal-body">
                <p>Selected {{ count($selected) }} products</p>
                <div class="form-group">
                    <label>Action</label>
                    <select class="form-control" id="bulkAction">
                        <option value="">Select Action</option>
                        <option value="activate">Activate</option>
                        <option value="deactivate">Deactivate</option>
                        <option value="delete">Delete</option>
                    </select>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">
                    Cancel
                </button>
                <button type="button" class="btn btn-primary" onclick="executeBulkAction()">
                    Execute
                </button>
            </div>
        </div>
    </div>
</div>
@endsection

@push('styles')
<style>
.table-responsive {
    margin-top: 20px;
}
.modal-lg {
    max-width: 800px;
}
</style>
@endpush

@push('scripts')
<script>
// Global variables
let currentProductId = null;
let currentAction = 'create';

// Modal functions
function showCreateModal() {
    currentAction = 'create';
    currentProductId = null;
    $('#modalTitle').text('Add Product');
    $('#productForm')[0].reset();
    $('#productModal').modal('show');
}

function editProduct(id) {
    currentAction = 'update';
    currentProductId = id;
    $('#modalTitle').text('Edit Product');
    
    // Load product data
    $.get('/api/products/' + id, function(data) {
        $('#id').val(data.data.id);
        $('#name').val(data.data.name);
        $('#category_id').val(data.data.category_id);
        $('#price').val(data.data.price);
        $('#stock').val(data.data.stock);
        $('#status').val(data.data.status);
        $('#description').val(data.data.description);
        
        if (data.data.image) {
            $('#imagePreview').html('<img src="/storage/' + data.data.image + 
                                  '" class="img-thumbnail" width="100">');
        }
        
        $('#productModal').modal('show');
    });
}

function deleteProduct(id) {
    if (confirm('Are you sure you want to delete this product?')) {
        $.ajax({
            url: '/api/products/' + id,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    alert('Product deleted successfully');
                    window.location.reload();
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr) {
                alert('Error: ' + xhr.responseText);
            }
        });
    }
}

function saveProduct() {
    const formData = new FormData($('#productForm')[0]);
    
    $.ajax({
        url: currentAction === 'create' ? '/api/products' : '/api/products/' + currentProductId,
        method: currentAction === 'create' ? 'POST' : 'PUT',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.success) {
                alert('Product saved successfully');
                $('#productModal').modal('hide');
                window.location.reload();
            } else {
                alert('Error: ' + response.message);
            }
        },
        error: function(xhr) {
            alert('Error: ' + xhr.responseText);
        }
    });
}

// Search functions
function searchProducts() {
    const searchTerm = $('#searchInput').val();
    const categoryId = $('#categoryFilter').val();
    const status = $('#statusFilter').val();
    
    window.location.href = '/admin/products?' +
        'search=' + searchTerm +
        '&category_id=' + categoryId +
        '&status=' + status;
}

function filterByCategory() {
    searchProducts();
}

function filterByStatus() {
    searchProducts();
}

// Export function
function exportProducts() {
    window.location.href = '/admin/products/export?' +
        'search=' + $('#searchInput').val() +
        '&category_id=' + $('#categoryFilter').val() +
        '&status=' + $('#statusFilter').val();
}

// Bulk actions
$('#selectAll').change(function() {
    $('input[name="product_ids[]"]').prop('checked', this.checked);
});

function toggleSelectAll() {
    const selectAll = $('#selectAll').prop('checked');
    $('input[name="product_ids[]"]').prop('checked', selectAll);
    
    if (selectAll) {
        $('#bulkModal').modal('show');
    }
}

function executeBulkAction() {
    const selectedIds = [];
    $('input[name="product_ids[]"]:checked').each(function() {
        selectedIds.push($(this).val());
    });
    
    const action = $('#bulkAction').val();
    
    if (!action) {
        alert('Please select an action');
        return;
    }
    
    if (confirm('Are you sure you want to ' + action + ' selected products?')) {
        $.ajax({
            url: '/api/products/bulk',
            method: 'POST',
            data: {
                ids: selectedIds,
                action: action
            },
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    window.location.reload();
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr) {
                alert('Error: ' + xhr.responseText);
            }
        });
    }
}

// Image preview
$('#image').change(function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            $('#imagePreview').html('<img src="' + e.target.result + 
                                  '" class="img-thumbnail" width="100">');
        };
        reader.readAsDataURL(file);
    }
});
</script>
@endpush
```

### v13 Database Patterns

#### Laravel 9/10 Migrations
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
            $table->text('description')->nullable();
            $table->decimal('price', 10, 2)->default(0);
            $table->integer('stock')->default(0);
            $table->boolean('status')->default(true);
            $table->unsignedInteger('category_id')->nullable();
            $table->string('image')->nullable();
            $table->timestamps();
            $table->softDeletes();
            
            // Foreign key
            $table->foreign('category_id')
                  ->references('id')
                  ->on('categories')
                  ->onDelete('set null');
            
            // Indexes
            $table->index('status');
            $table->index('category_id');
            $table->index(['status', 'stock']);
        });
    }
    
    public function down()
    {
        Schema::dropIfExists('products');
    }
};
```

#### Laravel 9/10 Model with Casts
```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Product extends Model
{
    use SoftDeletes;
    
    protected $fillable = [
        'name', 'description', 'price', 'stock', 
        'status', 'category_id', 'image'
    ];
    
    protected $casts = [
        'price' => 'decimal:2',
        'stock' => 'integer',
        'status' => 'boolean'
    ];
    
    // Relationships
    public function category()
    {
        return $this->belongsTo(Category::class);
    }
    
    // Accessors
    public function getFormattedPriceAttribute()
    {
        return '¥' . number_format($this->price, 2);
    }
    
    // Scopes
    public function scopeActive($query)
    {
        return $query->where('status', true);
    }
}
```

### v13 Testing Patterns

#### Feature Test with Laravel 9/10
```php
namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Product;
use App\Models\Category;

class ProductTest extends TestCase
{
    use RefreshDatabase;
    
    /** @test */
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
    }
    
    /** @test */
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
    
    /** @test */
    public function it_can_delete_product()
    {
        $product = Product::factory()->create();
        
        $response = $this->delete("/admin/products/{$product->id}");
        
        $response->assertRedirect('/admin/products');
        $this->assertDatabaseMissing('products', ['id' => $product->id]);
    }
    
    /** @test */
    public function it_validates_product_creation()
    {
        $response = $this->post('/admin/products', [
            'name' => '',
            'price' => -10
        ]);
        
        $response->assertSessionHasErrors(['name', 'price']);
    }
}
```

#### API Test with Laravel 9/10
```php
namespace Tests\Feature;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Models\Product;

class ProductApiTest extends TestCase
{
    use RefreshDatabase;
    
    /** @test */
    public function it_returns_product_list()
    {
        Product::factory(5)->create();
        
        $response = $this->get('/api/products');
        
        $response->assertStatus(200)
                ->assertJsonCount(5, 'data');
    }
    
    /** @test */
    public function it_searches_products()
    {
        Product::factory()->create(['name' => 'Test Product']);
        Product::factory()->create(['name' => 'Another Product']);
        
        $response = $this->get('/api/products?search=Test');
        
        $response->assertStatus(200)
                ->assertJsonCount(1, 'data');
    }
    
    /** @test */
    public function it_creates_product()
    {
        $productData = [
            'name' => 'New Product',
            'price' => 99.99,
            'stock' => 10
        ];
        
        $response = $this->post('/api/products', $productData);
        
        $response->assertStatus(201)
                ->assertJsonFragment(['name' => 'New Product']);
        
        $this->assertDatabaseHas('products', $productData);
    }
}
```

### v13 Performance Patterns

#### Query Optimization
```php
class ProductController extends Controller
{
    public function index(Request $request)
    {
        $query = Product::with(['category'])
                       ->select('id', 'name', 'price', 'category_id', 'status');
        
        // Add search
        if ($request->search) {
            $query->where(function($q) use ($request) {
                $q->where('name', 'like', "%{$request->search}%")
                  ->orWhere('description', 'like', "%{$request->search}%");
            });
        }
        
        // Add filters
        if ($request->category_id) {
            $query->where('category_id', $request->category_id);
        }
        
        if ($request->status !== null) {
            $query->where('status', $request->status);
        }
        
        // Add ordering
        if ($request->sort) {
            $query->orderBy($request->sort, $request->order ?? 'asc');
        }
        
        return $query->paginate($request->per_page ?? 15);
    }
}
```

#### Caching with Laravel 9/10
```php
class ProductController extends Controller
{
    public function index(Request $request)
    {
        $cacheKey = 'products:' . md5($request->url());
        $cacheTime = 60; // 1 minute
        
        return Cache::remember($cacheKey, $cacheTime, function() use ($request) {
            return $this->getFilteredProducts($request);
        });
    }
    
    public function featured()
    {
        return Cache::remember('featured:products', 3600, function() {
            return Product::where('featured', true)
                         ->where('status', true)
                         ->take(10)
                         ->get();
        });
    }
}
```

## v13 Upgrade Considerations

When upgrading to v14:

1. **PHP Version**: Upgrade to PHP 8.3+
2. **Laravel Version**: Upgrade to Laravel 11+
3. **Type Declarations**: Add full type declarations
4. **jQuery Components**: Migrate to Vue 3
5. **Blade Templates**: Update to modern syntax
6. **Testing**: Upgrade to PHPUnit 10
7. **Authentication**: Update to Laravel 11 auth patterns

### Migration Helper
```php
class MigrationHelper
{
    public static function checkVersionCompatibility()
    {
        return [
            'php_version' => version_compare(phpversion(), '8.3', '>='),
            'laravel_version' => version_compare(app()->version(), '11.0', '>='),
            'vue3_compatible' => config('app.vue3', false)
        ];
    }
}
```

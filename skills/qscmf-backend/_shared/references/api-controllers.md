> This file extends [../../../rules/common/patterns.md](../../../rules/common/patterns.md) with QSMCF-specific API controller patterns.

# RESTful API Controllers for QSMCF

This document provides comprehensive patterns for developing RESTful API controllers in QSMCF using the `RestController` base class and `ListBuilder` integration.

## Core Components

### QsListController with ListBuilder Integration

The `QsListController` is the base class for admin CRUD operations. When combined with `ListBuilder`, it provides powerful dynamic table functionality.

```php
class ProductController extends QsListController
{
    protected $model = Product::class;
    protected $resourceClass = ProductResource::class;
    
    protected $listConfig = [
        'default_field' => 'name',
        'table_fields' => [
            'id' => ['title' => 'ID', 'width' => 80],
            'name' => ['title' => 'Name', 'minWidth' => 120],
            'price' => ['title' => 'Price', 'type' => 'money'],
            'status' => ['title' => 'Status', 'type' => 'select'],
            'created_at' => ['title' => 'Created At', 'sorter' => true]
        ],
        'form_fields' => [
            'name' => ['label' => 'Product Name', 'rules' => 'required|max:255'],
            'price' => ['label' => 'Price', 'rules' => 'required|numeric|min:0'],
            'status' => ['label' => 'Status', 'type' => 'select', 'options' => [
                'active' => 'Active',
                'inactive' => 'Inactive'
            ]],
            'description' => ['label' => 'Description', 'type' => 'textarea']
        ],
        'search_fields' => ['name', 'description'],
        'filter_fields' => ['status']
    ];
    
    protected function customizeTableData($query)
    {
        $query->with(['category', 'supplier']);
        $query->where('user_id', auth()->id());
        
        if (request()->has('status_filter')) {
            $query->where('status', request()->status_filter);
        }
        
        return $query;
    }
}
```

### RestController for API Endpoints

The `RestController` provides a consistent API structure with proper response formatting.

```php
class ProductApiController extends RestController
{
    protected $model = Product::class;
    protected $resourceClass = ProductResource::class;
    
    protected $relationships = ['category', 'supplier'];
    protected $appends = ['formatted_price'];
    
    protected function listQuery()
    {
        $query = parent::listQuery();
        
        // Filter by user
        if (auth()->check()) {
            $query->where('user_id', auth()->id());
        }
        
        // Search support
        if (request()->has('search')) {
            $search = request()->search;
            $query->where(function($q) use ($search) {
                $q->where('name', 'like', "%{$search}%")
                  ->orWhere('description', 'like', "%{$search}%");
            });
        }
        
        return $query;
    }
    
    protected function customizeData($data)
    {
        // Add formatted data
        if (isset($data['price'])) {
            $data['formatted_price'] = '¥' . number_format($data['price'], 2);
        }
        
        return $data;
    }
    
    public function store(StoreProductRequest $request)
    {
        DB::beginTransaction();
        
        try {
            $product = $this->model::create([
                'name' => $request->name,
                'price' => $request->price,
                'description' => $request->description,
                'status' => $request->status ?? 'active',
                'user_id' => auth()->id()
            ]);
            
            // Handle category relationship
            if ($request->has('category_id')) {
                $product->category()->associate($request->category_id);
            }
            
            // Handle image upload
            if ($request->hasFile('image')) {
                $product->image = $request->file('image')->store('products');
            }
            
            $product->save();
            DB::commit();
            
            return $this->successResponse($product, 'Product created successfully');
            
        } catch (\Exception $e) {
            DB::rollBack();
            Log::error('Product creation failed', ['error' => $e->getMessage()]);
            
            return $this->errorResponse('Failed to create product', 500);
        }
    }
    
    public function update(UpdateProductRequest $request, $id)
    {
        $product = $this->model::findOrFail($id);
        
        if ($product->user_id !== auth()->id()) {
            return $this->errorResponse('Unauthorized', 403);
        }
        
        DB::beginTransaction();
        
        try {
            $product->update($request->validated());
            
            // Update relationships
            if ($request->has('category_id')) {
                $product->category()->associate($request->category_id);
            }
            
            // Handle image update
            if ($request->hasFile('image')) {
                // Delete old image if exists
                if ($product->image) {
                    Storage::delete($product->image);
                }
                $product->image = $request->file('image')->store('products');
            }
            
            $product->save();
            DB::commit();
            
            return $this->successResponse($product, 'Product updated successfully');
            
        } catch (\Exception $e) {
            DB::rollBack();
            Log::error('Product update failed', ['error' => $e->getMessage()]);
            
            return $this->errorResponse('Failed to update product', 500);
        }
    }
}
```

## Response Formatting

### Standard API Response Format

All API responses should follow a consistent format:

```php
// Success response
return $this->successResponse($data, 'Operation successful');

// Error response
return $this->errorResponse('Error message', $status_code);

// Paginated response
return $this->paginatedResponse($data, $pagination);

// Custom response format
return response()->json([
    'success' => true,
    'data' => $data,
    'message' => 'Success message',
    'meta' => [
        'timestamp' => now(),
        'request_id' => request()->header('X-Request-ID')
    ]
]);
```

### Response Types

```php
class RestController extends Controller
{
    /**
     * Success response with data
     */
    protected function successResponse($data = null, string $message = 'Success', int $status = 200)
    {
        return response()->json([
            'success' => true,
            'data' => $data,
            'message' => $message,
            'status' => $status
        ], $status);
    }
    
    /**
     * Error response
     */
    protected function errorResponse(string $message, int $status = 400, $errors = null)
    {
        return response()->json([
            'success' => false,
            'message' => $message,
            'status' => $status,
            'errors' => $errors
        ], $status);
    }
    
    /**
     * Paginated response
     */
    protected function paginatedResponse($data, $pagination)
    {
        return response()->json([
            'success' => true,
            'data' => $data,
            'pagination' => [
                'total' => $pagination->total(),
                'per_page' => $pagination->perPage(),
                'current_page' => $pagination->currentPage(),
                'last_page' => $pagination->lastPage(),
                'from' => $pagination->firstItem(),
                'to' => $pagination->lastItem()
            ]
        ]);
    }
}
```

## Authentication and Authorization

### JWT Authentication

```php
use Illuminate\Support\Facades\Auth;
use Tymon\JWTAuth\Facades\JWTAuth;

class AuthController extends Controller
{
    public function login(LoginRequest $request)
    {
        $credentials = $request->only('email', 'password');
        
        if (!$token = Auth::attempt($credentials)) {
            return $this->errorResponse('Invalid credentials', 401);
        }
        
        return $this->respondWithToken($token);
    }
    
    protected function respondWithToken($token)
    {
        return response()->json([
            'access_token' => $token,
            'token_type' => 'bearer',
            'expires_in' => auth()->factory()->getTTL() * 60
        ]);
    }
}

// Middleware for API routes
Route::middleware('auth:api')->group(function () {
    Route::apiResource('products', ProductApiController::class);
});
```

### Role-Based Access Control

```php
class ProductApiController extends RestController
{
    public function __construct()
    {
        $this->middleware(['auth:api']);
        $this->middleware('can:view,product')->only(['show']);
        $this->middleware('can:create,App\\Models\\Product')->only(['store']);
        $this->middleware('can:update,product')->only(['update']);
        $this->middleware('can:delete,product')->only(['destroy']);
    }
    
    protected function authorizeAction($action, $model = null)
    {
        $user = auth()->user();
        
        switch ($action) {
            case 'view':
                return $user->can('view', $model) || $user->is_admin;
            case 'create':
                return $user->can('create', Product::class);
            case 'update':
                return $user->can('update', $model) || $user->is_admin;
            case 'delete':
                return $user->can('delete', $model) || $user->is_admin;
            default:
                return false;
        }
    }
}
```

## Validation

### Form Request Validation

```php
class StoreProductRequest extends FormRequest
{
    public function authorize()
    {
        return auth()->check();
    }
    
    public function rules()
    {
        return [
            'name' => ['required', 'string', 'max:255'],
            'price' => ['required', 'numeric', 'min:0'],
            'description' => ['nullable', 'string'],
            'category_id' => ['required', 'exists:categories,id'],
            'image' => ['nullable', 'image', 'max:2048'],
            'status' => ['nullable', 'in:active,inactive']
        ];
    }
    
    public function messages()
    {
        return [
            'name.required' => 'Product name is required',
            'price.min' => 'Price must be greater than 0',
            'category_id.exists' => 'Selected category does not exist'
        ];
    }
}
```

### Inline Validation

```php
public function store(Request $request)
{
    $validated = $request->validate([
        'name' => 'required|string|max:255',
        'price' => 'required|numeric|min:0',
        'category_id' => 'required|exists:categories,id'
    ], [
        'name.required' => 'Product name is required',
        'price.min' => 'Price must be greater than 0'
    ]);
    
    // Process validated data
}
```

## Error Handling

### Global Exception Handler

```php
class ApiExceptionHandler extends ExceptionHandler
{
    protected function registerApiHandlers()
    {
        $this->renderable(function (\Illuminate\Validation\ValidationException $e, $request) {
            return response()->json([
                'success' => false,
                'message' => 'Validation failed',
                'errors' => $e->errors(),
                'status' => 422
            ], 422);
        });
        
        $this->renderable(function (\Illuminate\Auth\AuthenticationException $e, $request) {
            return response()->json([
                'success' => false,
                'message' => 'Unauthenticated',
                'status' => 401
            ], 401);
        });
        
        $this->renderable(function (\Illuminate\Database\Eloquent\ModelNotFoundException $e, $request) {
            return response()->json([
                'success' => false,
                'message' => 'Resource not found',
                'status' => 404
            ], 404);
        });
    }
}
```

### Custom Exception Classes

```php
class ApiException extends \Exception
{
    protected $errors;
    
    public function __construct(string $message, int $code = 400, $errors = null)
    {
        parent::__construct($message, $code);
        $this->errors = $errors;
    }
    
    public function getErrors()
    {
        return $this->errors;
    }
}

// Usage
throw new ApiException('Validation failed', 422, [
    'name' => ['Name is required']
]);
```

## Performance Optimization

### Query Optimization

```php
class ProductApiController extends RestController
{
    protected function listQuery()
    {
        $query = $this->model::query();
        
        // Eager load relationships
        $query->with(['category', 'supplier', 'reviews']);
        
        // Add indexes for common queries
        $query->select([
            'id', 'name', 'price', 'status', 
            'category_id', 'supplier_id', 'created_at', 'updated_at'
        ]);
        
        // Use join for better performance
        if (request()->has('category_name')) {
            $query->join('categories', 'products.category_id', '=', 'categories.id')
                  ->where('categories.name', 'like', '%' . request()->category_name . '%');
        }
        
        return $query;
    }
}
```

### Caching

```php
class ProductApiController extends RestController
{
    protected $cacheTags = ['products'];
    
    public function index()
    {
        $cacheKey = 'products:' . request()->page . ':20';
        
        return Cache::remember($cacheKey, now()->addHours(1), function () {
            return $this->model::paginate(20);
        });
    }
    
    public function show($id)
    {
        return Cache::remember("product:{$id}", now()->addHours(6), function () use ($id) {
            return $this->model::findOrFail($id);
        });
    }
}
```

## Testing API Controllers

### Unit Testing

```php
class ProductApiControllerTest extends TestCase
{
    use RefreshDatabase;
    
    protected $productApiController;
    protected $product;
    
    protected function setUp(): void
    {
        parent::setUp();
        $this->productApiController = new ProductApiController();
        $this->product = Product::factory()->create();
    }
    
    public function test_index_returns_paginated_products()
    {
        // Arrange
        Product::factory(5)->create();
        
        // Act
        $response = $this->actingAs($this->user)
                         ->getJson('/api/products');
        
        // Assert
        $response->assertStatus(200)
                 ->assertJsonStructure([
                     'success',
                     'data' => [['id', 'name', 'price']],
                     'pagination'
                 ]);
    }
    
    public function test_store_creates_new_product()
    {
        // Arrange
        $productData = [
            'name' => 'New Product',
            'price' => 99.99,
            'category_id' => Category::factory()->create()->id
        ];
        
        // Act
        $response = $this->actingAs($this->user)
                         ->postJson('/api/products', $productData);
        
        // Assert
        $response->assertStatus(201)
                 ->assertJsonFragment(['name' => 'New Product']);
        
        $this->assertDatabaseHas('products', ['name' => 'New Product']);
    }
    
    public function test_update_requires_authentication()
    {
        // Arrange
        $updateData = ['name' => 'Updated Name'];
        
        // Act
        $response = $this->putJson("/api/products/{$this->product->id}", $updateData);
        
        // Assert
        $response->assertStatus(401);
    }
}
```

### Feature Testing

```php
class ProductApiTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        
        // Create test data
        $this->category = Category::factory()->create();
        $this->product = Product::factory()->create(['category_id' => $this->category->id]);
        $this->user = User::factory()->create();
        
        // Create authentication token
        $this->token = JWTAuth::fromUser($this->user);
    }
    
    protected function getHeaders()
    {
        return [
            'Authorization' => 'Bearer ' . $this->token,
            'Accept' => 'application/json'
        ];
    }
    
    public function test_can_create_product()
    {
        $productData = [
            'name' => 'Test Product',
            'price' => 49.99,
            'description' => 'A test product',
            'category_id' => $this->category->id
        ];
        
        $response = $this->postJson('/api/products', $productData, $this->getHeaders());
        
        $response->assertStatus(201)
                 ->assertJsonFragment([
                     'name' => 'Test Product',
                     'price' => 49.99
                 ]);
        
        $this->assertDatabaseHas('products', ['name' => 'Test Product']);
    }
    
    public function test_can_update_product()
    {
        $updateData = [
            'name' => 'Updated Product Name',
            'price' => 79.99
        ];
        
        $response = $this->putJson("/api/products/{$this->product->id}", $updateData, $this->getHeaders());
        
        $response->assertStatus(200)
                 ->assertJsonFragment(['name' => 'Updated Product Name']);
        
        $this->assertDatabaseHas('products', ['name' => 'Updated Product Name', 'price' => 79.99]);
    }
}
```

## Advanced Patterns

### API Versioning

```php
// Version 1 API
Route::group(['prefix' => 'api/v1'], function () {
    Route::apiResource('products', V1\ProductController::class);
});

// Version 2 API
Route::group(['prefix' => 'api/v2'], function () {
    Route::apiResource('products', V2\ProductController::class);
});
```

### Rate Limiting

```php
// In RouteServiceProvider
Route::middleware(['auth:api', 'throttle:60,1'])->group(function () {
    Route::apiResource('products', ProductApiController::class);
});

// Custom rate limiting
Route::middleware(['auth:api', 'throttle:api'])->group(function () {
    Route::get('/products/export', [ProductApiController::class, 'export']);
});
```

### API Documentation

Use OpenAPI/Swagger for API documentation:

```php
/**
 * @OA\Info(
 *     title="QSMCF API",
 *     version="1.0.0",
 *     description="QSMCF Management API"
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
 *         @OA\JsonContent(type="array", @OA\Items(ref="#/components/schemas/Product"))
 *     )
 * )
 */
public function index()
{
    return $this->model::paginate(20);
}
```

## Best Practices

1. **Always use type hints** - Be explicit about parameter and return types
2. **Follow REST conventions** - Use proper HTTP methods and status codes
3. **Implement proper authentication** - Use JWT or OAuth for API endpoints
4. **Validate all input** - Use FormRequest classes for validation
5. **Handle errors gracefully** - Return consistent error response format
6. **Use proper HTTP status codes** - 200, 201, 400, 401, 403, 404, 500
7. **Implement rate limiting** - Protect your API from abuse
8. **Document your API** - Use OpenAPI/Swagger for documentation
9. **Cache responses** - For read-heavy operations
10. **Use transactions** - For multi-step operations
